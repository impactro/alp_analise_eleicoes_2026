"""Confere H13 em agregados TSE e IBGE, sem rede ou dependências externas."""

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
AGES = {"8589": "85 a 89 anos", "9094": "90 a 94 anos", "9599": "95 a 99 anos", "9999": "100 anos ou mais"}
IBGE_AGES = {"6649": "96 anos", "6650": "97 anos", "6651": "98 anos", "6652": "99 anos", "6653": "100 anos ou mais"}
IBGE_URL = ("https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93"
            "?localidades=N1%5B1%5D&classificacao=2%5B6794%5D%7C286%5B113635%5D"
            "%7C287%5B6649%2C6650%2C6651%2C6652%2C6653%5D")
REFERENCE = "https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026/tree/4a12ed014cf7927df24226f900450db7fe5b1a22"


def source_metadata(path, expected, url, edition):
    path = Path(path)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != expected.lower():
        raise ValueError("SHA-256 divergente; não combinar edições")
    return {"url": url, "sha256": digest, "bytes": path.stat().st_size, "edition": edition}


def select_members(names, prefix):
    """Nacional BRASIL sozinho; na ausência, 27 UFs + exterior, sem sobreposição."""
    national = prefix + "_BRASIL.csv"
    if names.count(national) > 1:
        raise ValueError("Membro nacional duplicado")
    if national in names:
        return [national]
    wanted = [prefix + "_" + uf + ".csv" for uf in sorted(UFS | {"ZZ"})]
    if any(names.count(name) != 1 for name in wanted):
        raise ValueError("ZIP sem membro BRASIL nem conjunto completo e único de UFs/ZZ")
    return wanted


def nonnegative(value):
    result = int(value)
    if result < 0:
        raise ValueError("Quantidade negativa")
    return result


def aggregate_rows(rows, headers, kind, year=2026):
    year_field = "AA_ELEICAO" if kind == "electorate" else "ANO_ELEICAO"
    metrics = ("QT_ELEITORES", "QT_ELEITORES_BIOMETRIA") if kind == "electorate" else ("QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO")
    required = {year_field, "SG_UF", "CD_FAIXA_ETARIA", "DS_FAIXA_ETARIA", "DT_GERACAO", "HH_GERACAO", *metrics}
    if kind == "attendance":
        required.add("NR_TURNO")
    if not required <= set(headers):
        raise ValueError("Cabeçalho incompleto")
    idx = {name: headers.index(name) for name in required}
    sums, generations, observed_ufs, counts = {}, set(), set(), {}
    for row in rows:
        if len(row) != len(headers):
            raise ValueError("Linha com quantidade incorreta de colunas")
        if int(row[idx[year_field]]) != year:
            raise ValueError("Ano inesperado no arquivo")
        uf = row[idx["SG_UF"]]
        if uf not in UFS | {"ZZ"}:
            raise ValueError("UF inesperada")
        observed_ufs.add(uf)
        generations.add((row[idx["DT_GERACAO"]], row[idx["HH_GERACAO"]]))
        turn = "cadastro" if kind == "electorate" else row[idx["NR_TURNO"]]
        if turn not in {"cadastro", "1", "2"}:
            raise ValueError("Turno inesperado")
        counts[turn] = counts.get(turn, 0) + 1
        age = row[idx["CD_FAIXA_ETARIA"]]
        if age not in AGES:
            continue
        if row[idx["DS_FAIXA_ETARIA"]] != AGES[age]:
            raise ValueError("Código e descrição da faixa etária divergentes")
        numbers = [nonnegative(row[idx[m]]) for m in metrics]
        if kind == "attendance" and numbers[0] != numbers[1] + numbers[2]:
            raise ValueError("Aptos não reconciliam comparecimento + abstenção")
        if kind == "electorate" and numbers[1] > numbers[0]:
            raise ValueError("Biometria maior que eleitorado")
        key = (turn, age, "exterior" if uf == "ZZ" else "brasil_sem_exterior")
        target = sums.setdefault(key, [0] * len(metrics))
        for i, value in enumerate(numbers):
            target[i] += value
    return {"sums": sums, "generations": generations, "ufs": observed_ufs, "rowCountsByTurn": counts}


