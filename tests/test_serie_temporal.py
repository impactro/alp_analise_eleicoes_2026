"""Testes do método temporal; import padrão a partir da raiz do repositório."""
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts import reconstruir_serie_temporal as m


def row(hour, lula, flavio, identifier, area='br', capture=None, stage='p', day='25/10/2026', counted=1, total=10):
    doc = {'ele': '6258', 't': '2', 'cdabr': area, 'idg': str(identifier),
           'dg': day, 'hg': hour, 'dt': day, 'ht': hour, 'and': stage,
           'v': {'vv': str(lula + flavio)}, 's': {'st': str(counted), 'ts': str(total), 'pstn': str(counted / total * 100)},
           'carg': [{'cd': '1', 'agr': [{'par': [{'cand': [
               {'n': '13', 'vap': str(lula), 'pvapn': str(100 * lula / (lula + flavio))},
               {'n': '22', 'vap': str(flavio), 'pvapn': str(100 * flavio / (lula + flavio))},
           ]}]}]}]}
    naive = m.source_clock(day, hour).isoformat()
    manifest = {'abr': area, 'idg': str(identifier), 'gerado': naive,
                'lido_em': capture or naive + '-03:00', 'sha256': 'a' * 64,
                'bytes': 123, 'url': 'https://example.org/capture'}
    return m.snapshot(doc, manifest, area + '/' + str(identifier) + '.json', 'a' * 64)


