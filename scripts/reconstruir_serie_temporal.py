"""Reconstrói capturas históricas preservadas, sem executar código do autor.

Somente biblioteca padrão. O eixo é geração do JSON, não horário do voto.
"""
import argparse
from bisect import bisect_right
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import zipfile

COMMIT = '4a12ed014cf7927df24226f900450db7fe5b1a22'
REPOSITORY = 'https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026'
ARCHIVE_SHA256 = 'f3a1378864bcc7085f24943c099afe649d7de7e8d304ffe809833936fac0a9b1'
# 25/10/2026: Brasília usa UTC-03. Não depende de tzdata no Windows.
BRASILIA = timezone(timedelta(hours=-3), 'America/Sao_Paulo')
DATE = '2026-10-25'
REGIONS = {
    'Norte': ('ac', 'am', 'ap', 'pa', 'ro', 'rr', 'to'),
    'Nordeste': ('al', 'ba', 'ce', 'ma', 'pb', 'pe', 'pi', 'rn', 'se'),
    'Centro-Oeste': ('df', 'go', 'ms', 'mt'),
    'Sudeste': ('es', 'mg', 'rj', 'sp'),
    'Sul': ('pr', 'rs', 'sc'),
}
DEFAULT_TARGETS = ('16:00:00', '17:00:00', '17:06:31', '17:07:01', '18:00:00',
                   '19:01:56', '19:04:36', '19:30:00', '20:00:00', '20:30:00',
                   '21:00:00', '21:30:00', '22:00:00', '22:30:00', '23:27:02')


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def logical_hash(value):
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode('utf-8'))


