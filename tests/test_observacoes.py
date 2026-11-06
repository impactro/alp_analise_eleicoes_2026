import importlib.util
from pathlib import Path
import unittest
import tempfile
spec=importlib.util.spec_from_file_location('observacoes',Path(__file__).parents[1]/'scripts/confrontar_observacoes.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class ObservationTests(unittest.TestCase):
    def test_own_observation_hash_portable_across_checkout_line_endings(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'observations.json'
            p.write_bytes(b'{\r\n  "observations": []\r\n}\r\n')
            self.assertEqual(m.canonical_observations_bytes(p),b'{\n  "observations": []\n}\n')
    def snapshot(self,**kw):
        return dict(area='br',eligibleElectionNightObservation=True,idg='1',
                    generatedAt='2026-10-25T19:21:46-03:00',votes={'lula':60,'flavio':40},
                    shareValidPercent={'lula':60.0,'flavio':40.0},sections={'countedPercent':2.78})|kw
    def observation(self,**kw):
        return dict(id='cnn1',sourceUrl='https://example.test/video?t=10',scope='BR',quality='confirmed',
                    candidateVotes={'lula':60,'flavio':40},candidatePercentages={'lula':60,'flavio':40},
                    sectionsPercent=2.78,observedDate='2026-10-25',visibleClock='19:22',timePrecision='minute',
                    timezone='America/Sao_Paulo')|kw
    def test_exact_counts_match_and_minute_range_not_exact_delay(self):
        r=m.compare(self.observation(),{'br':[self.snapshot()]})
        self.assertEqual(r['status'],'numbers_match_preserved_snapshot')
        self.assertEqual(r['displayMinusMatchingGenerationSecondsRange'],{'minimum':14,'maximum':73})
    def test_different_region_not_same_scope(self):
        self.assertFalse(m.matches_numbers(self.observation(scope='MG'),self.snapshot()))
    def test_percentage_cannot_rescue_wrong_integer(self):
        self.assertFalse(m.matches_numbers(self.observation(candidateVotes={'lula':61,'flavio':40}),self.snapshot()))
    def test_absent_clock_does_not_use_article_publication(self):
        r=m.compare(self.observation(visibleClock=None,publishedAt='2026-10-25T19:56:00-03:00'),{'br':[self.snapshot()]})
        self.assertIsNone(r['displayMinusMatchingGenerationSecondsRange'])
    def test_repeated_numbers_are_ambiguous_versions(self):
        rows=[self.snapshot(),self.snapshot(idg='2',generatedAt='2026-10-25T19:22:01-03:00')]
        r=m.compare(self.observation(),{'br':rows})
        self.assertEqual(r['matchingSnapshots'],2)
        self.assertFalse(r['uniqueVersionIdentified'])
    def test_no_match_is_not_automatically_false(self):
        r=m.compare(self.observation(),{'br':[]})
        self.assertEqual(r['status'],'no_exact_match_in_preserved_series')
    def test_unconfirmed_reading_not_promoted(self):
        self.assertEqual(m.compare(self.observation(quality='illegible'),{'br':[self.snapshot()]})['status'],
                         'not_tested_unconfirmed_reading')
    def test_percent_only_does_not_create_votes(self):
        o=self.observation(candidateVotes={'lula':None,'flavio':None})
        r=m.compare(o,{'br':[self.snapshot()]})
        self.assertEqual(r['status'],'numbers_match_preserved_snapshot')
        self.assertIsNone(r['candidateVotes']['lula'])
    def test_legible_percentages_without_clock_match_numbers_only(self):
        o=self.observation(candidateVotes={'lula':None,'flavio':None},visibleClock=None,
                           quality='percentages_confirmed_clock_missing',eligibleForTemporalMatching=False)
        r=m.compare(o,{'br':[self.snapshot()]})
        self.assertEqual(r['status'],'numbers_match_preserved_snapshot')
        self.assertFalse(r['eligibleForTemporalMatching'])
        self.assertIsNone(r['displayMinusMatchingGenerationSecondsRange'])
    def test_missing_measurement_not_zero_or_match(self):
        self.assertFalse(m.matches_numbers(self.observation(candidateVotes={},candidatePercentages={},sectionsPercent=None),self.snapshot()))
    def test_timezone_and_approximate_count_rejected(self):
        with self.assertRaises(ValueError):m.displayed_interval(self.observation(timezone='unknown'))
        with self.assertRaises(ValueError):m.matches_numbers(self.observation(candidateVotes={'lula':60.0}),self.snapshot())
    def test_section_count_is_checked_even_if_percent_matches(self):
        s=self.snapshot(sections={'counted':1225,'total':499248,'countedPercent':2.78})
        self.assertFalse(m.matches_numbers(self.observation(sectionsCount=1226),s))
    def test_lead_change_is_bracketed_not_interpolated(self):
        rows=[self.snapshot(),self.snapshot(idg='2',generatedAt='2026-10-25T19:22:26-03:00',
                                          votes={'lula':65,'flavio':70})]
        r=m.leader_changes(rows)
        self.assertEqual(len(r),1)
        self.assertEqual(r[0]['newObservedLeader'],'flavio')
        self.assertEqual(r[0]['elapsedSeconds'],40)
    def test_missing_candidate_does_not_bridge_leader_change(self):
        rows=[self.snapshot(),self.snapshot(idg='2',votes={'lula':None,'flavio':40}),
              self.snapshot(idg='3',votes={'lula':30,'flavio':70})]
        self.assertEqual(m.leader_changes(rows),[])
    def test_one_frame_with_national_and_state_panels_is_not_two_frames(self):
        observations=[self.observation(sourceVideoId='one',sourcePositionSeconds=10),
                      self.observation(scope='MG',sourceVideoId='one',sourcePositionSeconds=10)]
        results=[m.compare(o,{'br':[self.snapshot()],'mg':[]}) for o in observations]
        c=m.summary_counts(observations,results)
        self.assertEqual(c['distinctTimedSourceFrames'],1)
        self.assertEqual(c['withVisibleClock'],2)
        self.assertEqual(c['stateMatched'],0)


if __name__=='__main__':unittest.main()
