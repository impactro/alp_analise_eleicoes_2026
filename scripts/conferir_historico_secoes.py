"""Reproduz H07 em ZIPs oficiais, sem código do autor ou pacotes externos."""

import argparse
import csv
import hashlib
import io
import json
import re
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

from scripts.conferir_secoes import UFS, key

TERMS = r"INDIGENA|ALDEIA|INDIG|TERRA INDIGENA|QUILOMB|KM |MALOCA|COMUNIDADE|POLO BASE|POSTO DE SAUDE|SESAI"
COMMON = {"DT_GERACAO", "HH_GERACAO", "ANO_ELEICAO", "CD_TIPO_ELEICAO", "CD_CARGO",
          "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"}
PINS = {2018: "dde2250058a7efa3b7ee336520556905456cb75d7debf99ea4badfc4d598a48c",
        2022: "9353993de5cf03778aef44e01d4925e7ee105f5262491d344a2f0dbc956b0139",
        2026: "c928321f63f2d095706fca73d4607c048d2ada23bda6876455d6911aaf1bc9c1"}
DETAIL_PIN = "8ef9ce3a85cde260471faf7a83a9b4f5ccf3993fdda942aacaa658574344789c"
DETAIL_PINS = {2018: "de35b08db427ee0c3089d88317e6166ea5dea33630f5b1dabdccf3304de48f70",
               2022: "ad22c50b9e6d9dfb096a2170680a190f1734895ba89d8977b95fd63ca02c03da", 2026: DETAIL_PIN}
HISTORICAL_NAME_ALIASES = {("BA", "CAMACA"): (34118, "CAMACAN"),
                           ("PA", "SANTA ISABEL DO PARA"): (5290, "SANTA IZABEL DO PARA")}


def normalized(value):
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()


def municipal_key(uf, name, aliases=False):
    # Mesma correspondência explícita da análise municipal do projeto; sem fuzzy.
    from scripts.conferir_municipios import NAME_ALIASES, name_key
    canonical = NAME_ALIASES.get((uf, normalized(name)), name) if aliases else name
    if aliases and (uf, normalized(name)) in HISTORICAL_NAME_ALIASES:
        canonical = HISTORICAL_NAME_ALIASES[uf, normalized(name)][1]
    return uf, name_key(canonical)


def selected(row, year, turn=2):
    return (row["ANO_ELEICAO"] == str(year) and row["CD_TIPO_ELEICAO"] == "2"
            and row["CD_CARGO"] == "1" and int(row["NR_TURNO"]) == turn
            and row["SG_UF"] in UFS | {"ZZ"})


def rows(path, year, kind, provenance, expected=None):
    """Lê exclusivamente _BR.csv; nunca soma BRASIL nem os membros por UF."""
    prefix = "votacao_secao" if kind == "votes" else "detalhe_votacao_secao"
    member = f"{prefix}_{year}_BR.csv"
    with Path(path).open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    if expected and digest != expected:
        raise ValueError("SHA-256 divergente")
    generations = set()
    with ZipFile(path) as z:
        if z.namelist().count(member) != 1:
            raise ValueError("Membro nacional ausente ou duplicado")
        with z.open(member) as stream:
            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="latin1", newline=""), delimiter=";")
            required = COMMON | ({"NR_VOTAVEL", "QT_VOTOS", "NM_LOCAL_VOTACAO"} if kind == "votes" else
                                {"ST_SECAO_INSTALADA", "ST_SECAO_ANULADA", "QT_VOTOS_NOMINAIS",
                                 "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS", "QT_COMPARECIMENTO", "QT_APTOS"})
            if not required.issubset(reader.fieldnames or []) or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("Schema incompatível ou colunas duplicadas")
            for row in reader:
                generations.add(row["DT_GERACAO"] + " " + row["HH_GERACAO"])
                if len(generations) != 1:
                    raise ValueError("Edições misturadas no membro nacional")
                yield row
    archive_name = f"{prefix}_{year}_BR.zip" if kind == "votes" else f"{prefix}_{year}.zip"
    provenance[f"{kind}{year}"] = {
        "url": f"https://cdn.tse.jus.br/estatistica/sead/odsele/{prefix}/{archive_name}",
        "sha256": digest, "archiveBytes": Path(path).stat().st_size, "member": member,
        "generatedAtSource": next(iter(generations)), "timestampTimeZone": None}


