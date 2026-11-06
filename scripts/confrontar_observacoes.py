"""Confronta leituras documentadas de TV/jornal com a série histórica preservada.

Não faz OCR, não baixa mídia e não converte horário de publicação em hora do voto.
"""
import argparse
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path


def rounded(value, places=2):
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def canonical_observations_bytes(path):
    # Apenas artefato textual próprio; nunca aplicar às capturas/fontes brutas.
    return Path(path).read_bytes().replace(b'\r\n', b'\n')


def matches_numbers(observation, snapshot):
    if observation['scope'].lower() != snapshot['area'].lower():
        return False
    measurements = 0
    for field in ('lula', 'flavio'):
        value = observation.get('candidateVotes', {}).get(field)
        if value is not None:
            if type(value) is not int or value < 0:
                raise ValueError('Contagem observada deve ser inteiro não negativo, não aproximação')
            measurements += 1
            if value != snapshot['votes'].get(field):
                return False
        value = observation.get('candidatePercentages', {}).get(field)
        if value is not None:
            if not 0 <= value <= 100:
                raise ValueError('Percentual fora de0..100')
            measurements += 1
            official = snapshot['shareValidPercent'].get(field)
            if official is None or rounded(value) != rounded(official):
                return False
    sections = observation.get('sectionsPercent')
    if sections is not None:
        if not 0 <= sections <= 100:
            raise ValueError('Percentual de seções inválido')
        measurements += 1
        if rounded(sections) != rounded(snapshot['sections']['countedPercent']):
            return False
    for field, official in (('sectionsCount', 'counted'), ('sectionsTotal', 'total')):
        value = observation.get(field)
        if value is not None:
            if type(value) is not int or value < 0:
                raise ValueError('Contagem de seções inválida')
            measurements += 1
            if value != snapshot['sections'][official]:
                return False
    return measurements > 0


def displayed_interval(observation):
    clock = observation.get('visibleClock')
    if not clock:
        # Publicação pode ser posterior ao dado. Não é substituto do relógio.
        return None
    if observation.get('timePrecision') not in ('minute', 'second'):
        raise ValueError('Precisão do relógio não declarada')
    if observation.get('timezone') != 'America/Sao_Paulo':
        raise ValueError('Fuso do relógio precisa ser resolvido antes do confronto')
    value = observation['observedDate'] + 'T' + clock
    if observation['timePrecision'] == 'minute':
        if len(clock) != 5:
            raise ValueError('HH:mm esperado')
        value += ':00'
    elif len(clock) != 8:
        raise ValueError('HH:mm:ss esperado')
    start = datetime.fromisoformat(value + '-03:00')
    end = start + timedelta(seconds=59 if observation['timePrecision']=='minute' else 0)
    return start, end


def compare(observation, series):
    result = {'observationId': observation['id'], 'scope': observation['scope'],
              'sourceUrl': observation['sourceUrl'], 'source': observation.get('source'),
              'visibleClock': observation.get('visibleClock'),
              'candidateVotes': observation.get('candidateVotes', {}),
              'candidatePercentages': observation.get('candidatePercentages', {}),
              'sectionsPercent': observation.get('sectionsPercent')}
    if observation.get('quality') not in ('confirmed', 'percentages_confirmed_clock_missing'):
        return result | {'status':'not_tested_unconfirmed_reading'}
    result['eligibleForTemporalMatching'] = bool(observation.get('visibleClock')) and observation.get('eligibleForTemporalMatching', True)
    found = [r for r in series.get(observation['scope'].lower(), [])
             if r['eligibleElectionNightObservation'] and matches_numbers(observation,r)]
    found.sort(key=lambda r:(r['generatedAt'],int(r['idg'])))
    if not found:
        return result | {'status':'no_exact_match_in_preserved_series','matchingSnapshots':0}
    result.update(status='numbers_match_preserved_snapshot',matchingSnapshots=len(found),
                  firstMatchingGeneration=found[0]['generatedAt'],
                  lastMatchingGeneration=found[-1]['generatedAt'],
                  uniqueVersionIdentified=len(found)==1,
                  matchingSnapshotIds=[r['idg'] for r in found[:3]] +
                                      ([r['idg'] for r in found[-3:]] if len(found)>3 else []))
    span = displayed_interval(observation)
    if span:
        first,last=span
        generations=[datetime.fromisoformat(r['generatedAt']) for r in found]
        result['displayTimeInterval']={'from':first.isoformat(),'through':last.isoformat()}
        result['displayMinusMatchingGenerationSecondsRange']={
            'minimum':(first-max(generations)).total_seconds(),
            'maximum':(last-min(generations)).total_seconds()}
        result['allMatchingGenerationsAfterDisplayMinute']=min(generations)>last
        result['interpretation']='Range includes clock precision and repeated matching versions; not a measured transmission delay.'
    else:
        result['displayMinusMatchingGenerationSecondsRange']=None
        result['interpretation']='No source clock; article publication time was not used as the data timestamp.'
    return result


