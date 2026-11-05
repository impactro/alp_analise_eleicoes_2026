"""Recalcula H14/H19/H20/H23 de ZIPs TSE e resposta primária IBGE; stdlib."""
import argparse
import csv
import hashlib
import io
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

REGIONS = {uf: region for region, ufs in {
    'Norte': 'AC AM AP PA RO RR TO', 'Nordeste': 'AL BA CE MA PB PE PI RN SE',
    'Centro-Oeste': 'DF GO MS MT', 'Sudeste': 'ES MG RJ SP', 'Sul': 'PR RS SC'
}.items() for uf in ufs.split()}
LAGOS = {'ARARUAMA', 'CABO FRIO', 'SAO PEDRO DA ALDEIA', 'SAQUAREMA',
         'ARRAIAL DO CABO', 'ARMACAO DOS BUZIOS', 'IGUABA GRANDE'}
# Variações explícitas de grafia entre TSE2026 e a resposta IBGE2022.
# Não há aproximação fonética nem busca pela população desejada.
NAME_ALIASES = {
    ('GO', 'BOM JESUS'): 'BOM JESUS DE GOIAS',
    ('MG', 'BARAO DE MONTE ALTO'): 'BARAO DO MONTE ALTO',
    ('MG', 'DONA EUSEBIA'): 'DONA EUZEBIA',
    ('MG', 'SAO THOME DAS LETRAS'): 'SAO TOME DAS LETRAS',
    ('MT', 'SANTO ANTONIO DO LEVERGER'): 'SANTO ANTONIO DE LEVERGER',
    ('PA', 'ELDORADO DOS CARAJAS'): 'ELDORADO DO CARAJAS',
    ('PR', 'MUNHOZ DE MELLO'): 'MUNHOZ DE MELO',
    ('RN', 'BOA SAUDE'): 'JANUARIO CICCO',
    ('RO', 'ESPIGAO DO OESTE'): "ESPIGAO D'OESTE",
    ('RO', 'ALVORADA DO OESTE'): "ALVORADA D'OESTE",
    ('RR', 'SAO LUIZ'): 'SAO LUIZ DO ANAUA',
    ('SE', 'AMPARO DE SAO FRANCISCO'): 'AMPARO DO SAO FRANCISCO',
    ('SP', 'SAO LUIS DO PARAITINGA'): 'SAO LUIZ DO PARAITINGA',
}


def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text).upper()
                   if not unicodedata.combining(c))


def pct(a, b):
    return round(100 * a / b, 2) if b else None


def name_key(name):
    return ''.join(c for c in norm(name) if c.isalnum())


def checked(path, expected, url):
    p = Path(path)
    with p.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != expected.lower():
        raise ValueError('SHA256 divergente; fixar a edição antes de comparar')
    return {'url': url, 'sha256': digest, 'bytes': p.stat().st_size}


def archive_rows(path, member):
    with ZipFile(path) as z:
        if z.namelist().count(member) != 1:
            raise ValueError('Membro nacional ausente ou repetido')
        with z.open(member) as binary:
            yield from csv.DictReader(io.TextIOWrapper(binary, encoding='latin1', newline=''), delimiter=';')


def municipal_votes(rows):
    out, seen, generations = {}, set(), set()
    for r in rows:
        if r['CD_CARGO'] != '1' or r['CD_TIPO_ELEICAO'] != '2' or r['SG_UF'] == 'ZZ':
            continue
        if r['ANO_ELEICAO'] != '2026':
            raise ValueError('Ano de votação inesperado')
        turn, uf = int(r['NR_TURNO']), r['SG_UF']
        if turn not in (1, 2) or uf not in REGIONS:
            raise ValueError('Turno/UF inesperado')
        key = (turn, uf, r['CD_MUNICIPIO'], r['NR_ZONA'], r['SQ_CANDIDATO'],
               r['NM_TIPO_DESTINACAO_VOTOS'], r.get('ST_VOTO_EM_TRANSITO'))
        if key in seen:
            raise ValueError('Linha municipal duplicada')
        seen.add(key)
        generations.add(r['DT_GERACAO'] + ' ' + r['HH_GERACAO'])
        m = out.setdefault((uf, str(int(r['CD_MUNICIPIO']))), {'name': r['NM_MUNICIPIO'], 1: {}, 2: {}})
        dest = m[turn]
        n = r['NR_CANDIDATO']
        col = 'lula' if n == '13' else 'flavio' if n == '22' else 'others'
        v = int(r['QT_VOTOS_NOMINAIS_VALIDOS'])
        if v < 0:
            raise ValueError('Voto negativo')
        dest[col] = dest.get(col, 0) + v
        dest['valid'] = dest.get('valid', 0) + v
    if len(generations) != 1 or not out:
        raise ValueError('Gerações misturadas ou votação vazia')
    return out, sorted(generations)