def aggregate_votes(source_rows, year):
    """Ausência de opção vale zero apenas dentro de seção com votos nominais."""
    sections = {}
    opponent = 13  # Haddad em 2018; Lula nos outros anos.
    target = 17 if year == 2018 else 22
    options = {opponent: 0, target: 1, 95: 2, 96: 3}
    for row in source_rows:
        if not selected(row, year):
            continue
        k = key(row)
        number, count = int(row["NR_VOTAVEL"]), int(row["QT_VOTOS"])
        if number not in options or count < 0:
            raise ValueError("Opção inesperada ou contagem negativa")
        s = sections.setdefault(k, [0, 0, 0, 0, 0, row["NM_LOCAL_VOTACAO"]])
        index = options[number]
        if s[4] & (1 << index):
            raise ValueError("Votação duplicada na chave seção/opção")
        s[index] = count
        s[4] |= 1 << index
    if not sections:
        raise ValueError("Universo de votação vazio")
    return sections


def count_scope(sections, allowed=None, include_foreign=False):
    selected_sections = {k: s for k, s in sections.items()
                         if (include_foreign or k[0] != "ZZ") and (allowed is None or k in allowed)
                         and s[0] + s[1] > 0}
    zero = {k: s for k, s in selected_sections.items() if s[1] == 0 and s[0] > 0}
    return {"sectionsWithPositiveNominalVotes": len(selected_sections), "zeroTargetSections": len(zero),
            "opponentVotesInZeroSections": sum(s[0] for s in zero.values()),
            "zeroOpponentSections": sum(s[0] == 0 and s[1] > 0 for s in selected_sections.values())}


