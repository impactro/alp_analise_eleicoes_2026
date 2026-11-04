"""Recalcula H07 diretamente dos ZIPs públicos TSE, sem banco ou dependências."""

import argparse
import csv
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())
SOURCES = {
    "detail": ("detalhe_votacao_secao_2026_BR.csv", "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip"),
    "votes": ("votacao_secao_2026_BR.csv", "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip"),
}
REQUIRED_COMMON = {"DT_GERACAO", "HH_GERACAO", "ANO_ELEICAO", "CD_TIPO_ELEICAO", "CD_CARGO",
                   "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"}
REQUIRED = {
    "detail": REQUIRED_COMMON | {"ST_SECAO_INSTALADA", "ST_SECAO_ANULADA", "QT_VOTOS_NOMINAIS",
                                "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS", "QT_COMPARECIMENTO", "QT_APTOS"},
    "votes": REQUIRED_COMMON | {"NR_VOTAVEL", "QT_VOTOS"},
}


def key(row):
    return (row["SG_UF"], row["CD_MUNICIPIO"], int(row["NR_ZONA"]), int(row["NR_SECAO"]))


def presidential(row, turn=2):
    return (row["ANO_ELEICAO"] == "2026" and row["CD_TIPO_ELEICAO"] == "2"
            and row["CD_CARGO"] == "1" and int(row["NR_TURNO"]) == turn
            and row["SG_UF"] in UFS)


def summarize(details, votes):
    """Zero requer seção elegível e reconciliação, não só ausência de uma linha."""
    sections = {}
    for row in details:
        if not presidential(row):
            continue
        if row["ST_SECAO_INSTALADA"].lower() != "sim" or not row["ST_SECAO_ANULADA"].lower().startswith("n"):
            continue
        nums = [int(row[k]) for k in ("QT_VOTOS_NOMINAIS", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS", "QT_COMPARECIMENTO", "QT_APTOS")]
        if min(nums) < 0 or sum(nums[:3]) != nums[3] or nums[3] > nums[4]:
            raise ValueError("Detalhe não reconcilia comparecimento/votos/aptos")
        if nums[0] == 0:
            continue
        k = key(row)
        if k in sections:
            raise ValueError("Detalhe duplicado na chave UF/município/zona/seção")
        # nominal, branco, nulo, comparecimento, aptos, Lula, Flávio, máscara
        sections[k] = nums + [0, 0, 0]
    if not sections:
        raise ValueError("Universo elegível vazio")
    for row in votes:
        if not presidential(row):
            continue
        k = key(row)
        if k not in sections:
            continue
        number, amount = int(row["NR_VOTAVEL"]), int(row["QT_VOTOS"])
        if amount < 0 or number not in (13, 22, 95, 96):
            raise ValueError("Contagem negativa ou opção presidencial inesperada no segundo turno")
        target, bit = {13: (5, 1), 22: (6, 2), 95: (1, 4), 96: (2, 8)}[number]
        s = sections[k]
        if s[7] & bit:
            raise ValueError("Votação duplicada na chave da seção/opção")
        s[7] |= bit
        if number in (13, 22):
            s[target] = amount
        elif s[target] != amount:
            raise ValueError("Branco/nulo divergente entre votação e detalhe")
    zero = []
    for k, s in sections.items():
        if s[5] + s[6] != s[0]:
            raise ValueError("Votação nominal incompleta ou divergente do detalhe")
        if (s[1] and not s[7] & 4) or (s[2] and not s[7] & 8):
            raise ValueError("Branco/nulo ausente no arquivo de votação")
        if s[6] == 0:
            zero.append((k, s))
    return {"schema": "alp.zero-sections.v1", "claim": "H07", "status": "recomputed_from_official_archives",
            "scope": "Brasil sem exterior, presidente, segundo turno, seções instaladas, não anuladas, nominal positivo",
            "eligibleSections": len(sections), "nominalVotesReconciled": sum(s[0] for s in sections.values()),
            "zeroFlavioSections": len(zero), "lulaVotesInZeroSections": sum(s[5] for _, s in zero),
            "zeroBlankAndNullSections": sum(s[1] == s[2] == 0 for _, s in zero),
            "attendanceInZeroSections": sum(s[3] for _, s in zero),
            "zeroSectionsByUF": {uf: sum(k[0] == uf for k, _ in zero) for uf in sorted({k[0] for k, _ in zero})},
            "limits": ["Reprodução de agregados; não identifica eleitores nem demonstra integridade ou fraude.",
                       "Comparações históricas de 2018/2022 não foram executadas nesta rodada."]}


def archive_rows(path, kind, provenance, expected=None):
    member, url = SOURCES[kind]
    with Path(path).open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    if expected and digest != expected.lower():
        raise ValueError("SHA-256 divergente: " + kind)
    generations = set()
    with ZipFile(path) as z:
        if z.namelist().count(member) != 1:
            raise ValueError("Membro nacional ausente ou duplicado: " + kind)
        with z.open(member) as binary:
            reader = csv.DictReader(io.TextIOWrapper(binary, encoding="latin1", newline=""), delimiter=";")
            if (len(reader.fieldnames or []) != len(set(reader.fieldnames or []))
                    or not REQUIRED[kind].issubset(reader.fieldnames or [])):
                raise ValueError("Schema oficial incompatível ou coluna duplicada")
            for row in reader:
                generations.add(row["DT_GERACAO"] + " " + row["HH_GERACAO"])
                if len(generations) != 1:
                    raise ValueError("Gerações misturadas")
                yield row
    provenance[kind] = {"url": url, "member": member, "sha256": digest,
                        "archiveBytes": Path(path).stat().st_size,
                        "generatedAtSource": next(iter(generations)), "timestampTimeZone": None}


def check_archives(detail, votes, detail_sha256=None, votes_sha256=None):
    start, provenance, started = time.perf_counter(), {}, datetime.now(timezone.utc).isoformat()
    result = summarize(archive_rows(detail, "detail", provenance, detail_sha256),
                       archive_rows(votes, "votes", provenance, votes_sha256))
    result["sources"] = provenance
    result["execution"] = {"startedAt": started, "finishedAt": datetime.now(timezone.utc).isoformat(),
                           "elapsedSeconds": round(time.perf_counter() - start, 3), "officialTokens": None,
                           "engine": "Python stdlib csv/zipfile", "device": "CPU", "fallback": None}
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--detail-zip", type=Path, required=True)
    p.add_argument("--votes-zip", type=Path, required=True)
    p.add_argument("--detail-sha256")
    p.add_argument("--votes-sha256")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = check_archives(args.detail_zip, args.votes_zip, args.detail_sha256, args.votes_sha256)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
