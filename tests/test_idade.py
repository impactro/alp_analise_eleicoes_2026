"""Regras de recorte de H13; executar unittest a partir da raiz do projeto."""

import unittest

from scripts.conferir_idade import AGES, IBGE_AGES, aggregate_rows, census_totals, compare, select_members


class AgeTests(unittest.TestCase):
    def test_national_prevents_double_counting(self):
        self.assertEqual(select_members(["p_BRASIL.csv", "p_SP.csv"], "p"), ["p_BRASIL.csv"])
        with self.assertRaises(ValueError):
            select_members(["p_SP.csv"], "p")
        with self.assertRaises(ValueError):
            select_members(["p_BRASIL.csv", "p_BRASIL.csv"], "p")

    def test_attendance_turn_and_exterior_are_separate(self):
        headers = ["ANO_ELEICAO", "NR_TURNO", "SG_UF", "CD_FAIXA_ETARIA", "DS_FAIXA_ETARIA", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO", "DT_GERACAO", "HH_GERACAO"]
        rows = [["2026", "1", uf, "9999", AGES["9999"], "100", "2", "98", "13/10/2026", "16:46:32"] for uf in ("SP", "ZZ")]
        part = aggregate_rows(rows, headers, "attendance")
        self.assertEqual(part["sums"][("1", "9999", "brasil_sem_exterior")], [100, 2, 98])
        self.assertEqual(set(part["rowCountsByTurn"]), {"1"})
        rows[0][6] = "3"
        with self.assertRaises(ValueError):
            aggregate_rows(rows, headers, "attendance")

    def test_age_label_and_year_guard(self):
        headers = ["AA_ELEICAO", "SG_UF", "CD_FAIXA_ETARIA", "DS_FAIXA_ETARIA", "QT_ELEITORES", "QT_ELEITORES_BIOMETRIA", "DT_GERACAO", "HH_GERACAO"]
        row = ["2026", "SP", "9999", "95 a 99 anos", "100", "3", "14/07/2026", "18:03:33"]
        with self.assertRaises(ValueError):
            aggregate_rows([row], headers, "electorate")
        row[3], row[0] = AGES["9999"], "2022"
        with self.assertRaises(ValueError):
            aggregate_rows([row], headers, "electorate")

    def census_fixture(self):
        results = []
        for age, label in IBGE_AGES.items():
            results.append({"classificacoes": [{"id": "2", "categoria": {"6794": "Total"}}, {"id": "286", "categoria": {"113635": "Total"}}, {"id": "287", "categoria": {age: label}}],
                            "series": [{"localidade": {"id": "1", "nivel": {"id": "N1"}}, "serie": {"2022": "10"}}]})
        return [{"id": "93", "unidade": "Pessoas", "resultados": results}]

    def test_census_requires_complete_unduplicated_categories(self):
        fixture = self.census_fixture()
        self.assertEqual(census_totals(fixture)["population96plus"], 50)
        self.assertEqual(census_totals(fixture)["population100plus"], 10)
        fixture[0]["resultados"].append(fixture[0]["resultados"][0])
        with self.assertRaises(ValueError):
            census_totals(fixture)

    def test_census_missing_suppressed_or_wrong_geography_fails(self):
        fixture = self.census_fixture()
        fixture[0]["resultados"].pop()
        with self.assertRaises(ValueError):
            census_totals(fixture)
        fixture = self.census_fixture()
        fixture[0]["resultados"][0]["series"][0]["serie"]["2022"] = "-"
        with self.assertRaises(ValueError):
            census_totals(fixture)
        fixture = self.census_fixture()
        fixture[0]["resultados"][0]["series"][0]["localidade"]["nivel"]["id"] = "N3"
        with self.assertRaises(ValueError):
            census_totals(fixture)

    def test_rates_do_not_invent_second_turn(self):
        electorate = {"sums": {("cadastro", "9999", "brasil_sem_exterior"): [297977, 10000]}}
        attendance = {"sums": {("1", "9999", "brasil_sem_exterior"): [297977, 2141, 295836]}, "rowCountsByTurn": {"1": 1}}
        result = compare(electorate, attendance, {"population96plus": 149424, "population100plus": 37814})
        self.assertEqual(result["differenceElectorate100plusMinusCensus96plus"], 148553)
        self.assertEqual(result["availableAttendanceTurns"], ["1"])
        self.assertNotIn("2", result["attendanceByAge"][AGES["9999"]]["byTurn"])
        self.assertEqual(round(result["attendanceByAge"][AGES["9999"]]["byTurn"]["1"]["attendancePct"], 2), 0.72)


if __name__ == "__main__":
    unittest.main()