def aggregate_archive(path, kind, year=2026):
    prefix = ("perfil_eleitorado_" if kind == "electorate" else "perfil_comparecimento_abstencao_") + str(year)
    merged = {"sums": {}, "generations": set(), "ufs": set(), "rowCountsByTurn": {}}
    with ZipFile(path) as archive:
        members = select_members(archive.namelist(), prefix)
        for name in members:
            with archive.open(name) as raw:
                reader = csv.reader(io.TextIOWrapper(raw, encoding="latin1"), delimiter=";")
                part = aggregate_rows(reader, next(reader), kind, year)
            merged["generations"].update(part["generations"])
            merged["ufs"].update(part["ufs"])
            for key, values in part["sums"].items():
                target = merged["sums"].setdefault(key, [0] * len(values))
                for i, value in enumerate(values):
                    target[i] += value
            for turn, amount in part["rowCountsByTurn"].items():
                merged["rowCountsByTurn"][turn] = merged["rowCountsByTurn"].get(turn, 0) + amount
    if merged["ufs"] != UFS | {"ZZ"}:
        raise ValueError("Cobertura geográfica incompleta")
    merged["members"] = members
    return merged


def census_totals(data):
    """Exige cinco idades, sexo e declaração totais, um valor nacional por idade."""
    if len(data) != 1 or data[0]["id"] != "93" or data[0]["unidade"] != "Pessoas":
        raise ValueError("Variável censitária inesperada")
    found = {}
    for result in data[0]["resultados"]:
        classes = {c["id"]: c["categoria"] for c in result["classificacoes"]}
        if set(classes) != {"2", "286", "287"} or classes["2"] != {"6794": "Total"} or classes["286"] != {"113635": "Total"}:
            raise ValueError("Classificações censitárias inesperadas")
        if len(classes["287"]) != 1:
            raise ValueError("Idade censitária ambígua")
        age, label = next(iter(classes["287"].items()))
        if age not in IBGE_AGES or label != IBGE_AGES[age] or age in found:
            raise ValueError("Idade censitária inesperada ou duplicada")
        if len(result["series"]) != 1:
            raise ValueError("Esperada uma série nacional")
        series = result["series"][0]
        if series["localidade"]["id"] != "1" or series["localidade"]["nivel"]["id"] != "N1" or set(series["serie"]) != {"2022"}:
            raise ValueError("Geografia/período censitário inesperado")
        found[age] = nonnegative(series["serie"]["2022"])
    if set(found) != set(IBGE_AGES):
        raise ValueError("Consulta censitária incompleta")
    return {"byAge": {IBGE_AGES[k]: found[k] for k in IBGE_AGES}, "population96plus": sum(found.values()), "population100plus": found["6653"]}


def compare(electorate, attendance, census):
    e100 = electorate["sums"][("cadastro", "9999", "brasil_sem_exterior")][0]
    by_age = {}
    turns = sorted(attendance["rowCountsByTurn"])
    for age, label in AGES.items():
        voters, bio = electorate["sums"].get(("cadastro", age, "brasil_sem_exterior"), (0, 0))
        observations = {}
        for turn in turns:
            apt, present, absent = attendance["sums"].get((turn, age, "brasil_sem_exterior"), (0, 0, 0))
            observations[turn] = {"eligible": apt, "attendance": present, "abstention": absent,
                                  "attendancePct": round(100 * present / apt, 6) if apt else None,
                                  "attendanceOverBiometricRegistrationsPct": round(100 * present / bio, 6) if bio else None}
        by_age[label] = {"registered": voters, "withBiometrics": bio, "byTurn": observations}
    return {"electorate100plus2026": e100, "census2022": census,
            "differenceElectorate100plusMinusCensus96plus": e100 - census["population96plus"],
            "ratioElectorate100plusToCensus96plus": round(e100 / census["population96plus"], 6),
            "differenceElectorate100plusMinusCensus100plusSameAgeDifferentDates": e100 - census["population100plus"],
            "availableAttendanceTurns": turns, "attendanceByAge": by_age,
            "exteriorElectorate100plusExcluded": electorate["sums"].get(("cadastro", "9999", "exterior"), [0])[0]}