def leader_changes(rows):
    """Limites entre observações adjacentes, sem interpolar o instante da virada."""
    eligible = sorted((r for r in rows if r['eligibleElectionNightObservation']),
                      key=lambda r: (r['generatedAt'], int(r['idg'])))
    changes = []
    previous = None
    for row in eligible:
        left, right = row['votes'].get('lula'), row['votes'].get('flavio')
        if left is None or right is None:
            previous = None
            continue
        leader = 'lula' if left > right else 'flavio' if right > left else 'tie'
        if previous is not None and previous[1] != leader:
            before, old = previous
            seconds = (datetime.fromisoformat(row['generatedAt']) -
                       datetime.fromisoformat(before['generatedAt'])).total_seconds()
            changes.append({'lastObservedPreviousLeader': old, 'newObservedLeader': leader,
                            'fromGeneration': before['generatedAt'], 'toGeneration': row['generatedAt'],
                            'fromIdg': before['idg'], 'toIdg': row['idg'],
                            'elapsedSeconds': seconds,
                            'interpretation': 'Change in saved totals between observations; exact crossing instant not observed.'})
        previous = row, leader
    return changes


def summary_counts(observations, results):
    timed = [o for o in observations if o.get('visibleClock') and o.get('sourceVideoId')]
    matched = lambda r: r['status'] == 'numbers_match_preserved_snapshot'
    return {'observations': len(results), 'matched': sum(map(matched, results)),
            'unmatched': sum(r['status'] == 'no_exact_match_in_preserved_series' for r in results),
            'notTested': sum(r['status'] == 'not_tested_unconfirmed_reading' for r in results),
            'withVisibleClock': sum(bool(r.get('eligibleForTemporalMatching')) for r in results),
            'distinctTimedSourceFrames': len({(o['sourceVideoId'], o['sourcePositionSeconds']) for o in timed}),
            'nationalObservations': sum(r['scope'].lower() == 'br' for r in results),
            'nationalMatched': sum(r['scope'].lower() == 'br' and matched(r) for r in results),
            'stateObservations': sum(r['scope'].lower() != 'br' for r in results),
            'stateMatched': sum(r['scope'].lower() != 'br' and matched(r) for r in results)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--series',required=True,type=Path)
    p.add_argument('--summary',required=True,type=Path)
    p.add_argument('--observations',required=True,type=Path)
    a=p.parse_args()
    b=a.series.read_bytes();digest=hashlib.sha256(b).hexdigest()
    summary=json.loads(a.summary.read_text(encoding='utf-8'))
    refs=summary['derivativeArtifacts']
    if not any(r.get('sha256')==digest for r in refs):
        raise ValueError('Série completa não corresponde ao resumo fixado')
    observation_bytes=canonical_observations_bytes(a.observations)
    data=json.loads(b);obs=json.loads(observation_bytes)
    if data['schema']!='alp.temporal-disclosure.v1':raise ValueError('Schema temporal inesperado')
    ids=[r['id'] for r in obs['observations']]
    if len(ids)!=len(set(ids)):raise ValueError('Observação repetida')
    out=[compare(o,data['series']) for o in obs['observations']]
    result={'schema':'alp.display-crosscheck.v1','status':'comparison_executed',
            'provenance':{'seriesSha256':digest,'observationsSha256':hashlib.sha256(observation_bytes).hexdigest(),
                          'observationsHashScope':'Canonical Git UTF-8 bytes with LF; only own observation JSON, not original source captures.',
                          'sourceArchive':summary['provenance']},
            'counts':summary_counts(obs['observations'],out),
            'observations':out,
            'nationalObservedLeadChanges':leader_changes(data['series'].get('br', [])),
            'limits':['Numbers on multiple broadcasters can derive from the same TSE feed; this is display corroboration, not independent vote tabulation.',
                      'No exact match can mean unpreserved version, different rounding/scope, reading error or source conflict; not automatically false.',
                      'Broadcast HH:mm has minute precision. Player position and live-start metadata do not determine wall-clock time.',
                      'Candidate vote increases measure reported totals, not when individual votes were cast.']}
    # ASCII JSON keeps stdout portable through Windows shells; values remain Unicode on decode.
    print(json.dumps(result,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
