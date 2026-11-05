import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('municipios', Path(__file__).parents[1]/'scripts/conferir_municipios.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MunicipalTests(unittest.TestCase):
    def vote(self, **overrides):
        row = dict(CD_CARGO='1',CD_TIPO_ELEICAO='2',SG_UF='RJ',ANO_ELEICAO='2026',NR_TURNO='1',
                   CD_MUNICIPIO='1',NR_ZONA='1',SQ_CANDIDATO='100',NM_TIPO_DESTINACAO_VOTOS='Válido',
                   ST_VOTO_EM_TRANSITO='N',DT_GERACAO='01/01/2026',HH_GERACAO='00:00:00',
                   NM_MUNICIPIO='ARARUAMA',NR_CANDIDATO='13',QT_VOTOS_NOMINAIS_VALIDOS='5')
        return row | overrides

    def test_duplicate_zone_rows_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicada'):
            m.municipal_votes([self.vote(),self.vote()])

    def test_zones_added_and_exterior_separated(self):
        v,_ = m.municipal_votes([self.vote(),self.vote(NR_ZONA='2'),self.vote(SG_UF='ZZ')])
        self.assertEqual(v['RJ','1'][1]['lula'],10)
        self.assertEqual(len(v),1)

    def test_source_generations_not_mixed(self):
        with self.assertRaisesRegex(ValueError,'Gerações'):
            m.municipal_votes([self.vote(),self.vote(NR_ZONA='2',HH_GERACAO='01:00:00')])

    def test_other_candidates_not_assigned_to_finalists(self):
        v,_ = m.municipal_votes([self.vote(NR_CANDIDATO='80')])
        self.assertEqual(v['RJ','1'][1],{'others':5,'valid':5})

    def test_name_key_does_not_depend_on_apostrophe(self):
        self.assertEqual(m.name_key("Olho d'Água"),m.name_key('OLHO D ÁGUA'))
        self.assertNotEqual(m.name_key('Santo Antônio do Leverger'),m.name_key('Santo Antônio de Leverger'))

    def test_ibge_total_only_and_no_suppressed_zero(self):
        doc=[{'id':'93','resultados':[{'classificacoes':[
            {'id':'2','categoria':{'6794':'Total'}},{'id':'286','categoria':{'113635':'Total'}},
            {'id':'287','categoria':{'100362':'Total'}}],
            'series':[{'localidade':{'id':'3300209','nome':'Araruama - RJ','nivel':{'id':'N6'}},'serie':{'2022':'10'}}]}]}]
        self.assertEqual(m.census_population(doc)['RJ','ARARUAMA']['population'],10)
        doc[0]['resultados'][0]['series'][0]['serie']['2022']='...'
        with self.assertRaises(ValueError): m.census_population(doc)
        doc[0]['resultados'][0]['classificacoes'][2]['categoria']={'6653':'100+'}
        with self.assertRaises(ValueError): m.census_population(doc)

    def fixture(self):
        votes, detail, pop = {}, {}, {}
        for i,name in enumerate(sorted(m.LAGOS)):
            key=('RJ',str(i+1))
            votes[key]={'name':name,1:{'lula':10,'flavio':30,'valid':40},2:{'lula':30,'flavio':31,'valid':61}}
            detail[key]={1:{'aptos':100,'attendance':40,'absence':60,'blank':0,'null':0},
                         2:{'aptos':100,'attendance':61,'absence':39,'blank':0,'null':0}}
            pop['RJ',m.name_key(name)]={'id':str(i),'population':50}
        votes['RJ','8']={'name':'VOLTA REDONDA',1:{'lula':25,'flavio':75,'valid':100},2:{'lula':35,'flavio':80,'valid':115}}
        detail['RJ','8']={1:{'aptos':200,'attendance':100,'absence':100,'blank':0,'null':0},
                          2:{'aptos':200,'attendance':115,'absence':85,'blank':0,'null':0}}
        pop['RJ','VOLTAREDONDA']={'id':'8','population':300}
        return votes,detail,pop

    def test_net_gain_share_and_weighted_absence(self):
        v,d,p=self.fixture();out=m.calculate(v,d,p)
        self.assertEqual(out['H23']['lagosLulaShareOfNetGainPercent'],95.24)
        self.assertEqual(out['H23']['lagosLulaGain'],140)
        self.assertEqual(out['H20']['Sudeste']['firstAbsencePercent'],57.78)
        self.assertEqual(out['H14']['attendanceAboveCensus'],7)

    def test_unmatched_population_not_replaced_with_zero(self):
        v,d,p=self.fixture();p.pop(next(iter(p)))
        out=m.calculate(v,d,p)
        self.assertEqual(out['H14']['attendanceAboveCensus'],6)
        self.assertEqual(len(out['H14']['unmatchedPopulation']),1)

    def test_many_to_one_join_and_turn_mismatch_rejected(self):
        v,d,p=self.fixture();p['RJ','VOLTAREDONDA']['id']='0'
        with self.assertRaisesRegex(ValueError,'mesma população'):m.calculate(v,d,p)
        v,d,p=self.fixture();d.pop(('RJ','8'))
        with self.assertRaisesRegex(ValueError,'Universos'):m.calculate(v,d,p)


if __name__ == '__main__':
    unittest.main()