def run(args):
    started = datetime.now(timezone.utc).isoformat()
    timer = time.perf_counter()
    sources = {}
    tables = {}
    for kind, path, expected, family in (
        ("electorate", args.electorate_zip, args.electorate_sha256, "perfil_eleitorado"),
        ("attendance", args.attendance_zip, args.attendance_sha256, "perfil_comparecimento_abstencao"),
    ):
        url = f"https://cdn.tse.jus.br/estatistica/sead/odsele/{family}/{family}_2026.zip"
        sources[kind] = source_metadata(path, expected, url, "Arquivo TSE 2026 identificado pelo SHA-256; geração interna abaixo")
        tables[kind] = aggregate_archive(path, kind)
        sources[kind]["csvMembersRead"] = tables[kind]["members"]
        sources[kind]["csvGenerationDatesAndTimes"] = sorted(tables[kind]["generations"])
        sources[kind]["rowCountsByTurnIncludingExterior"] = tables[kind]["rowCountsByTurn"]
    sources["census"] = source_metadata(args.census_json, args.census_sha256, IBGE_URL, "Censo Demográfico 2022; tabela 9514; variável 93; consulta nacional N1[1]")
    sources["census"]["retrievalLayer"] = "primary_ibge_api"
    census = census_totals(json.loads(Path(args.census_json).read_text(encoding="utf-8")))
    result = compare(tables["electorate"], tables["attendance"], census)
    actual = {"electorate100plus2026": result["electorate100plus2026"], "censusPopulation96plus2022": census["population96plus"],
              "difference": result["differenceElectorate100plusMinusCensus96plus"],
              "attendance100plusFirstTurn": result["attendanceByAge"][AGES["9999"]]["byTurn"].get("1", {}).get("attendance")}
    claimed = {"electorate100plus2026": 297977, "censusPopulation96plus2022": 149424, "difference": 148553, "attendance100plusFirstTurn": 2141}
    first_turn_rate = result["attendanceByAge"][AGES["9999"]]["byTurn"].get("1", {}).get("attendancePct")
    return {"schema": "alp.age-check.v1", "claim": "H13", "status": "recomputed_from_primary_sources",
            "scope": "Eleitorado e comparecimento de 2026, Brasil sem exterior; Censo 2022 nacional. Sem identificação individual.",
            "sources": sources, "results": result,
            "referenceComparison": {"reference": REFERENCE, "expected": claimed, "actual": actual, "matches": actual == claimed,
                                    "referenceAttendancePctRounded": 0.72,
                                    "actualAttendancePctRounded": round(first_turn_rate, 2) if first_turn_rate is not None else None},
            "limits": ["Cadastro eleitoral, população residente e comparecimento são universos e datas distintos.",
                       "96 anos ou mais em 2022 é uma aproximação de coorte para 100 anos ou mais em 2026; não incorpora aniversário exato, migração, mortalidade nem erro de idade/cobertura.",
                       "A diferença agregada não identifica óbitos, registros individuais impossíveis, voto de falecido ou fraude.",
                       "Comparecimento publicado por faixa etária não atribui votos a candidato e não atesta identificação biométrica em cada votação.",
                       "Turno ausente do arquivo não equivale a comparecimento zero; esta edição só pode responder pelos turnos efetivamente observados.",
                       "Não reproduzido o cruzamento municipal ou o controle de eleitorado de 2022 do autor."],
            "execution": {"startedAtUtc": started, "finishedAtUtc": datetime.now(timezone.utc).isoformat(),
                          "elapsedSeconds": round(time.perf_counter() - timer, 3), "officialTokensBaseline": None,
                          "officialTokensFinal": None, "officialTokensDelta": None, "externalPaidProviders": False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("electorate", "attendance"):
        parser.add_argument("--" + name + "-zip", type=Path, required=True)
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--census-json", type=Path, required=True)
    parser.add_argument("--census-sha256", required=True)
    args = parser.parse_args()
    # ASCII JSON também atravessa shells com encoding legado sem corromper texto.
    print(json.dumps(run(args), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