def parse_instant(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError('Instante sem fuso explícito')
    return parsed


def source_clock(date, hour):
    if not date and not hour:
        return None
    if not date or not hour:
        raise ValueError('Relógio incompleto')
    return datetime.strptime(date + ' ' + hour, '%d/%m/%Y %H:%M:%S')


def number(value):
    return float(value.replace(',', '.'))


def snapshot(doc, manifest, relative_path, file_hash):
    """Mantém os relógios separados; dt/ht de UF não ganha fuso inventado."""
    area = manifest['abr']
    if doc['t'] != '2' or doc['ele'] != '6258' or doc['cdabr'].lower() != area:
        raise ValueError('Eleição/turno/abrangência divergente')
    if str(doc['idg']) != str(manifest['idg']):
        raise ValueError('Identificador divergente')
    generated_raw = source_clock(doc['dg'], doc['hg'])
    if generated_raw.isoformat() != manifest['gerado']:
        raise ValueError('Geração JSON/manifesto divergente')
    generated = generated_raw.replace(tzinfo=BRASILIA)
    captured = parse_instant(manifest['lido_em']).astimezone(BRASILIA)
    tally_raw = source_clock(doc['dt'], doc['ht'])
    cargos = [cargo for cargo in doc['carg'] if cargo['cd'] == '1']
    if len(cargos) != 1:
        raise ValueError('Cargo presidencial ausente/duplicado')
    votes = {}
    declared_shares = {}
    for group in cargos[0]['agr']:
        for party in group['par']:
            for candidate in party['cand']:
                key = candidate['n']
                if key in votes:
                    raise ValueError('Candidato duplicado')
                votes[key] = int(candidate['vap'])
                declared_shares[key] = number(candidate['pvapn'])
    if not {'13', '22'} <= votes.keys():
        raise ValueError('Candidato ausente não é zero')
    if min(votes.values()) < 0:
        raise ValueError('Votos negativos')
    valid = int(doc['v']['vv'])
    if sum(votes.values()) != valid:
        raise ValueError('Votos de candidatos não fecham com votos válidos')
    total_sections, counted_sections = int(doc['s']['ts']), int(doc['s']['st'])
    if not 0 <= counted_sections <= total_sections:
        raise ValueError('Seções incompatíveis')
    stage = doc['and']
    eligible = generated.date().isoformat() == DATE and stage != 'n'
    return {
        'area': area, 'idg': str(doc['idg']), 'dg': doc['dg'], 'hg': doc['hg'],
        'dt': doc['dt'], 'ht': doc['ht'], 'generatedAt': generated.isoformat(),
        'totalizedLocalClock': tally_raw.isoformat() if tally_raw else None,
        'totalizedAtBrasilia': tally_raw.replace(tzinfo=BRASILIA).isoformat()
        if tally_raw and area == 'br' else None,
        'totalizationTimezoneBasis': 'Brasilia_assumption_national' if area == 'br'
        else 'not_encoded_in_source_unresolved',
        'lido_em': manifest['lido_em'], 'capturedAt': captured.isoformat(),
        'eligibleElectionNightObservation': eligible,
        'captureMinusGenerationSeconds': (captured - generated).total_seconds(),
        'capturePrecedesGeneration': captured < generated,
        'votes': {'lula': votes['13'], 'flavio': votes['22']}, 'validVotes': valid,
        'shareValidPercent': {'lula': 100 * votes['13'] / valid if valid else None,
                              'flavio': 100 * votes['22'] / valid if valid else None},
        'sourceShareValidPercent': {'lula': declared_shares['13'], 'flavio': declared_shares['22']},
        'sections': {'counted': counted_sections, 'total': total_sections,
                     'countedPercent': 100 * counted_sections / total_sections if total_sections else None,
                     'sourceCountedPercent': number(doc['s']['pstn']),
                     'complete': counted_sections == total_sections},
        'stage': stage,
        'source': {'path': relative_path, 'sha256': file_hash,
                   'manifestOriginalPath': manifest.get('arquivo'),
                   'manifestSha256': manifest['sha256'], 'manifestBytes': manifest['bytes'],
                   'url': manifest['url'], 'repositoryCommit': COMMIT},
    }


def read_verified(captures_root, manifest_path, archive_path, expected_archive_hash):
    """Exige identidade de bytes nos arquivos, no manifesto e no ZIP fixado."""
    archive_hash = sha256(archive_path)
    if archive_hash != expected_archive_hash.lower():
        raise ValueError('Hash ZIP do autor divergente')
    entries = {}
    for line in Path(manifest_path).read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        key = (entry['abr'], str(entry['idg']))
        if key in entries:
            raise ValueError('Manifesto com chave duplicada')
        entries[key] = entry
    series = {}
    pins = []
    with zipfile.ZipFile(archive_path) as archive:
        members = {}
        for name in archive.namelist():
            marker = '/dados/copias/noite/versoes-tse/'
            if marker in name and name.endswith('.json'):
                relative = name.split(marker, 1)[1]
                if relative in members:
                    raise ValueError('Membro ZIP duplicado')
                members[relative] = name
        for path in sorted(Path(captures_root).glob('*/*.json')):
            area, identifier = path.parent.name, path.stem
            entry = entries.get((area, identifier))
            if entry is None:
                raise ValueError('Captura sem manifesto')
            raw = path.read_bytes()
            file_hash = digest_bytes(raw)
            if file_hash != entry['sha256'] or len(raw) != entry['bytes']:
                raise ValueError('Bytes/hash da captura divergem do manifesto: ' + area + '/' + path.name)
            relative = area + '/' + path.name
            if relative not in members or archive.read(members[relative]) != raw:
                raise ValueError('Bytes da captura divergem do ZIP fixado: ' + relative)
            row = snapshot(json.loads(raw), entry, 'dados/copias/noite/versoes-tse/' + relative, file_hash)
            series.setdefault(area, []).append(row)
            pins.append({'path': row['source']['path'], 'sha256': file_hash})
    if len(pins) != len(entries) or len(pins) != len(members):
        raise ValueError('Cobertura arquivos/manifesto/ZIP divergente')
    expected_areas = {'br', 'zz'} | {uf for ufs in REGIONS.values() for uf in ufs}
    if set(series) != expected_areas:
        raise ValueError('Abrangências incompletas/inesperadas')
    for rows in series.values():
        rows.sort(key=lambda row: (row['generatedAt'], int(row['idg'])))
        if len({row['idg'] for row in rows}) != len(rows):
            raise ValueError('Versão repetida')
    return series, {
        'repository': REPOSITORY, 'repositoryCommit': COMMIT,
        'archiveSha256': archive_hash, 'archiveBytes': Path(archive_path).stat().st_size,
        'manifestSha256': sha256(manifest_path), 'files': len(pins),
        'logicalPathHashSetSha256': logical_hash(pins),
        'verification': {'exactManifestBytes': len(pins), 'exactPinnedArchiveBytes': len(pins),
                         'lineEndingNormalizationUsed': False},
    }


def eligible_rows(rows):
    return [row for row in rows if row['eligibleElectionNightObservation']]


def asof(rows, target, clock='generatedAt'):
    """Último instante <= alvo; nunca escolhe atualização futura."""
    target = parse_instant(target) if isinstance(target, str) else target
    ordered = sorted(eligible_rows(rows), key=lambda row: (parse_instant(row[clock]), int(row['idg'])))
    if clock == 'capturedAt':
        ordered = [row for row in ordered if not row['capturePrecedesGeneration']]
    times = [parse_instant(row[clock]) for row in ordered]
    index = bisect_right(times, target) - 1
    return ordered[index] if index >= 0 else None


def gap_list(rows, max_gap_seconds):
    rows = eligible_rows(rows)
    result = []
    for previous, current in zip(rows, rows[1:]):
        seconds = (parse_instant(current['generatedAt']) - parse_instant(previous['generatedAt'])).total_seconds()
        if seconds > max_gap_seconds:
            result.append({'from': previous['generatedAt'], 'to': current['generatedAt'],
                           'seconds': seconds, 'fromIdg': previous['idg'], 'toIdg': current['idg']})
    return result


def window_rate(previous, current, rows, max_gap_seconds):
    if previous is None or current is None:
        return {'status': 'unobserved_endpoint', 'notContinuous': True, 'votesPerMinute': None}
    elapsed = (parse_instant(current['generatedAt']) - parse_instant(previous['generatedAt'])).total_seconds()
    if elapsed <= 0:
        return {'status': 'no_new_observation', 'notContinuous': True, 'votesPerMinute': None}
    minutes = elapsed / 60
    gaps = [gap for gap in gap_list(rows, max_gap_seconds)
            if gap['from'] >= previous['generatedAt'] and gap['to'] <= current['generatedAt']]
    delta = {candidate: current['votes'][candidate] - previous['votes'][candidate]
             for candidate in ('lula', 'flavio')}
    return {
        'status': 'observed_endpoints', 'fromIdg': previous['idg'], 'toIdg': current['idg'],
        'from': previous['generatedAt'], 'to': current['generatedAt'], 'elapsedMinutes': minutes,
        'deltaVotes': delta, 'votesPerMinute': {candidate: delta[candidate] / minutes for candidate in delta},
        'sharePercentagePointsPerMinute': {
            candidate: (current['shareValidPercent'][candidate] - previous['shareValidPercent'][candidate]) / minutes
            if current['shareValidPercent'][candidate] is not None and previous['shareValidPercent'][candidate] is not None
            else None for candidate in delta},
        'notContinuous': bool(gaps), 'unobservedGaps': gaps,
        'interpretation': 'Mean disclosure increment between saved generation timestamps; no interpolation inside gaps.',
    }


def region_asof(series, ufs, target, max_stale_seconds):
    target_dt = parse_instant(target)
    selected = {uf: asof(series.get(uf, []), target_dt) for uf in ufs}
    missing = [uf for uf, row in selected.items() if row is None]
    present = {uf: row for uf, row in selected.items() if row is not None}
    ages = {uf: (target_dt - parse_instant(row['generatedAt'])).total_seconds() for uf, row in present.items()}
    stale = [uf for uf, age in ages.items() if age > max_stale_seconds]
    totals = {candidate: sum(row['votes'][candidate] for row in present.values())
              for candidate in ('lula', 'flavio')} if present else None
    valid = sum(row['validVotes'] for row in present.values()) if present else None
    return {
        'expectedUfCount': len(ufs), 'observedUfCount': len(present), 'missingUfs': missing,
        'staleUfs': stale, 'coverageComplete': not missing, 'asynchronous': True,
        'oldestGenerationAt': min((row['generatedAt'] for row in present.values()), default=None),
        'newestGenerationAt': max((row['generatedAt'] for row in present.values()), default=None),
        'maxGenerationAgeSeconds': max(ages.values(), default=None),
        'captureAfterTargetUfs': [uf for uf, row in present.items() if parse_instant(row['capturedAt']) > target_dt],
        'votes': totals, 'validVotes': valid,
        'shareValidPercent': {candidate: 100 * totals[candidate] / valid if valid else None
                              for candidate in ('lula', 'flavio')},
        'incompleteSectionUfs': [uf for uf, row in present.items() if not row['sections']['complete']],
        'sourceSetSha256': logical_hash([{'uf': uf, 'idg': row['idg'], 'sha256': row['source']['sha256']}
                                        for uf, row in sorted(present.items())]),
    }


def region_rate(previous, current, minutes, unobserved_gap_ufs=()):
    if not previous['coverageComplete'] or not current['coverageComplete']:
        return {'status': 'incomplete_coverage', 'notContinuous': True, 'votesPerMinute': None}
    return {'status': 'asynchronous_asof_sum',
            'notContinuous': bool(previous['staleUfs'] or current['staleUfs'] or unobserved_gap_ufs),
            'unobservedGapUfs': list(unobserved_gap_ufs),
            'elapsedTargetMinutes': minutes,
            'deltaVotes': {candidate: current['votes'][candidate] - previous['votes'][candidate]
                           for candidate in ('lula', 'flavio')},
            'votesPerMinute': {candidate: (current['votes'][candidate] - previous['votes'][candidate]) / minutes
                               for candidate in ('lula', 'flavio')},
            'sharePercentagePointsPerMinute': {
                candidate: (current['shareValidPercent'][candidate] - previous['shareValidPercent'][candidate]) / minutes
                if current['shareValidPercent'][candidate] is not None and previous['shareValidPercent'][candidate] is not None
                else None for candidate in ('lula', 'flavio')}}


def build_report(series, provenance, targets=DEFAULT_TARGETS, max_gap_seconds=300):
    national = eligible_rows(series['br'])
    if len(national) < 2:
        raise ValueError('Série nacional insuficiente')
    target_instants = [DATE + 'T' + value + '-03:00' for value in targets]
    if target_instants != sorted(set(target_instants)):
        raise ValueError('Alvos devem ser únicos e crescentes')
    anchors = []
    for target in target_instants:
        row = asof(national, target)
        captured = asof(national, target, 'capturedAt')
        regional = {region: region_asof(series, ufs, target, max_gap_seconds)
                    for region, ufs in REGIONS.items()}
        domestic = region_asof(series, tuple(uf for ufs in REGIONS.values() for uf in ufs), target, max_gap_seconds)
        exterior = asof(series['zz'], target)
        comparator = None
        if domestic['coverageComplete'] and exterior is not None and row is not None:
            comparator = {'meaning': 'Mixed-vintage UF+exterior sums minus national; not a synchronous reconciliation.',
                          'nationalIdg': row['idg'], 'exteriorIdg': exterior['idg'],
                          'exteriorGeneratedAt': exterior['generatedAt'],
                          'exteriorSourceSha256': exterior['source']['sha256'],
                          'exteriorCapturePrecedesGeneration': exterior['capturePrecedesGeneration'],
                          'sumMinusNationalVotes': {candidate: domestic['votes'][candidate] + exterior['votes'][candidate] - row['votes'][candidate]
                                                   for candidate in ('lula', 'flavio')}}
        item = {'targetAtBrasilia': target, 'national': row,
                'generationAgeSeconds': (parse_instant(target) - parse_instant(row['generatedAt'])).total_seconds() if row else None,
                'nationalSnapshotStale': (parse_instant(target) - parse_instant(row['generatedAt'])).total_seconds() > max_gap_seconds if row else None,
                'nationalCapturedAfterTarget': parse_instant(row['capturedAt']) > parse_instant(target) if row else None,
                'status': 'asof_generation_observation' if row else 'no_observation_at_or_before_target',
                'latestActuallyCapturedNational': {'idg': captured['idg'], 'generatedAt': captured['generatedAt'],
                                                   'capturedAt': captured['capturedAt'], 'votes': captured['votes'],
                                                   'source': captured['source']} if captured else None,
                'regions': regional, 'domesticCoverage': domestic, 'nationalComparator': comparator}
        if anchors:
            item['nationalRateFromPreviousAnchor'] = window_rate(anchors[-1]['national'], row, national, max_gap_seconds)
            minutes = (parse_instant(target) - parse_instant(anchors[-1]['targetAtBrasilia'])).total_seconds() / 60
            for region, ufs in REGIONS.items():
                gap_ufs = []
                for uf in ufs:
                    a = asof(series.get(uf, []), anchors[-1]['targetAtBrasilia'])
                    b = asof(series.get(uf, []), target)
                    if a and b and window_rate(a, b, series[uf], max_gap_seconds).get('unobservedGaps'):
                        gap_ufs.append(uf)
                regional[region]['rateFromPreviousAnchor'] = region_rate(
                    anchors[-1]['regions'][region], regional[region], minutes, gap_ufs)
        anchors.append(item)
    statistics = {}
    for area, all_rows in sorted(series.items()):
        rows = eligible_rows(all_rows)
        statistics[area] = {'savedVersions': len(all_rows), 'electionNightVersions': len(rows),
                            'excludedNotStartedOrOtherDate': len(all_rows) - len(rows),
                            'first': {'idg': rows[0]['idg'], 'generatedAt': rows[0]['generatedAt'], 'votes': rows[0]['votes']} if rows else None,
                            'last': {'idg': rows[-1]['idg'], 'generatedAt': rows[-1]['generatedAt'], 'votes': rows[-1]['votes'], 'sections': rows[-1]['sections']} if rows else None,
                            'nominalDecreases': {candidate: sum(b['votes'][candidate] < a['votes'][candidate]
                                                              for a, b in zip(rows, rows[1:])) for candidate in ('lula', 'flavio')},
                            'generationGapsOverThreshold': gap_list(rows, max_gap_seconds)}
    return {'schema': 'alp.temporal-disclosure.v1', 'electionDate': DATE,
            'status': 'recomputed_from_author_preserved_snapshots', 'provenance': provenance,
            'timeBasis': {'name': 'America/Sao_Paulo', 'offsetOnElectionDate': '-03:00',
                          'axis': 'dg/hg JSON generation interpreted as Brasilia; source does not encode its offset',
                          'capture': 'lido_em has explicit offset; generation is not observed network availability',
                          'totalization': 'dt/ht preserved independently; UF timezone unresolved, never converted implicitly'},
            'method': {'asof': 'last eligible generation <= target, no future update or interpolation',
                       'gapAndStalenessThresholdSeconds': max_gap_seconds,
                       'percentDenominator': 'validVotes in each saved scope, independent of nominal count',
                       'rates': 'delta votes / elapsed generation minutes; percentage points are separate',
                       'regions': 'asof sums of asynchronous UF records; exterior kept separate',
                       'angle': 'Not reported: geometric angle changes with chart scales. Compare votes/minute instead.'},
            'clockDiagnostics': {
                'capturePrecedesGeneration': [
                    {'area': row['area'], 'idg': row['idg'], 'generatedAt': row['generatedAt'],
                     'lido_em': row['lido_em'], 'differenceSeconds': row['captureMinusGenerationSeconds'],
                     'sourceSha256': row['source']['sha256']}
                    for rows in series.values() for row in rows if row['capturePrecedesGeneration']],
                'handling': 'Preserve original values; exclude impossible chronology from capturedAt asof; generation axis remains attributed, not verified publication time.'},
            'seriesStatistics': statistics, 'anchors': anchors,
            'limits': ['No observation before the first saved version: not zero votes.',
                       'Saved generation timestamps do not establish when votes were cast, received, or first visible to the public.',
                       'A long gap is unobserved, not a flat count or a reconstructed straight line.',
                       'Monotonic saved totals do not establish electoral integrity or any individual vote transfer.',
                       'Last UF capture may be partial even when the national last capture is complete.',
                       'Region rates describe changing mixed-vintage saved totals; unavailable/stale UF records limit comparison.',
                       'Source acquisition is attributed to the author and has not been repeated independently.']}


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures-root', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--author-archive', type=Path, required=True)
    parser.add_argument('--author-archive-sha256', default=ARCHIVE_SHA256)
    parser.add_argument('--full-output-dir', type=Path, required=True)
    parser.add_argument('--summary-output', type=Path, required=True)
    parser.add_argument('--max-gap-seconds', type=int, default=300)
    parser.add_argument('--targets', nargs='+', default=DEFAULT_TARGETS, metavar='HH:mm:ss',
                        help='Horários-alvo de Brasília, únicos e crescentes; omitir preserva as 15 âncoras padrão.')
    args = parser.parse_args()
    if args.max_gap_seconds <= 0:
        parser.error('--max-gap-seconds deve ser positivo')
    series, provenance = read_verified(args.captures_root, args.manifest,
                                       args.author_archive, args.author_archive_sha256)
    report = build_report(series, provenance, targets=args.targets, max_gap_seconds=args.max_gap_seconds)
    full_series_path = args.full_output_dir / 'series-completas.json'
    intervals_path = args.full_output_dir / 'intervalos-nacionais.json'
    write_json(full_series_path, {
        'schema': report['schema'], 'provenance': provenance, 'timeBasis': report['timeBasis'], 'series': series})
    intervals = [window_rate(a, b, eligible_rows(series['br']), args.max_gap_seconds)
                 for a, b in zip(eligible_rows(series['br']), eligible_rows(series['br'])[1:])]
    write_json(intervals_path, intervals)
    report['derivativeArtifacts'] = [{'name': path.name, 'sha256': sha256(path), 'bytes': path.stat().st_size}
                                     for path in (full_series_path, intervals_path)]
    write_json(args.summary_output, report)
    print(json.dumps({'filesVerified': provenance['files'], 'nationalVersions': len(series['br']),
                      'anchors': len(report['anchors']), 'summarySha256': sha256(args.summary_output)}, indent=2))


if __name__ == '__main__':
    main()