def municipal_detail(rows):
    out, seen, generations = {}, set(), set()
    cols = {'aptos': 'QT_APTOS', 'attendance': 'QT_COMPARECIMENTO', 'absence': 'QT_ABSTENCOES',
            'blank': 'QT_VOTOS_BRANCOS', 'null': 'QT_VOTOS_NULOS', 'nominalRaw': 'QT_VOTOS_NOMINAIS'}
    for r in rows:
        if r['CD_CARGO'] != '1' or r['CD_TIPO_ELEICAO'] != '2' or r['SG_UF'] == 'ZZ':
            continue
        if r['ANO_ELEICAO'] != '2026':
            raise ValueError('Ano de detalhe inesperado')
        t, uf, code = int(r['NR_TURNO']), r['SG_UF'], str(int(r['CD_MUNICIPIO']))
        if t not in (1, 2) or uf not in REGIONS:
            raise ValueError('Turno/UF de detalhe inesperado')
        key = (t, uf, code, r['NR_ZONA'], r['NR_SECAO'])
        if key in seen:
            raise ValueError('Seção duplicada no detalhe')
        seen.add(key)
        generations.add(r['DT_GERACAO'] + ' ' + r['HH_GERACAO'])
        m = out.setdefault((uf, code), {1: {}, 2: {}})[t]
        for col, src in cols.items():
            v = int(r[src])
            if v < 0:
                raise ValueError('Contagem negativa no detalhe')
            m[col] = m.get(col, 0) + v
    if len(generations) != 1 or not out:
        raise ValueError('Geração de detalhe misturada ou vazia')
    return out, sorted(generations)


def census_population(doc):
    out = {}
    for variable in doc:
        if str(variable['id']) != '93':
            raise ValueError('Variável IBGE inesperada')
        for result in variable['resultados']:
            cats = {str(c['id']): set(c['categoria']) for c in result['classificacoes']}
            if cats != {'2': {'6794'}, '286': {'113635'}, '287': {'100362'}}:
                raise ValueError('Censo exige sexo, declaração e idade totais')
            for series in result['series']:
                loc = series['localidade']
                if loc['nivel']['id'] != 'N6':
                    raise ValueError('População exige municípios')
                name, uf = loc['nome'].rsplit(' - ', 1)
                key = (uf, name_key(name))
                if key in out:
                    raise ValueError('Localidade IBGE repetida')
                value = series['serie']['2022']
                if not value.isdigit():
                    raise ValueError('População ausente não pode ser zero')
                out[key] = {'id': loc['id'], 'population': int(value)}
    return out


