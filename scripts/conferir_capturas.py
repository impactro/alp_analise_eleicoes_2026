"""Código próprio para conferir tabelas/capturas públicas preservadas pelo autor.

Não revalida a aquisição original dos BUs/logs. Parquet requer pyarrow opcional.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

COMMIT = '4a12ed014cf7927df24226f900450db7fe5b1a22'
REPO = 'https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026'
FUSO = {'ac': 2, 'am': 1, 'ro': 1, 'rr': 1, 'mt': 1, 'ms': 1}
COLS = ['uf','situacao','abertura','encerramento','bu_lula','bu_flavio','comparecimento',
        'log_votos_depois_17h','log_votos_depois_19h','log_manual_mesario','log_manual_sem_digital','log_ja_votou']


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def hour_seconds(value):
    if not value:
        return None
    t = datetime.fromisoformat(value)
    return t.hour*3600+t.minute*60+t.second


def summarize_captured_rows(rows):
    sums = Counter()
    groups = {n: Counter() for n in ('local_all_before1701','bsb_brazil_before1701','bsb_brazil_from1716')}
    for r in rows:
        sums['rows'] += 1
        if r['situacao'] == 'Nao instalada':
            continue
        sums['installedRows'] += 1
        local = hour_seconds(r['encerramento'])
        opening = hour_seconds(r['abertura'])
        oh = opening//3600 if opening is not None else None
        offset = (8-oh) if oh in (6,7,8) else FUSO.get(r['uf'],0)
        if oh not in (6,7,8): sums['fallbackOffsetRows'] += 1
        bsb = local + offset*3600 if local is not None else None
        if local is None: sums['missingClosingRows'] += 1
        selected = []
        if local is not None and local < 17*3600+60:
            selected.append('local_all_before1701')
        if r['uf'] != 'zz':
            sums['brazilRows'] += 1
            for c in ('log_votos_depois_17h','log_votos_depois_19h','log_manual_mesario','log_manual_sem_digital','log_ja_votou'):
                if r[c] is None:
                    sums['missing_'+c] += 1
                else:
                    v = int(r[c])
                    if v < 0: raise ValueError('Evento negativo')
                    sums[c] += v
            if bsb is not None and bsb < 17*3600+60: selected.append('bsb_brazil_before1701')
            if bsb is not None and bsb >= 17*3600+16*60: selected.append('bsb_brazil_from1716')
        for g in selected:
            d=groups[g]; d['sections']+=1
            for src,col in [('bu_lula','lula'),('bu_flavio','flavio'),('comparecimento','attendance'),('log_votos_depois_17h','loggedVotesAfter17')]:
                if r[src] is not None: d[col]+=int(r[src])
                else: d['missing_'+col]+=1
    result={}
    for name,c in groups.items():
        result[name]=dict(c)
        total=c['lula']+c['flavio']
        result[name]['flavioPercent']=round(100*c['flavio']/total,2) if total else None
    return {'counts': dict(sums), 'groups': result,
            'offsetMethod': 'Opening-hour6/7/8 mapped to common opening08Brasilia; otherwise UF fallback. Reproduces documented author assumption, not an independent timezone audit.'}


def read_parquet(path):
    import pyarrow.parquet as pq
    for batch in pq.ParquetFile(path).iter_batches(batch_size=8192,columns=COLS):
        yield from batch.to_pylist()


def snapshot_row(doc):
    if doc['tpabr'] != 'br' or doc['t'] != '2':
        raise ValueError('Exige versão nacional do segundo turno')
    cargos=[c for c in doc['carg'] if c['cd']=='1']
    if len(cargos)!=1: raise ValueError('Cargo presidencial ausente/duplicado')
    votes={}
    for group in cargos[0]['agr']:
        for party in group['par']:
            for candidate in party['cand']:
                n=candidate['n']
                if n in votes: raise ValueError('Candidato duplicado na versão')
                votes[n]=int(candidate['vap'])
    if not {'13','22'} <= votes.keys(): raise ValueError('Candidato ausente não é zero')
    if any(v<0 for v in votes.values()): raise ValueError('Total negativo')
    return {'generated': datetime.strptime(doc['dg']+' '+doc['hg'],'%d/%m/%Y %H:%M:%S').isoformat(),
            'id': int(doc['idg']), 'lula': votes['13'], 'flavio': votes['22']}


def snapshot_series(rows):
    ids=[r['id'] for r in rows]
    if len(set(ids))!=len(ids): raise ValueError('Versão nacional repetida')
    rows=sorted(rows,key=lambda r:(r['generated'],r['id']))
    if len(rows)<2: raise ValueError('Série insuficiente')
    drops={c:sum(b[c]<a[c] for a,b in zip(rows,rows[1:])) for c in ('lula','flavio')}
    return {'versions': len(rows),'nominalDecreases':drops,'first':rows[0],'last':rows[-1],
            'scope': 'Somente versões nacionais preservadas; não prova o que ocorreu entre capturas.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parquet',required=True)
    ap.add_argument('--parquet-sha256',required=True)
    ap.add_argument('--national-captures',required=True)
    a=ap.parse_args()
    h=sha(a.parquet)
    if h!=a.parquet_sha256.lower(): raise ValueError('Hash Parquet divergente')
    snaps=sorted(Path(a.national_captures).glob('*.json'))
    pins=[{'name':f.name,'sha256':sha(f)} for f in snaps]
    # Selo lógico por nome+hash; lista completa fica nos arquivos de entrada, fora do Git.
    set_hash=hashlib.sha256(json.dumps(pins,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    terms={'H02':34424,'H13':148553,'H14':33408,'H15':113315,'H18':49110,'H23':3025,'H10':246,'H07':118}
    total=sum(terms.values())
    out={'schema':'alp.captured-source-check.v1','status':'recomputed_from_author_preserved_inputs',
         'authorRepository':REPO,'authorCommit':COMMIT,
         'sources':{'parquet':{'url':REPO+'/blob/'+COMMIT+'/dados/copias/t2_secoes.parquet','sha256':h,'bytes':Path(a.parquet).stat().st_size},
                    'nationalCaptures':{'url':REPO+'/tree/'+COMMIT+'/dados/copias/noite/versoes-tse/br','files':len(snaps),'logicalNameHashSetSha256':set_hash}},
         'capturedSectionCalculations':summarize_captured_rows(read_parquet(a.parquet)),
         'nationalSeries':snapshot_series([snapshot_row(json.loads(f.read_text(encoding='utf-8'))) for f in snaps]),
         'publishedScenarioArithmetic':{'termsSuppliedByAuthor':terms,'sum':total,'nationalMargin':4430191,
                                        'percent':round(total/4430191*100,2),'level':'arithmetic_only; not validation of every input or of a global upper bound'},
         'limits':['Independent calculation code; original BU/log acquisition and transformations not independently repeated.',
                   'H02 table RESUMO and final narrative have different totals; retain versions rather than silently substituting.',
                   'Snapshot monotonicity is a count in the saved series, not a system-wide integrity proof.',
                   'Author scenario combines hypotheses and potentially overlapping categories; arithmetic is not a universal fraud bound.']}
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