def check_details(source_rows, sections, year, population=None):
    allowed, seen, zero = set(), set(), {}
    excluded = {"notInstalled": 0, "annulled": 0, "zeroNominal": 0}
    unknown_status = 0
    municipal_attendance = {}
    municipality_codes, aliases_used = {}, set()
    for row in source_rows:
        if not selected(row, year):
            continue
        k = key(row)
        if k in seen:
            raise ValueError("Detalhe duplicado")
        seen.add(k)
        installed, annulled = normalized(row["ST_SECAO_INSTALADA"]), normalized(row["ST_SECAO_ANULADA"])
        if installed == "NAO":
            excluded["notInstalled"] += 1
            continue
        if annulled == "SIM":
            excluded["annulled"] += 1
            continue
        status_known = installed == "SIM" and annulled == "NAO"
        unknown_status += not status_known
        nominal, blank, nulls, attendance, apt = (int(row[c]) for c in
            ("QT_VOTOS_NOMINAIS", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS", "QT_COMPARECIMENTO", "QT_APTOS"))
        if min(nominal, blank, nulls, attendance, apt) < 0 or nominal + blank + nulls != attendance or attendance > apt:
            raise ValueError("Detalhe não reconcilia votos/comparecimento/aptos")
        if population is not None and k[0] != "ZZ":
            historical_alias = HISTORICAL_NAME_ALIASES.get((k[0], normalized(row["NM_MUNICIPIO"])))
            if historical_alias and int(k[1]) != historical_alias[0]:
                raise ValueError("Alias histórico não corresponde ao código TSE esperado")
            mk = municipal_key(k[0], row["NM_MUNICIPIO"], aliases=True)
            if mk in municipality_codes and municipality_codes[mk] != k[1]:
                raise ValueError("Dois municípios TSE ligados à mesma população IBGE")
            municipality_codes[mk] = k[1]
            if municipal_key(k[0], row["NM_MUNICIPIO"]) != mk:
                aliases_used.add((k[0], row["NM_MUNICIPIO"], mk[1]))
            municipal_attendance[mk] = municipal_attendance.get(mk, 0) + attendance
        if nominal == 0:
            excluded["zeroNominal"] += 1
            continue
        s = sections.get(k)
        if s is None or s[0] + s[1] != nominal or s[2:4] != [blank, nulls]:
            raise ValueError("Votação ausente ou divergente do detalhe")
        if status_known:
            allowed.add(k)
        if status_known and s[1] == 0 and s[0] > 0 and k[0] != "ZZ":
            zero[k] = {"opponentVotes": s[0], "blank": blank, "null": nulls, "attendance": attendance,
                       "name": row.get("NM_LOCAL_VOTACAO", s[5])}
    if not seen:
        raise ValueError("Universo de detalhe vazio")
    missing_detail = sum(k not in seen for k, s in sections.items() if s[0] + s[1] > 0)
    if missing_detail:
        raise ValueError("Seções com voto sem detalhe")
    report = {"detailSections": len(seen), "excludedByStatus": excluded, "unknownStatusSections": unknown_status,
              "positiveVoteSectionsWithoutDetail": missing_detail}
    if population is not None:
        matched = municipal_attendance.keys() & population.keys()
        unmatched = municipal_attendance.keys() - population.keys()
        above = [k for k in matched if municipal_attendance[k] > population[k]]
        report["attendanceAboveCensus2022"] = {
            "municipalitiesInTSE": len(municipal_attendance), "matchedByUFAndNormalizedName": len(matched),
            "unmatchedMunicipalities": [f"{uf}-{name}" for uf, name in sorted(unmatched)],
            "explicitAliasesApplied": [{"uf": uf, "tseName": name, "normalizedIBGEName": target} for uf, name, target in sorted(aliases_used)],
            "municipalitiesAbovePopulation": len(above), "authorReference": 52,
            "differenceFromReference": len(above) - 52,
            "scope": "2022 segundo turno; seções instaladas e não anuladas; comparecimento versus população residente Censo2022; junção UF+nome normalizado, aliases explícitos de conferir_municipios.py e dois aliases históricos com código TSE conferido; sem fuzzy",
            "limits": "Domicílio eleitoral e residência censitária são conceitos diferentes; excedente não prova voto irregular."}
    return allowed, zero, report


def first_turn(source_rows, zero_keys):
    counts, seen_options, names = {}, set(), {}
    for row in source_rows:
        if not selected(row, 2026, 1):
            continue
        k = key(row)
        if k not in zero_keys:
            continue
        number, amount = int(row["NR_VOTAVEL"]), int(row["QT_VOTOS"])
        if amount < 0 or (k, number) in seen_options:
            raise ValueError("Votação de primeiro turno negativa ou duplicada")
        seen_options.add((k, number))
        s = counts.setdefault(k, [0, 0])  # total nominal da seção, votos para22
        if number not in (95, 96):
            s[0] += amount
        if number == 22:
            s[1] = amount
        names[k] = row["NM_LOCAL_VOTACAO"]
    matched = {k: s[1] for k, s in counts.items() if s[0] > 0}
    return {"matchedSections": len(matched), "missingOrEmptySections": len(zero_keys - matched.keys()),
            "flavioVotes": sum(matched.values()), "zeroFlavioSections": sum(v == 0 for v in matched.values()),
            "oneToFiveFlavioSections": sum(1 <= v <= 5 for v in matched.values()),
            "atMostFiveFlavioSections": sum(v <= 5 for v in matched.values()),
            "aboveFiveFlavioSections": sum(v > 5 for v in matched.values()),
            "maximumFlavioVotes": max(matched.values(), default=None),
            "distribution": {str(v): list(matched.values()).count(v) for v in sorted(set(matched.values()))}}


def section_distribution(sections, allowed):
    eligible = {k: s for k, s in sections.items() if k in allowed and k[0] != "ZZ" and s[0] + s[1] > 0}
    nominal = Counter(tuple(s[:2]) for s in eligible.values())
    full = Counter(tuple(s[:4]) for s in eligible.values())
    municipal = Counter((k[0], k[1], *s[:4]) for k, s in eligible.items())
    zone = Counter((k[0], k[1], k[2], *s[:4]) for k, s in eligible.items())
    return {"scope": "Brasil sem exterior, segundo turno2026; instaladas, não anuladas, nominal positivo",
        "sections": len(eligible),
        "H04": {"lulaAbove90Percent": sum(10*s[0] > 9*(s[0]+s[1]) for s in eligible.values()),
                "flavioAbove90Percent": sum(10*s[1] > 9*(s[0]+s[1]) for s in eligible.values()),
                "threshold": "Estritamente mais de90% dos votos nominais; não inclui exatamente90%",
                "authorReference": {"lula": 6802, "flavio": 368}},
        "H08": {"repeatedNominalScoreGroups": sum(n >= 2 for n in nominal.values()),
                "sectionsInRepeatedNominalScoreGroups": sum(n for n in nominal.values() if n >= 2),
                "repeatedFourOptionScoreGroups": sum(n >= 2 for n in full.values()),
                "sectionsInRepeatedFourOptionScoreGroups": sum(n for n in full.values() if n >= 2),
                "repeatedFourOptionGroupsWithinMunicipality": sum(n >= 2 for n in municipal.values()),
                "repeatedFourOptionGroupsWithinZone": sum(n >= 2 for n in zone.values()),
                "definition": "Grupo com frequência>=2. Placar nominal=(Lula,Flávio); quatro opções=(Lula,Flávio,brancos,nulos). Não é cópia integral de todos os campos de um BU.",
                "authorReference": {"nominalScoreGroups": 41133, "fourOptionScoreGroups": 54304, "sectionsInFourOptionGroups": 117488},
                "simulation": None,
                "limits": "Reproduz frequências observadas; não executa simulação, distribuição nula ou teste de significância."}}


def load_population(path, provenance):
    content = path.read_bytes()
    payload = json.loads(content)
    result = payload[0]["resultados"][0]
    categories = {item["id"]: item["categoria"] for item in result["classificacoes"]}
    if len(payload) != 1 or payload[0]["id"] != "93" or len(payload[0]["resultados"]) != 1 or categories != {
            "2": {"6794": "Total"}, "286": {"113635": "Total"}, "287": {"100362": "Total"}}:
        raise ValueError("Consulta IBGE não corresponde à população municipal total2022")
    index = {}
    for item in result["series"]:
        if item["localidade"]["nivel"]["id"] != "N6":
            raise ValueError("Nível IBGE não é municipal")
        name, uf = item["localidade"]["nome"].rsplit(" - ", 1)
        k = municipal_key(uf, name)
        if k in index:
            raise ValueError("Município IBGE duplicado na chave UF/nome")
        index[k] = int(item["serie"]["2022"])
    provenance["ibgeCensus2022"] = {"url": "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93?localidades=N6%5Ball%5D&classificacao=2%5B6794%5D%7C286%5B113635%5D%7C287%5B100362%5D",
        "sha256": hashlib.sha256(content).hexdigest(), "archiveBytes": len(content), "edition": "Censo Demográfico 2022, tabela 9514, população total"}
    return index


def run(data_dir, population_json=None):
    start, started, provenance, history = time.perf_counter(), datetime.now(timezone.utc).isoformat(), {}, {}
    zero_2026 = None
    population = load_population(population_json, provenance) if population_json is not None else None
    for year in (2026, 2022, 2018):
        votes = aggregate_votes(rows(data_dir / f"votacao_secao_{year}_BR.zip", year, "votes", provenance, PINS[year]), year)
        entry = {"target": "Bolsonaro" if year != 2026 else "Flávio", "opponent": "Haddad" if year == 2018 else "Lula",
                 "allPositiveVoteSectionsBrazil": count_scope(votes),
                 "allPositiveVoteSectionsIncludingForeign": count_scope(votes, include_foreign=True)}
        if year != 2026 and zero_2026 is not None:
            matched = [votes[k] for k in zero_2026 if k in votes and votes[k][0] + votes[k][1] > 0]
            entry["within2026ZeroSectionsBySameKey"] = {"matchedSections": len(matched),
                "targetVotes": sum(s[1] for s in matched), "zeroTargetSections": sum(s[1] == 0 for s in matched)}
        detail = data_dir / f"detalhe_votacao_secao_{year}.zip"
        if detail.exists():
            allowed, zero, checks = check_details(rows(detail, year, "detail", provenance, DETAIL_PINS[year]), votes, year,
                                                population if year == 2022 else None)
            entry.update(statusChecks=checks,
                         installedNonAnnulledBrazil=count_scope(votes, allowed) if not checks["unknownStatusSections"] else None,
                         installedNonAnnulledIncludingForeign=count_scope(votes, allowed, True) if not checks["unknownStatusSections"] else None)
            if year == 2026:
                entry["sectionDistribution"] = section_distribution(votes, allowed)
                zero_2026 = zero
                entry["attendanceInZeroSections"] = sum(s["attendance"] for s in zero.values())
                entry["zeroBlankAndNullSections"] = sum(s["blank"] == s["null"] == 0 for s in zero.values())
                entry["locationNameTerms"] = {"regex": TERMS, "matchedSections": sum(bool(re.search(TERMS, normalized(s["name"]))) for s in zero.values()),
                                              "totalSections": len(zero), "source": "NM_LOCAL_VOTACAO do detalhe oficial, segundo turno"}
        else:
            entry["statusChecks"] = {"status": "not_available", "reason": "ZIP de detalhe não fornecido; voto positivo não certifica status"}
        reference = {2018: 328, 2022: 141, 2026: 106}[year]
        entry["authorReferenceZeroTargetSections"] = reference
        entry["differenceFromReferenceBrazil"] = entry["allPositiveVoteSectionsBrazil"]["zeroTargetSections"] - reference
        history[str(year)] = entry
    if zero_2026 is not None:
        history["2026"]["firstTurnWithinSecondTurnZeroSections"] = first_turn(
            rows(data_dir / "votacao_secao_2026_BR.zip", 2026, "votes", provenance, PINS[2026]), set(zero_2026))
    return {"schema": "alp.historical-zero-sections.v1", "claim": "H07", "status": "recomputed_from_official_archives",
            "scope": "Eleição ordinária, presidente, segundo turno; chave UF/município/zona/seção; opções ausentes só em seções com nominal positivo.",
            "sources": provenance, "results": history,
            "authorReference": {"url": "https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026/blob/4a12ed014cf7927df24226f900450db7fe5b1a22/ferramentas/analise.py", "commit": "4a12ed014cf7927df24226f900450db7fe5b1a22"},
            "limits": ["Agregados de seção não identificam eleitores, mortes ou transferência individual de voto e não provam fraude nem integridade.",
                       "Correspondência da chave entre eleições não garante mesmos eleitores, composição ou local.",
                       "Regex reproduz indícios no nome do local; não classifica identidade étnica de pessoas nem confirma comunidade indígena.",
                       "A contagem por nome usa o detalhe oficial, enquanto o autor usa cadastro de locais; fontes podem divergir.",
                       "Históricos sem ZIP de detalhe não tiveram status de instalação/anulação reconciliado.",
                       "Testes do próprio DEV; não constituem validação independente."],
            "execution": {"startedAt": started, "finishedAt": datetime.now(timezone.utc).isoformat(),
                          "elapsedSeconds": round(time.perf_counter()-start, 3), "officialTokens": None,
                          "engine": "Python 3.12 stdlib csv/zipfile", "device": "CPU", "fallback": None}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--population-json", type=Path, help="Resposta opcional da API IBGE tabela9514/população municipal total2022")
    args = parser.parse_args()
    payload = json.dumps(run(args.data_dir, args.population_json), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
