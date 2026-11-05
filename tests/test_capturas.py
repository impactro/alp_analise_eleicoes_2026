import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('capturas',Path(__file__).parents[1]/'scripts/conferir_capturas.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CaptureTests(unittest.TestCase):
    def row(self,**kw):
        return dict(uf='ac',situacao='Totalizada',abertura='2026-10-25T06:00:00',encerramento='2026-10-25T16:00:00',
                    bu_lula=40,bu_flavio=60,comparecimento=105,log_votos_depois_17h=4,log_votos_depois_19h=0,
                    log_manual_mesario=2,log_manual_sem_digital=1,log_ja_votou=1)|kw
    def test_local_and_brasilia_cut_differ(self):
        r=m.summarize_captured_rows([self.row()])
        self.assertEqual(r['groups']['local_all_before1701']['flavioPercent'],60)
        self.assertEqual(r['groups']['bsb_brazil_from1716']['sections'],1)
        self.assertEqual(r['groups']['bsb_brazil_before1701'].get('sections',0),0)
    def test_western_am_uses_opening_not_one_state_offset(self):
        r=m.summarize_captured_rows([self.row(uf='am',encerramento='2026-10-25T15:30:00')])
        self.assertEqual(r['groups']['bsb_brazil_from1716']['sections'],1)
    def test_missing_event_not_proven_zero(self):
        r=m.summarize_captured_rows([self.row(log_ja_votou=None)])
        self.assertEqual(r['counts']['missing_log_ja_votou'],1)
    def test_exterior_not_added_to_domestic_logs(self):
        r=m.summarize_captured_rows([self.row(uf='zz')])
        self.assertEqual(r['counts'].get('brazilRows',0),0)
    def test_percentage_drop_does_not_mean_nominal_drop(self):
        rows=[{'id':1,'generated':'a','lula':100,'flavio':100},{'id':2,'generated':'b','lula':200,'flavio':110}]
        self.assertEqual(m.snapshot_series(rows)['nominalDecreases'],{'lula':0,'flavio':0})
        rows[1]['flavio']=90
        self.assertEqual(m.snapshot_series(rows)['nominalDecreases']['flavio'],1)
    def test_repeated_snapshot_rejected(self):
        r={'id':1,'generated':'a','lula':1,'flavio':2}
        with self.assertRaises(ValueError):m.snapshot_series([r,r])

if __name__=='__main__':unittest.main()