class TemporalTests(unittest.TestCase):
    def test_json_writer_produces_portable_utf8_lf_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'derived.json'
            m.write_json(path, {'texto': 'ação', 'numero': 1})
            expected = b'{\n  "texto": "a\xc3\xa7\xc3\xa3o",\n  "numero": 1\n}\n'
            self.assertEqual(path.read_bytes(), expected)
            self.assertNotIn(b'\r', path.read_bytes())

    def test_before_first_is_missing_not_zero(self):
        first = row('17:06:31', 193574, 142169, 1)
        self.assertIsNone(m.asof([first], '2026-10-25T17:00:00-03:00'))

    def test_asof_never_anticipates_future_update(self):
        first = row('19:00:00', 100, 200, 1)
        later = row('19:05:00', 900, 700, 2)
        self.assertEqual(m.asof([first, later], '2026-10-25T19:04:59-03:00')['idg'], '1')
        self.assertEqual(m.asof([first, later], '2026-10-25T19:05:00-03:00')['idg'], '2')

    def test_custom_targets_keep_stale_sample_without_anticipating_update(self):
        a = row('19:01:56', 271370, 217312, 1)
        b = row('19:20:00', 1000000, 900000, 2)
        series = {'br': [a, b], 'zz': []}
        result = m.build_report(series, {}, targets=('19:10:00', '19:20:00', '19:30:00'))
        anchors = result['anchors']
        self.assertEqual(len(anchors), 3)
        self.assertEqual(anchors[0]['national']['idg'], '1')
        self.assertEqual(anchors[0]['generationAgeSeconds'], 484)
        self.assertTrue(anchors[0]['nationalSnapshotStale'])
        self.assertEqual(anchors[1]['national']['idg'], '2')
        self.assertFalse(anchors[1]['nationalSnapshotStale'])
        self.assertTrue(anchors[1]['nationalRateFromPreviousAnchor']['notContinuous'])
        self.assertEqual(anchors[2]['nationalRateFromPreviousAnchor']['status'], 'no_new_observation')
        default_result = m.build_report(series, {})
        self.assertEqual(len(default_result['anchors']), 15)
        self.assertEqual(default_result['anchors'][0]['targetAtBrasilia'], '2026-10-25T16:00:00-03:00')
        self.assertEqual(default_result['anchors'][-1]['targetAtBrasilia'], '2026-10-25T23:27:02-03:00')

    def test_custom_targets_reject_wrong_order_or_duplicates(self):
        series = {'br': [row('19:00:00', 100, 100, 1), row('19:20:00', 200, 300, 2)], 'zz': []}
        for targets in (('19:20:00', '19:10:00'), ('19:10:00', '19:10:00')):
            with self.subTest(targets=targets), self.assertRaisesRegex(ValueError, 'únicos e crescentes'):
                m.build_report(series, {}, targets=targets)

    def test_generation_does_not_prove_capture_availability(self):
        first = row('17:06:31', 193574, 142169, 1, capture='2026-10-25T17:20:42-03:00')
        target = '2026-10-25T17:10:00-03:00'
        self.assertIsNotNone(m.asof([first], target))
        self.assertIsNone(m.asof([first], target, 'capturedAt'))

    def test_capture_preceding_generation_is_exposed_not_repaired(self):
        point = row('23:26:57', 200154, 171497, 1, area='zz', capture='2026-10-25T22:23:09-03:00')
        self.assertEqual(point['captureMinusGenerationSeconds'], -3828)
        self.assertTrue(point['capturePrecedesGeneration'])
        self.assertEqual(point['lido_em'], '2026-10-25T22:23:09-03:00')
        self.assertIsNone(m.asof([point], '2026-10-25T22:30:00-03:00', 'capturedAt'))

    def test_lacuna_6895_seconds_flagged_without_interpolation(self):
        a = row('17:07:01', 221227, 168920, 1)
        b = row('19:01:56', 271370, 217312, 2)
        rate = m.window_rate(a, b, [a, b], 300)
        self.assertEqual(rate['unobservedGaps'][0]['seconds'], 6895)
        self.assertTrue(rate['notContinuous'])
        self.assertAlmostEqual(rate['votesPerMinute']['lula'], 50143 / (6895 / 60))

    def test_same_saved_version_is_not_zero_growth(self):
        a = row('17:07:01', 100, 100, 1)
        rate = m.window_rate(a, a, [a], 300)
        self.assertEqual(rate['status'], 'no_new_observation')
        self.assertIsNone(rate['votesPerMinute'])

    def test_votes_increase_while_share_decreases(self):
        a = row('19:00:00', 100, 100, 1)
        b = row('19:02:00', 200, 150, 2)
        rate = m.window_rate(a, b, [a, b], 300)
        self.assertEqual(rate['votesPerMinute']['flavio'], 25)
        self.assertLess(rate['sharePercentagePointsPerMinute']['flavio'], 0)

    def test_clock_without_offset_rejected(self):
        with self.assertRaisesRegex(ValueError, 'fuso'):
            m.parse_instant('2026-10-25T19:00:00')

    def test_uf_clock_not_silently_assigned_brasilia(self):
        point = row('19:00:00', 100, 100, 1, area='am')
        self.assertEqual(point['generatedAt'], '2026-10-25T19:00:00-03:00')
        self.assertIsNone(point['totalizedAtBrasilia'])
        self.assertEqual(point['totalizedLocalClock'], '2026-10-25T19:00:00')

    def test_region_reports_stale_missing_and_partial_uf(self):
        series = {'am': [row('19:00:00', 100, 200, 1, area='am')]}
        region = m.region_asof(series, ('am', 'pa'), '2026-10-25T19:10:00-03:00', 300)
        self.assertEqual(region['missingUfs'], ['pa'])
        self.assertEqual(region['staleUfs'], ['am'])
        self.assertEqual(region['incompleteSectionUfs'], ['am'])
        self.assertEqual(region['maxGenerationAgeSeconds'], 600)
        self.assertFalse(region['coverageComplete'])
        self.assertEqual(region['votes']['lula'], 100)

    def test_not_started_historical_zero_is_not_night_observation(self):
        point = row('17:00:00', 1, 1, 1, area='ac', stage='n', day='13/10/2026')
        result = m.region_asof({'ac': [point]}, ('ac',), '2026-10-25T17:00:00-03:00', 300)
        self.assertEqual(result['missingUfs'], ['ac'])
        self.assertIsNone(result['votes'])

    def test_changing_coverage_does_not_create_rate(self):
        incomplete = {'coverageComplete': False}
        complete = {'coverageComplete': True}
        self.assertIsNone(m.region_rate(incomplete, complete, 30)['votesPerMinute'])

    def test_region_fresh_endpoints_do_not_hide_gap_inside_window(self):
        a = row('19:00:00', 100, 100, 1, area='am')
        b = row('19:10:00', 200, 300, 2, area='am')
        series = {'am': [a, b]}
        earlier = m.region_asof(series, ('am',), a['generatedAt'], 300)
        later = m.region_asof(series, ('am',), b['generatedAt'], 300)
        self.assertFalse(earlier['staleUfs'] or later['staleUfs'])
        result = m.region_rate(earlier, later, 10, ['am'])
        self.assertTrue(result['notContinuous'])
        self.assertEqual(result['unobservedGapUfs'], ['am'])

    def test_last_partial_is_not_100_percent(self):
        point = row('22:00:00', 100, 100, 1, area='am', counted=9999, total=10000)
        self.assertFalse(point['sections']['complete'])
        self.assertEqual(point['sections']['countedPercent'], 99.99)

    def test_missing_candidate_is_not_zero(self):
        # O parser também protege esse caso antes de validar o total.
        original = row('19:00:00', 100, 100, 1)
        self.assertEqual(original['votes']['flavio'], 100)
        doc = {'ele': '6258', 't': '2', 'cdabr': 'br', 'idg': '1',
               'dg': '25/10/2026', 'hg': '19:00:00', 'dt': '', 'ht': '',
               'carg': [{'cd': '1', 'agr': []}]}
        manifest = {'abr': 'br', 'idg': '1', 'gerado': '2026-10-25T19:00:00',
                    'lido_em': '2026-10-25T19:00:01-03:00'}
        with self.assertRaisesRegex(ValueError, 'ausente'):
            m.snapshot(doc, manifest, 'br/1.json', 'a' * 64)

    def test_manifest_hash_mismatch_fails_without_newline_normalization(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            captures = root / 'captures'
            (captures / 'br').mkdir(parents=True)
            (captures / 'br/1.json').write_bytes(b'{}\r\n')
            manifest = root / 'manifest.jsonl'
            manifest.write_text(json.dumps({'abr': 'br', 'idg': '1',
                                            'sha256': m.digest_bytes(b'{}\n'), 'bytes': 3}), encoding='utf-8')
            archive = root / 'author.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('repo/dados/copias/noite/versoes-tse/br/1.json', b'{}\r\n')
            with self.assertRaisesRegex(ValueError, 'divergem do manifesto'):
                m.read_verified(captures, manifest, archive, m.sha256(archive))

    def test_archive_hash_is_checked_before_reading_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'wrong.zip'
            path.write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError, 'Hash ZIP'):
                m.read_verified(Path(folder), Path(folder) / 'absent', path, '0' * 64)


if __name__ == '__main__':
    unittest.main()
