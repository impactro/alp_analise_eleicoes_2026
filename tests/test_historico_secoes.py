import csv
import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.conferir_historico_secoes import aggregate_votes, check_details, count_scope, first_turn, rows, section_distribution, municipal_key


def vote(section, candidate, amount, year=2022, uf="AC", turn=2):
    return dict(ANO_ELEICAO=str(year), CD_TIPO_ELEICAO="2", CD_CARGO="1", NR_TURNO=str(turn),
                SG_UF=uf, CD_MUNICIPIO="1", NR_ZONA="1", NR_SECAO=str(section),
                NR_VOTAVEL=str(candidate), QT_VOTOS=str(amount), NM_LOCAL_VOTACAO="ESCOLA")


def detail(section, nominal=10, installed="Sim", annulled="Não"):
    return dict(vote(section, 13, nominal), ST_SECAO_INSTALADA=installed, ST_SECAO_ANULADA=annulled,
                QT_VOTOS_NOMINAIS=str(nominal), QT_VOTOS_BRANCOS="0", QT_VOTOS_NULOS="0",
                QT_COMPARECIMENTO=str(nominal), QT_APTOS="100")


class HistoricalSectionsTest(unittest.TestCase):
    def test_zero_requires_positive_opponent_and_foreign_is_explicit(self):
        source = [vote(1, 13, 10), vote(2, 95, 3), vote(3, 13, 7, uf="ZZ"), vote(4, 22, 1)]
        sections = aggregate_votes(source, 2022)
        self.assertEqual(count_scope(sections)["zeroTargetSections"], 1)
        self.assertEqual(count_scope(sections, include_foreign=True)["zeroTargetSections"], 2)
        self.assertEqual(count_scope(sections)["zeroOpponentSections"], 1)

    def test_historical_candidate_number_and_turn_filters(self):
        source = [vote(1, 13, 10, 2018), vote(2, 17, 3, 2018), vote(3, 13, 9, 2018, turn=1),
                  vote(4, 13, 9, 2022)]
        self.assertEqual(count_scope(aggregate_votes(source, 2018))["sectionsWithPositiveNominalVotes"], 2)

    def test_duplicates_cannot_silently_double_totals(self):
        with self.assertRaisesRegex(ValueError, "duplicada"):
            aggregate_votes([vote(1, 13, 10)] * 2, 2022)

    def test_status_filter_and_positive_vote_reconciliation(self):
        sections = aggregate_votes([vote(1, 13, 10), vote(2, 13, 10), vote(3, 13, 10)], 2022)
        allowed, zero, report = check_details([detail(1), detail(2, installed="Não"), detail(3, annulled="Sim")], sections, 2022)
        self.assertEqual(count_scope(sections, allowed)["zeroTargetSections"], 1)
        self.assertEqual(len(zero), 1)
        self.assertEqual(report["excludedByStatus"], {"notInstalled": 1, "annulled": 1, "zeroNominal": 0})
        with self.assertRaisesRegex(ValueError, "divergente"):
            check_details([detail(1, nominal=9)], {next(iter(sections)): sections[next(iter(sections))]}, 2022)

    def test_absent_voting_section_is_not_zero(self):
        with self.assertRaisesRegex(ValueError, "ausente"):
            check_details([detail(1)], {}, 2022)

    def test_unknown_status_is_not_misread_as_not_installed(self):
        sections = aggregate_votes([vote(1, 13, 10)], 2022)
        allowed, _, report = check_details([detail(1, installed="#NULO#", annulled="#NULO#")], sections, 2022)
        self.assertEqual(len(allowed), 0)
        self.assertEqual(report["unknownStatusSections"], 1)
        self.assertEqual(report["excludedByStatus"]["notInstalled"], 0)

    def test_population_join_preserves_missing_and_uses_explicit_alias(self):
        source = [vote(1, 13, 10)]
        source[0]["SG_UF"] = "GO"
        sections = aggregate_votes(source, 2022)
        d = detail(1); d.update(SG_UF="GO", NM_MUNICIPIO="BOM JESUS")
        _, _, report = check_details([d], sections, 2022, {("GO", "BOMJESUSDEGOIAS"): 9})
        r = report["attendanceAboveCensus2022"]
        self.assertEqual((r["matchedByUFAndNormalizedName"], r["municipalitiesAbovePopulation"]), (1, 1))
        _, _, report = check_details([d], sections, 2022, {})
        r = report["attendanceAboveCensus2022"]
        self.assertEqual((r["matchedByUFAndNormalizedName"], r["municipalitiesAbovePopulation"]), (0, 0))
        self.assertEqual(len(r["unmatchedMunicipalities"]), 1)
        self.assertEqual(municipal_key("BA", "CAMAÇÃ", aliases=True), ("BA", "CAMACAN"))
        self.assertEqual(municipal_key("PA", "SANTA ISABEL DO PARÁ", aliases=True), ("PA", "SANTAIZABELDOPARA"))

    def test_first_turn_missing_section_not_filled_zero(self):
        zero_keys = {("AC", "1", 1, n) for n in (1, 2, 3, 4, 5)}
        source = [vote(1, 13, 10, 2026, turn=1), vote(2, 22, 5, 2026, turn=1),
                  vote(3, 22, 6, 2026, turn=1), vote(5, 95, 2, 2026, turn=1)]
        result = first_turn(source, zero_keys)
        self.assertEqual((result["matchedSections"], result["zeroFlavioSections"],
                          result["atMostFiveFlavioSections"], result["missingOrEmptySections"]), (3, 1, 2, 2))

    def test_strict_saturation_and_repeated_groups_are_not_sections(self):
        keys = [("AC", "1", 1, n) for n in range(1, 6)]
        sections = {keys[0]: [9, 1, 0, 0], keys[1]: [9, 1, 0, 0], keys[2]: [9, 1, 0, 0],
                    keys[3]: [9, 1, 1, 0], keys[4]: [10, 0, 0, 0]}
        result = section_distribution(sections, set(keys))
        self.assertEqual(result["H04"]["lulaAbove90Percent"], 1)
        self.assertEqual(result["H08"]["repeatedNominalScoreGroups"], 1)
        self.assertEqual(result["H08"]["sectionsInRepeatedNominalScoreGroups"], 4)
        self.assertEqual(result["H08"]["repeatedFourOptionScoreGroups"], 1)
        self.assertEqual(result["H08"]["sectionsInRepeatedFourOptionScoreGroups"], 3)

    def test_archive_reads_only_one_national_member_and_checks_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "votes.zip"
            row = dict(vote(1, 13, 10), DT_GERACAO="01/11/2022", HH_GERACAO="16:05:25")
            text = io.StringIO()
            writer = csv.DictWriter(text, fieldnames=row, delimiter=";")
            writer.writeheader(); writer.writerow(row)
            with ZipFile(path, "w") as z:
                for member in ("votacao_secao_2022_BR.csv", "votacao_secao_2022_BRASIL.csv", "votacao_secao_2022_AC.csv"):
                    z.writestr(member, text.getvalue().encode("latin1"))
            provenance = {}
            self.assertEqual(len(list(rows(path, 2022, "votes", provenance))), 1)
            self.assertEqual(provenance["votes2022"]["member"], "votacao_secao_2022_BR.csv")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                list(rows(path, 2022, "votes", {}, "0" * 64))


if __name__ == "__main__":
    unittest.main()
