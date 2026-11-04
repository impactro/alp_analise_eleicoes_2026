"""Controle independente do CSV presidencial oficial; apenas biblioteca padrão."""

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

SOURCE = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip"
MEMBER = "votacao_candidato_munzona_2026_BR.csv"
REQUIRED = {
    "DT_GERACAO", "HH_GERACAO", "ANO_ELEICAO", "CD_TIPO_ELEICAO",
    "CD_CARGO", "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA",
    "SQ_CANDIDATO", "NM_URNA_CANDIDATO", "QT_VOTOS_NOMINAIS",
    "QT_VOTOS_NOMINAIS_VALIDOS", "NM_TIPO_DESTINACAO_VOTOS",
}
UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())


def summarize(rows):
    """Agrega votos de eleição ordinária presidencial, sem inferir zero ausente."""
    totals = defaultdict(lambda: {"raw": 0, "valid": 0})
    names, generations, keys, territories = {}, set(), set(), defaultdict(set)
    count = 0
    for row in rows:
        if row["ANO_ELEICAO"] != "2026":
            raise ValueError("Ano inesperado no arquivo de 2026")
        if row["CD_CARGO"] != "1" or row["CD_TIPO_ELEICAO"] != "2":
            continue
        turn, cid, uf = int(row["NR_TURNO"]), row["SQ_CANDIDATO"], row["SG_UF"]
        raw, valid = int(row["QT_VOTOS_NOMINAIS"]), int(row["QT_VOTOS_NOMINAIS_VALIDOS"])
        if turn not in (1, 2) or uf not in UFS | {"ZZ"} or not cid.isdigit() or not 0 <= valid <= raw:
            raise ValueError("Turno, UF, candidato ou contagem inválida")
        name = row["NM_URNA_CANDIDATO"]
        if cid in names and names[cid] != name:
            raise ValueError("Nome conflitante para a mesma candidatura")
        names[cid] = name
        # Destinações diferentes podem ser linhas legítimas do mesmo candidato.
        key = (turn, cid, uf, row["CD_MUNICIPIO"], row["NR_ZONA"], row["NM_TIPO_DESTINACAO_VOTOS"])
        if key in keys:
            raise ValueError("Linha duplicada na chave de município/zona/destinação")
        keys.add(key)
        generations.add((row["DT_GERACAO"], row["HH_GERACAO"]))
        if len(generations) != 1:
            raise ValueError("Gerações misturadas no mesmo CSV")
        scope = "exterior" if uf == "ZZ" else "brasil"
        totals[turn, cid, scope]["raw"] += raw
        totals[turn, cid, scope]["valid"] += valid
        territories[turn, scope].add((uf, row["CD_MUNICIPIO"]))
        count += 1
    if not count:
        raise ValueError("Nenhuma linha presidencial ordinária encontrada")
    result = []
    turns = sorted({t for t, _, _ in totals})
    for turn in turns:
        candidates = []
        for cid in sorted({c for t, c, _ in totals if t == turn}):
            scopes = {scope: totals[turn, cid, scope] for scope in ("brasil", "exterior") if (turn, cid, scope) in totals}
            candidates.append({"id": cid, "name": names[cid], "scopes": scopes,
                               "raw": sum(x["raw"] for x in scopes.values()),
                               "valid": sum(x["valid"] for x in scopes.values())})
        candidates.sort(key=lambda x: (-x["valid"], x["id"]))
        denominator = sum(c["valid"] for c in candidates)
        for c in candidates:
            c["shareValidPercent"] = str((Decimal(c["valid"]) * 100 / denominator).quantize(Decimal("0.0001"))) if denominator else None
        result.append({"turn": turn, "candidates": candidates,
                       "validTotal": denominator,
                       "topTwoValidDifference": candidates[0]["valid"] - candidates[1]["valid"] if len(candidates) >= 2 else None,
                       "observedTerritories": {s: len(territories[turn, s]) for s in ("brasil", "exterior")}})
    day, hour = next(iter(generations))
    return {"schema": "alp.national-control.v1", "status": "recomputed_from_official_archive",
            "generatedAtSource": f"{day} {hour}", "inputRows": count,
            "turnsObserved": turns, "turns": result,
            "limits": ["Totais nominais; não mede comparecimento, abstenção, brancos ou nulos.",
                       "Territórios observados não certificam completude da fonte.",
                       "Não identifica eleitores nem certifica integridade das urnas."]}


def check_archive(path, expected_sha256=None):
    with Path(path).open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise ValueError("SHA-256 divergente; não comparar edições diferentes silenciosamente")
    with ZipFile(path) as archive:
        if archive.namelist().count(MEMBER) != 1:
            raise ValueError("Membro nacional _BR.csv ausente ou duplicado")
        with archive.open(MEMBER) as binary:
            reader = csv.DictReader(io.TextIOWrapper(binary, encoding="latin1", newline=""), delimiter=";")
            if len(reader.fieldnames or []) != len(set(reader.fieldnames or [])) or not REQUIRED.issubset(reader.fieldnames or []):
                raise ValueError("Schema oficial incompatível")
            result = summarize(reader)
    result["source"] = {"url": SOURCE, "sha256": digest, "archiveBytes": Path(path).stat().st_size, "member": MEMBER}
    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True, help="ZIP oficial local; não é extraído")
    parser.add_argument("--sha256", help="Digest da edição desejada")
    args = parser.parse_args()
    print(json.dumps(check_archive(args.zip, args.sha256), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