def calculate(votes, detail, population):
    if set(votes) != set(detail):
        raise ValueError('Universos de municípios dos ZIPs divergentes')
    missing, aliases_used, joined = [], [], set()
    municipalities = []
    for (uf, code), v in sorted(votes.items()):
        if not all(v[t] and detail[uf, code][t] for t in (1, 2)):
            raise ValueError('Município sem os dois turnos')
        m = {'uf': uf, 'code': code, 'name': v['name'], 1: v[1] | detail[uf, code][1],
             2: v[2] | detail[uf, code][2]}
        for t in (1, 2):
            for field in ('lula', 'flavio', 'others'):
                m[t].setdefault(field, 0)
            if m[t]['aptos'] != m[t]['attendance'] + m[t]['absence']:
                raise ValueError('Aptos não reconciliam com comparecimento/abstenção')
        cname = NAME_ALIASES.get((uf, norm(v['name'])), v['name'])
        pop = population.get((uf, name_key(cname)))
        if pop:
            if pop['id'] in joined:
                raise ValueError('Dois municípios TSE ligados à mesma população IBGE')
            joined.add(pop['id'])
            m.update(pop)
            if norm(cname) != norm(v['name']):
                aliases_used.append({'uf': uf, 'tseName': v['name'], 'ibgeName': cname, 'ibgeCode': pop['id']})
        else:
            missing.append({'uf': uf, 'municipality': v['name']})
        municipalities.append(m)
    states = defaultdict(lambda: {1: defaultdict(int), 2: defaultdict(int)})
    regions = defaultdict(lambda: {1: defaultdict(int), 2: defaultdict(int)})
    for m in municipalities:
        for t in (1, 2):
            for k, v in m[t].items():
                states[m['uf']][t][k] += v
                regions[REGIONS[m['uf']]][t][k] += v
    decreased = {uf: {'flavioDelta': d[2]['flavio'] - d[1]['flavio'],
                     'attendanceDelta': d[2]['attendance'] - d[1]['attendance']}
                 for uf, d in states.items() if d[2]['flavio'] < d[1]['flavio']}
    above = [m for m in municipalities if 'population' in m and m[2]['attendance'] > m['population']]
    lula_above = [m for m in municipalities if 'population' in m and m[2]['lula'] > m['population']]
    rj = [m for m in municipalities if m['uf'] == 'RJ']
    lagos = [m for m in rj if norm(m['name']) in LAGOS]
    if len(lagos) != 7:
        raise ValueError('Região dos Lagos do autor deve conter exatamente sete cidades')
    def gains(ms):
        return tuple(sum(m[2][c] - m[1][c] for m in ms) for c in ('lula', 'flavio'))
    g_l, g_f = gains(lagos)
    f1 = sum(m[1]['flavio'] for m in lagos) / sum(m[1]['valid'] for m in lagos)
    peers = [m for m in rj if norm(m['name']) not in LAGOS and
             abs(m[1]['flavio'] / m[1]['valid'] - f1) <= 0.05]
    p_l, p_f = gains(peers)
    cases = []
    for m in municipalities:
        if (m['uf'] == 'RJ' and norm(m['name']) in LAGOS) or (m['uf'] == 'SC' and norm(m['name']) == 'JOACABA'):
            cases.append({'uf': m['uf'], 'municipality': m['name'],
                          'first': m[1], 'second': m[2],
                          'lulaGain': m[2]['lula'] - m[1]['lula'],
                          'flavioGain': m[2]['flavio'] - m[1]['flavio'],
                          'explicitBlankNullDrop': m[1]['blank']+m[1]['null']-m[2]['blank']-m[2]['null'],
                          'attendanceLessValidDrop': (m[1]['attendance']-m[1]['valid'])-(m[2]['attendance']-m[2]['valid']),
                          'nonValidNominalOrEditionResidualFirst': m[1]['attendance']-m[1]['valid']-m[1]['blank']-m[1]['null']})
    return {'H14': {'municipalities': len(municipalities), 'matchedPopulation': len(municipalities)-len(missing),
                    'unmatchedPopulation': missing, 'populationJoinAliases': aliases_used, 'attendanceAboveCensus': len(above),
                    'flavioWinsInThose': sum(m[2]['flavio'] > m[2]['lula'] for m in above),
                    'sumAttendanceMinusCensusPositive': sum(m[2]['attendance']-m['population'] for m in above),
                    'lulaVotesAbovePopulation': [{'uf': m['uf'], 'name': m['name'], 'population': m['population'],
                                                 'lula': m[2]['lula'], 'lulaFirst': m[1]['lula']} for m in lula_above]},
            'H19': {'flavioDecreases': decreased, 'lulaDecreases': [uf for uf,d in states.items() if d[2]['lula'] < d[1]['lula']]},
            'H20': {region: {'firstAbsencePercent': pct(d[1]['absence'], d[1]['aptos']),
                            'secondAbsencePercent': pct(d[2]['absence'], d[2]['aptos'])} for region,d in sorted(regions.items())},
            'H23': {'lagosLulaGain': g_l, 'lagosFlavioGain': g_f, 'lagosLulaShareOfNetGainPercent': pct(g_l,g_l+g_f),
                    'lagosFlavioFirstSharePercent': pct(sum(m[1]['flavio'] for m in lagos),sum(m[1]['valid'] for m in lagos)),
                    'peersInRJ': len(peers), 'peersLulaShareOfNetGainPercent': pct(p_l,p_l+p_f),
                    'lulaAbovePeerScenario': round(g_l - (p_l/(p_l+p_f))*(g_l+g_f)), 'cases': cases}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('votes', 'detail', 'population'):
        ap.add_argument('--'+name, required=True)
        ap.add_argument('--'+name+'-sha256', required=True)
    a = ap.parse_args()
    sources = {
        'votes': checked(a.votes,a.votes_sha256,'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip'),
        'detail': checked(a.detail,a.detail_sha256,'https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip'),
        'population': checked(a.population,a.population_sha256,'https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93?localidades=N6%5Ball%5D&classificacao=2%5B6794%5D%7C286%5B113635%5D%7C287%5B100362%5D')}
    votes, sources['votes']['generatedAtSource'] = municipal_votes(archive_rows(a.votes,'votacao_candidato_munzona_2026_BR.csv'))
    detail, sources['detail']['generatedAtSource'] = municipal_detail(archive_rows(a.detail,'detalhe_votacao_secao_2026_BR.csv'))
    result = {'schema': 'alp.municipal-reproduction.v1', 'status': 'recomputed_from_primary_sources',
              'sources': sources, 'scope': 'Brasil sem exterior; Presidente; eleição ordinária; dois turnos2026; população residente2022',
              'results': calculate(votes,detail,census_population(json.loads(Path(a.population).read_text(encoding='utf-8')))),
              'limits': ['Fontes TSE de edições distintas explicitadas; não constituem snapshot simultâneo.',
                         'Municípios sem correspondência exata de UF/nome não recebem população zero.',
                         'População residente não é eleitorado; excesso agregado não identifica votos irregulares.',
                         'Parte do saldo é razão de ganhos líquidos agregados, não destino individual de votos.',
                         'Comparação de municípios semelhantes é cenário descritivo, não estimativa causal de fraude.']}
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
