import unittest
import csv
import io
import tempfile
from pathlib import Path
from zipfile import ZipFile
from scripts.conferir_secoes import summarize, check_archives, SOURCES


def detail(section, nominal=10, blank=1, nulls=2):
    return dict(ANO_ELEICAO="2026", CD_TIPO_ELEICAO="2", CD_CARGO="1", NR_TURNO="2", SG_UF="AC",
                CD_MUNICIPIO="1", NR_ZONA="1", NR_SECAO=str(section), ST_SECAO_INSTALADA="Sim",
                ST_SECAO_ANULADA="Não", QT_VOTOS_NOMINAIS=str(nominal), QT_VOTOS_BRANCOS=str(blank),
                QT_VOTOS_NULOS=str(nulls), QT_COMPARECIMENTO=str(nominal+blank+nulls), QT_APTOS="100")


def vote(section, candidate, amount):
    return dict(detail(section), NR_VOTAVEL=str(candidate), QT_VOTOS=str(amount))


class SectionsTest(unittest.TestCase):
    def test_missing_candidate_is_zero_only_after_reconciliation(self):
        rows = [vote(1,13,10), vote(1,95,1), vote(1,96,2), vote(2,13,5), vote(2,22,5)]
        r = summarize([detail(1),detail(2,blank=0,nulls=0)],rows)
        self.assertEqual((r["eligibleSections"],r["zeroFlavioSections"],r["lulaVotesInZeroSections"],r["attendanceInZeroSections"]),(2,1,10,13))

    def test_missing_section_votes_cannot_be_inferred_as_zero(self):
        with self.assertRaisesRegex(ValueError,"incompleta"):
            summarize([detail(1)],[])

    def test_duplicate_votes_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicada"):
            summarize([detail(1)],[vote(1,13,10),vote(1,13,10)])

    def test_counts_must_reconcile(self):
        bad=detail(1); bad["QT_COMPARECIMENTO"]="99"
        with self.assertRaisesRegex(ValueError,"não reconcilia"):
            summarize([bad],[])

    def test_foreign_sections_excluded(self):
        foreign=detail(2); foreign["SG_UF"]="ZZ"
        r=summarize([detail(1,blank=0,nulls=0),foreign],[vote(1,13,10)])
        self.assertEqual(r["eligibleSections"],1)

    def test_zero_blank_and_null_count(self):
        r=summarize([detail(1,blank=0,nulls=0)],[vote(1,13,10)])
        self.assertEqual(r["zeroBlankAndNullSections"],1)

    def test_duplicate_detail_rejected(self):
        with self.assertRaisesRegex(ValueError,"Detalhe duplicado"):
            summarize([detail(1),detail(1)],[])

    def test_archives_and_hash_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            paths={}
            for kind,rows in (("detail",[detail(1,blank=0,nulls=0)]),("votes",[vote(1,13,10)])):
                for row in rows:
                    row.update(DT_GERACAO="26/10/2026",HH_GERACAO="12:00:00")
                text=io.StringIO(); w=csv.DictWriter(text,fieldnames=rows[0],delimiter=";"); w.writeheader(); w.writerows(rows)
                paths[kind]=Path(directory)/(kind+".zip")
                with ZipFile(paths[kind],"w") as z:
                    z.writestr(SOURCES[kind][0],text.getvalue().encode("latin1"))
            result=check_archives(paths["detail"],paths["votes"])
            self.assertEqual(result["zeroFlavioSections"],1)
            self.assertEqual(len(result["sources"]["detail"]["sha256"]),64)
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                check_archives(paths["detail"],paths["votes"],detail_sha256="0"*64)


if __name__ == "__main__":
    unittest.main()
