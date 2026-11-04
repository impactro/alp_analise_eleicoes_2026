"""Fixtures sintéticas: não são dados eleitorais nem saem nos resultados."""

import csv
import io
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from conferir_totais import MEMBER, REQUIRED, check_archive, summarize


def row(cid="1", votes=10, uf="SP", turn="2", valid=None):
    return {"DT_GERACAO": "03/11/2026", "HH_GERACAO": "19:31:38", "ANO_ELEICAO": "2026",
            "CD_TIPO_ELEICAO": "2", "CD_CARGO": "1", "NR_TURNO": turn, "SG_UF": uf,
            "CD_MUNICIPIO": "71072", "NR_ZONA": "1", "SQ_CANDIDATO": cid,
            "NM_URNA_CANDIDATO": f"SINTETICO {cid}", "QT_VOTOS_NOMINAIS": str(votes),
            "QT_VOTOS_NOMINAIS_VALIDOS": str(votes if valid is None else valid),
            "NM_TIPO_DESTINACAO_VOTOS": "Válido"}


class TotalsTest(unittest.TestCase):
    def test_exterior_valid_votes_and_missing_turn(self):
        report = summarize([row(votes=10, valid=9), row(votes=2, uf="ZZ"), row(cid="2", votes=8)])
        self.assertEqual(report["turnsObserved"], [2])
        turn = report["turns"][0]
        self.assertEqual(turn["validTotal"], 19)
        self.assertEqual(turn["topTwoValidDifference"], 3)
        self.assertEqual(turn["candidates"][0]["scopes"]["exterior"]["valid"], 2)

    def test_duplicate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicada"):
            summarize([row(), row()])

    def test_invalid_count_and_generation_are_rejected(self):
        with self.assertRaises(ValueError):
            summarize([row(votes=10, valid=11)])
        other = row(cid="2")
        other["HH_GERACAO"] = "19:32:00"
        with self.assertRaisesRegex(ValueError, "misturadas"):
            summarize([row(), other])

    def test_br_is_read_once_without_brasil_or_uf(self):
        content = io.StringIO()
        writer = csv.DictWriter(content, fieldnames=sorted(REQUIRED), delimiter=";")
        writer.writeheader(); writer.writerows([row(), row(cid="2", votes=7)])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr(MEMBER, content.getvalue().encode("latin1"))
                archive.writestr(MEMBER.replace("_BR.csv", "_BRASIL.csv"), content.getvalue().encode("latin1"))
                archive.writestr(MEMBER.replace("_BR.csv", "_SP.csv"), content.getvalue().encode("latin1"))
            self.assertEqual(check_archive(path)["turns"][0]["validTotal"], 17)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                check_archive(path, "0" * 64)


if __name__ == "__main__":
    unittest.main()
