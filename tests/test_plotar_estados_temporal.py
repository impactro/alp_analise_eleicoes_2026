from copy import deepcopy
import unittest

from scripts import plotar_estados_temporal as charts


def point(hour, area='am', eligible=True, conflict=False, votes=1000000):
    return {'area': area, 'idg': hour.replace(':', ''),
            'generatedAt': '2026-10-25T' + hour + '-03:00',
            'eligibleElectionNightObservation': eligible, 'capturePrecedesGeneration': conflict,
            'votes': {'lula': votes, 'flavio': votes}, 'shareValidPercent': {'lula': 50, 'flavio': 50}}


class StateChartTests(unittest.TestCase):
    def test_missing_uf_blocks_instead_of_replacing_another_series(self):
        with self.assertRaisesRegex(ValueError, 'ausente: ba'):
            charts.select_areas({'series': {'am': [point('19:00:00')]}}, ('am', 'ba'))

    def test_historical_initialization_does_not_become_zero_before_first(self):
        earlier = point('17:00:00', eligible=False, votes=0)
        first = point('19:01:54')
        selected = charts.select_areas({'series': {'am': [earlier, first]}}, ('am',))
        self.assertEqual(selected['am'], [first])
        self.assertEqual(selected['am'][0]['generatedAt'], '2026-10-25T19:01:54-03:00')

    def test_gap_splits_series_and_retains_isolated_endpoints(self):
        rows = [point('19:00:00'), point('19:01:00'), point('19:39:00'), point('22:05:57')]
        parts = charts.segments(rows, 300)
        self.assertEqual([len(part) for part in parts], [2, 1, 1])
        self.assertEqual(sum(map(len, parts)), len(rows))

    def test_missing_eligible_records_and_bad_chronology_block(self):
        for row in (point('17:00:00', eligible=False), point('19:00:00', conflict=True)):
            with self.subTest(row=row), self.assertRaises(ValueError):
                charts.select_areas({'series': {'am': [row]}}, ('am',))

    def test_grid_uses_common_absolute_scale_with_no_hidden_normalization(self):
        selected = {'am': [point('19:00:00', votes=1000000)],
                    'sp': [point('19:00:00', area='sp', votes=14000000)]}
        spec = charts.panel_specs(selected, ('am', 'sp'), 'quantidades')
        self.assertEqual(spec['yLimits'], [0, 16])
        self.assertEqual(spec['scale'], 'common_absolute_within_figure')
        self.assertEqual(selected['am'][0]['votes']['lula'], 1000000)

    def test_percentage_scale_is_separate_and_rejects_clipping(self):
        selected = {'am': [point('19:00:00')]}
        self.assertEqual(charts.panel_specs(selected, ('am',), 'percentuais')['yLimits'], [20, 80])
        bad = deepcopy(selected)
        bad['am'][0]['shareValidPercent']['lula'] = 90
        with self.assertRaisesRegex(ValueError, 'fora da escala'):
            charts.panel_specs(bad, ('am',), 'percentuais')


if __name__ == '__main__':
    unittest.main()
