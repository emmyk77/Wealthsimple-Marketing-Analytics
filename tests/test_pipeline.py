"""Data integrity, parser boundaries and independent control totals."""
import unittest, sys, json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from clean_data import number,parse_date,CHAIN

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=pd.read_csv(ROOT/'data/processed/fact_campaigns.csv');cls.r=json.loads((ROOT/'data/analysis/findings.json').read_text())
    def test_source_rows_and_keys(self):
        raw=pd.read_excel(ROOT/'data/raw/Power_BI_project.xlsx')
        self.assertEqual(len(self.f),len(raw));self.assertEqual(set(self.f.campaign_record_id),set(raw.campaign_record_id));self.assertTrue(self.f.campaign_record_id.is_unique)
    def test_parsers(self):
        self.assertEqual(number('CAD $1,234.56'),1234.56);self.assertEqual(number('-12'),-12);self.assertIsNone(number('ten'));self.assertIsNone(number('missing'))
        self.assertEqual(str(parse_date('31/01/2025').date()),'2025-01-31');self.assertTrue(pd.isna(parse_date('2026-13-01')))
    def test_same_population_totals(self):
        a=self.f[self.f.analysis_eligible];t=self.r['totals']
        self.assertEqual(len(a),t['eligible_records']);self.assertEqual(a.paying_customers.sum(),t['paying']);self.assertAlmostEqual(a.total_marketing_cost_cad.sum()/a.paying_customers.sum(),t['cac'])
    def test_known_anomalies_excluded(self):
        ids=['WS-MKT-000922','WS-MKT-001358','WS-MKT-001983']
        self.assertTrue((~self.f.set_index('campaign_record_id').loc[ids,'analysis_eligible']).all())
    def test_funnel_is_complete_and_monotonic(self):
        a=self.f[self.f.funnel_eligible];self.assertTrue(a[CHAIN].notna().all().all());self.assertTrue(a[CHAIN].ge(0).all().all())
        for x,y in zip(CHAIN,CHAIN[1:]):self.assertTrue((a[x]>=a[y]).all())
    def test_channels_reconcile(self):
        c=pd.read_csv(ROOT/'data/analysis/channel.csv');t=self.r['totals']
        for k in ['spend','paying','signups','funded','impressions','clicks']:self.assertAlmostEqual(c[k].sum(),t[k],places=6)
    def test_date_coverage_reconciles(self):
        m=pd.read_csv(ROOT/'data/analysis/monthly.csv');t=self.r['totals'];q=self.r['quality']
        self.assertAlmostEqual(m.spend.sum()+q['eligible_undated_spend'],t['spend'],places=6)
    def test_log_has_record_ids(self):
        log=pd.read_csv(ROOT/'data/processed/data_quality_log.csv');self.assertTrue(log.campaign_record_id.notna().all());self.assertTrue(set(log.campaign_record_id)<=set(self.f.campaign_record_id))
    def test_missing_is_not_zero(self):
        self.assertTrue(self.f.paying_customers.isna().any());c=pd.read_csv(ROOT/'data/analysis/channel.csv');self.assertTrue(c.loc[c.paying.eq(0),'cac'].isna().all())

if __name__=='__main__':unittest.main()
