"""Produce one numerical source for the report, charts, README and Power BI reconciliation."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
TOTALS={'spend':'total_marketing_cost_cad','ad_spend':'ad_spend_cad','revenue':'first_month_revenue_cad','impressions':'impressions','clicks':'clicks','signups':'signups','funded':'funded_accounts','paying':'paying_customers','kyc_started':'kyc_started','kyc_completed':'kyc_completed'}

def ratio(a,b):return a/b if pd.notna(a) and pd.notna(b) and b>0 else None

def metrics(g):
    a=g[g.analysis_eligible];r=g[g.revenue_eligible];ad=g[g.roas_eligible]
    out={'records':len(g),'eligible_records':len(a),'excluded_records':len(g)-len(a),'known_spend':g.total_marketing_cost_cad.sum(min_count=1),'eligible_share':len(a)/len(g) if len(g) else None}
    for k,c in TOTALS.items():out[k]=a[c].sum(min_count=1)
    out['revenue']=r.first_month_revenue_cad.sum(min_count=1)
    out['revenue_records']=len(r)
    out['ctr']=ratio(out['clicks'],out['impressions']);out['click_signup']=ratio(out['signups'],out['clicks'])
    out['signup_funded']=ratio(out['funded'],out['signups']);out['funded_paying']=ratio(out['paying'],out['funded']);out['paid_conversion']=ratio(out['paying'],out['signups'])
    out['kyc_completion']=ratio(out['kyc_completed'],out['kyc_started'])
    out['cac']=ratio(out['spend'],out['paying']);out['cpc']=ratio(out['spend'],out['clicks']);out['cps']=ratio(out['spend'],out['signups'])
    out['roas']=ratio(ad.first_month_revenue_cad.sum(min_count=1),ad.ad_spend_cad.sum(min_count=1))
    out['marketing_return']=ratio(out['revenue'],r.total_marketing_cost_cad.sum(min_count=1))
    out['revenue_cost_gap']=out['revenue']-r.total_marketing_cost_cad.sum(min_count=1)
    out['revenue_roi_proxy']=ratio(out['revenue_cost_gap'],r.total_marketing_cost_cad.sum(min_count=1))
    out['arpc']=ratio(out['revenue'],r.paying_customers.sum(min_count=1))
    return out

def clean_json(obj):
    if isinstance(obj,dict):return {k:clean_json(v) for k,v in obj.items()}
    if isinstance(obj,list):return [clean_json(v) for v in obj]
    if obj is None:return None
    if pd.isna(obj):return None
    if hasattr(obj,'item'):return obj.item()
    return obj

def main():
    f=pd.read_csv(ROOT/'data/processed/fact_campaigns.csv',parse_dates=['event_date'])
    old=pd.read_excel(ROOT/'data/raw/Power_BI_project.xlsx',keep_default_na=False)
    out=ROOT/'data/analysis';out.mkdir(exist_ok=True)
    R={'totals':metrics(f),'groups':{}}
    for k,col in [('channel','marketing_channel'),('campaign','campaign_key'),('family','campaign_family'),('segment','customer_segment'),('region','province'),('device','device_type'),('product','product_focus'),('objective','campaign_objective')]:
        g=pd.DataFrame([{col:v,**metrics(x)} for v,x in f.groupby(col,dropna=False)]).sort_values('spend',ascending=False)
        g.to_csv(out/(k+'.csv'),index=False);R['groups'][k]=g.to_dict('records')
    monthly=f[f.date_eligible].copy();monthly['year_month']=monthly.event_date.dt.strftime('%Y-%m')
    g=pd.DataFrame([{'year_month':v,**metrics(x)} for v,x in monthly.groupby('year_month')]);g.to_csv(out/'monthly.csv',index=False);R['monthly']=g.to_dict('records')
    fam=pd.read_csv(out/'family.csv');zero=fam[(fam.paying==0)&fam.spend.gt(0)]
    # These are observed zero-output families, not demonstrated waste or automatic pause decisions.
    R['zero_output_families']={'count':len(zero),'spend':zero.spend.sum(),'share':zero.spend.sum()/R['totals']['spend'],'families':zero.to_dict('records')}
    a=f[f.analysis_eligible]
    R['quality']={'records':len(f),'funnel_eligible':int(f.funnel_eligible.sum()),'analysis_eligible':int(f.analysis_eligible.sum()),'funnel_missing':int(f.flag_missing_funnel.sum()),'funnel_order':int(f.flag_funnel_order.sum()),'missing_dates':int(f.flag_missing_date.sum()),'date_month_conflicts':int(f.flag_date_month_conflict.sum()),'trusted_dated_records':int(f.date_eligible.sum()),'trusted_dated_eligible_records':int((f.date_eligible&f.analysis_eligible).sum()),'cost_eligible':int(f.cost_eligible.sum()),'cost_reconstructed':int(f.cost_basis.eq('complete component sum').sum()),'campaign_ids_conflicting':int(f.loc[f.flag_campaign_id_conflict,'campaign_id'].nunique()),'campaign_keys':int(f.campaign_key.nunique()),'campaign_families':int(f.campaign_family.nunique()),'raw_channels':int(old.marketing_channel.nunique()),'clean_channels':int(f.marketing_channel.nunique()),'raw_segments':int(old.customer_segment.nunique()),'clean_segments':int(f.customer_segment.nunique()),'zero_revenue_rows':int(f.first_month_revenue_cad.eq(0).sum()),'missing_revenue_rows':int(f.first_month_revenue_cad.isna().sum()),'known_spend':f.total_marketing_cost_cad.sum(),'excluded_known_spend':f.loc[~f.analysis_eligible,'total_marketing_cost_cad'].sum(),'unknown_spend_rows':int(f.total_marketing_cost_cad.isna().sum()),'eligible_undated_spend':a.loc[~a.date_eligible,'total_marketing_cost_cad'].sum(),'raw_paying_numeric':pd.to_numeric(old.paying_customers,errors='coerce').sum(),'eligible_paying':a.paying_customers.sum(),'eligible_zero_revenue':int(a.first_month_revenue_cad.eq(0).sum()),'eligible_revenue_missing':int(a.first_month_revenue_cad.isna().sum())}
    # Sensitivity keeps the spend and customer populations aligned in each row.
    sens=[]
    for label,mask in [('Known numeric values (not validated)',pd.Series(True,index=f.index)),('Consistent funnel only',f.funnel_eligible),('Consistent funnel and usable cost (headline)',f.analysis_eligible),('Headline plus trusted date',f.analysis_eligible&f.date_eligible)]:
        z=f[mask];sp=z.total_marketing_cost_cad.sum();pay=z.paying_customers.sum()
        sens.append({'population':label,'rows':len(z),'known_spend':sp,'paying':pay,'cac':ratio(sp,pay),'signups':z.signups.sum(),'paid_conversion':ratio(pay,z.signups.sum())})
    pd.DataFrame(sens).to_csv(out/'population_sensitivity.csv',index=False);R['sensitivity']=sens
    R=clean_json(R);(out/'findings.json').write_text(json.dumps(R,indent=2,allow_nan=False))
    print(json.dumps({'totals':R['totals'],'quality':R['quality'],'zero_output':{k:v for k,v in R['zero_output_families'].items() if k!='families'}},indent=2))

if __name__=='__main__':main()
