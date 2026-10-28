"""Auditable preparation of the supplied fictional campaign records. Never repairs by guessing."""
from pathlib import Path
from datetime import datetime, date
import argparse, json, re, math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPS = json.loads((Path(__file__).with_name('category_maps.json')).read_text())
NULLS = {'', 'nan', 'na', 'n/a', 'missing', 'error', 'check', 'unknown', 'none', 'null', 'tbd', '-'}
COUNTS = ['impressions','clicks','website_sessions','app_installs','signups','kyc_started','kyc_completed','funded_accounts','paying_customers']
MONEY = ['ad_spend_cad','agency_fee_cad','incentive_cost_cad','total_marketing_cost_cad','first_month_revenue_cad','projected_ltv_cad','avg_first_deposit_cad']
CHAIN = ['impressions','clicks','signups','kyc_started','kyc_completed','funded_accounts','paying_customers']

def norm(v):
    return re.sub(r'[\s\-_]+',' ',str(v).strip().lower())

def number(v):
    s=re.sub(r'(?i)CAD|\$|,','',str(v)).strip()
    if s.lower() in NULLS: return None
    try:
        n=float(s)
        return n if math.isfinite(n) else None
    except (ValueError,TypeError): return None

def parse_date(v):
    if isinstance(v,(datetime,date,pd.Timestamp)): return pd.Timestamp(v).normalize()
    s=str(v).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d/%m/%Y','%d.%m.%Y','%d-%m-%Y'):
        try:return pd.Timestamp(datetime.strptime(s,fmt)).normalize()
        except ValueError:pass
    return pd.NaT

def prepare(source):
    raw=pd.read_excel(source,sheet_name='Sheet1',keep_default_na=False)
    assert len(raw)>0 and raw.campaign_record_id.is_unique and raw.campaign_record_id.ne('').all()
    f=raw.copy(); log=[]
    def issue(i,field,rule,action,old=None,new=None):
        log.append(dict(campaign_record_id=raw.at[i,'campaign_record_id'],field=field,rule=rule,action=action,
                        raw_value=str(raw.at[i,field] if old is None and field in raw else old),clean_value='' if new is None else str(new)))
    for c in raw:
        if c not in COUNTS+MONEY+['event_date_raw','bounce_rate','lead_quality_score','days_to_paid_customer_avg']:
            f[c]=raw[c].map(lambda v:str(v).strip() if str(v).strip() else None)
    for c in COUNTS+MONEY+['bounce_rate','lead_quality_score','days_to_paid_customer_avg']:
        ns=[]
        for i,v in raw[c].items():
            n=number(v)
            if n is None: issue(i,c,'missing_or_unparseable','retained as null')
            elif n<0:
                issue(i,c,'negative_numeric','retained in raw; analytical value null');n=None
            elif c in COUNTS and not float(n).is_integer():
                issue(i,c,'fractional_count','analytical value null');n=None
            elif (c=='bounce_rate' and n>1) or (c=='lead_quality_score' and n>100):
                issue(i,c,'outside_allowed_range','analytical value null');n=None
            ns.append(n)
        f[c]=pd.Series(ns,dtype='float64')
    for c,m in [('marketing_channel','channel_map'),('customer_segment','seg_map'),('device_type','device_map')]:
        values=[]
        for i,v in raw[c].items():
            new=MAPS[m].get(norm(v),'Unknown')
            if new=='Unknown':issue(i,c,'missing_or_unmapped_category','Unknown retained',new=new)
            elif str(v)!=new:issue(i,c,'category_standardized','mapped',new=new)
            values.append(new)
        f[c]=values
    f['province_code']=raw.province.map(lambda x:MAPS['prov_map'].get(norm(x),'Unknown'))
    f['province']=f.province_code.map(lambda x:MAPS['prov_full'].get(x,'Unknown'))
    for i in f.index:
        if f.at[i,'province']!=str(raw.at[i,'province']):issue(i,'province','category_standardized','mapped or Unknown',new=f.at[i,'province'])
    platform_names=['Google Ads','Bing Ads','Meta Ads','TikTok Ads','Snap Ads','YouTube Ads','Google Display','Programmatic DSP','SEO','Referral Program','HubSpot','Braze','Instagram Creator','TikTok Creator','YouTube Creator','LinkedIn Ads','Finance Blog','Newsletter Partner','Comparison Site','Transit Ads','Campus Posters']
    pm={norm(x):x for x in platform_names}
    f['ad_platform']=raw.ad_platform.map(lambda x:pm.get(norm(x),'Unknown'))
    for c in ['utm_source','utm_medium']:
        f[c]=raw[c].map(lambda x:'Unknown' if str(x).lower().strip() in NULLS else str(x).lower().strip())
    f['utm_source']=f.utm_source.replace({'fb':'meta'})
    for c in ['support_chat_before_payment','unsubscribe_flag','churned_within_30_days']:
        f[c]=raw[c].map(lambda x:{'yes':'Yes','no':'No'}.get(norm(x),'Unknown'))
    f['event_date']=raw.event_date_raw.map(parse_date)
    f['campaign_month']=raw.campaign_id.str.extract(r'^CMP-(\d{6})-',expand=False)
    f['flag_missing_date']=f.event_date.isna()
    f['flag_date_month_conflict']=f.event_date.notna() & f.campaign_month.notna() & f.event_date.dt.strftime('%Y%m').ne(f.campaign_month)
    f['date_eligible']=~(f.flag_missing_date|f.flag_date_month_conflict)
    for i in f.index:
        if f.at[i,'flag_missing_date']:issue(i,'event_date_raw','invalid_or_missing_date','exclude from dated trends')
        if f.at[i,'flag_date_month_conflict']:issue(i,'event_date_raw','date_campaign_month_conflict','retain date; exclude from trusted trend')
    components=['ad_spend_cad','agency_fee_cad','incentive_cost_cad']
    f['component_total_cad']=f[components].sum(axis=1,min_count=3).round(2)
    f['flag_cost_mismatch']=f.total_marketing_cost_cad.notna() & f.component_total_cad.notna() & ((f.total_marketing_cost_cad-f.component_total_cad).abs()>0.021)
    neg_component=pd.concat([raw[c].map(number).lt(0) for c in components],axis=1).any(axis=1)
    f['reported_cost_cad']=f.total_marketing_cost_cad
    rebuild=f.total_marketing_cost_cad.isna() & f.component_total_cad.notna()
    f.loc[rebuild,'total_marketing_cost_cad']=f.loc[rebuild,'component_total_cad']
    f['cost_basis']='reported';f.loc[rebuild,'cost_basis']='complete component sum'
    f['cost_eligible']=f.total_marketing_cost_cad.notna() & ~f.flag_cost_mismatch & ~neg_component
    for i in f.index:
        if rebuild[i]:issue(i,'total_marketing_cost_cad','cost_reconstructed','sum of all three valid components',new=f.at[i,'total_marketing_cost_cad'])
        if f.at[i,'flag_cost_mismatch']:issue(i,'total_marketing_cost_cad','cost_component_mismatch','exclude from comparable cost analysis')
    f['flag_missing_funnel']=f[CHAIN].isna().any(axis=1)
    flags=[]
    for a,b in zip(CHAIN,CHAIN[1:]):
        c='flag_'+b+'_gt_'+a;f[c]=f[b]>f[a];flags.append(c)
        for i in f.index[f[c]]:issue(i,b,c,'retain and exclude from consistent funnel')
    f['flag_funnel_order']=f[flags].any(axis=1)
    f['funnel_eligible']=~(f.flag_missing_funnel|f.flag_funnel_order)
    f['analysis_eligible']=f.funnel_eligible & f.cost_eligible
    f['revenue_eligible']=f.analysis_eligible & f.first_month_revenue_cad.notna()
    f['roas_eligible']=f.revenue_eligible & f.ad_spend_cad.notna()
    conflicts=raw.groupby('campaign_id').campaign_name.nunique();bad=set(conflicts[conflicts>1].index)
    f['flag_campaign_id_conflict']=f.campaign_id.isin(bad)
    f['campaign_key']=f.campaign_id+' | '+f.campaign_name
    f['campaign_family']=f.marketing_channel+' | '+f.campaign_name
    for i in f.index[f.flag_campaign_id_conflict]:issue(i,'campaign_id','campaign_id_multiple_names','use composite id plus name')
    for c in ['ad_spend_cad','total_marketing_cost_cad']:
        q1,q3=f[c].quantile([.25,.75]);cut=q3+3*(q3-q1)
        f['flag_'+c+'_outlier']=f[c]>cut
        for i in f.index[f['flag_'+c+'_outlier']]:issue(i,c,'high_value_review','retained; 3-IQR review only')
    f['flag_zero_click_spend']=f.cost_eligible & f.clicks.eq(0) & f.total_marketing_cost_cad.gt(0)
    f['flag_signup_no_impressions']=f.impressions.eq(0)&f.signups.gt(0)
    f['flag_paid_status_no_paying']=f.crm_status.eq('Paid Customer')&f.paying_customers.eq(0)
    f['flag_zero_revenue_spend']=f.cost_eligible&f.first_month_revenue_cad.eq(0)&f.total_marketing_cost_cad.gt(0)
    # Coverage is a count of observations, never an imputation of unknown values.
    fields=['event_date','marketing_channel','province','device_type']+CHAIN+['total_marketing_cost_cad','first_month_revenue_cad']
    present=f[fields].notna() & f[fields].ne('Unknown')
    f['row_completeness']=present.mean(axis=1)
    for c in ['ad_platform','utm_source','utm_medium','support_chat_before_payment','unsubscribe_flag','churned_within_30_days']:
        for i in f.index:
            if str(raw.at[i,c])!=str(f.at[i,c]):issue(i,c,'text_standardized','standardized or Unknown',new=f.at[i,c])
    logs=pd.DataFrame(log)
    profile=[]
    for c in raw:
        profile.append(dict(field=c,raw_blank=int(raw[c].eq('').sum()),raw_distinct=int(raw[c].nunique()),clean_missing=int((f[c].isna()|f[c].eq('Unknown')).sum()),clean_distinct=int(f[c].nunique())))
    dq=logs.groupby(['rule','action']).agg(issues=('campaign_record_id','size'),records=('campaign_record_id','nunique')).reset_index()
    return raw,f,logs,pd.DataFrame(profile),dq

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'data/raw/Power_BI_project.xlsx');args=p.parse_args()
    raw,f,logs,profile,dq=prepare(args.source)
    out=ROOT/'data/processed';out.mkdir(parents=True,exist_ok=True)
    for name,df in [('fact_campaigns',f),('data_quality_log',logs),('field_profile',profile),('dq_summary',dq)]:df.to_csv(out/(name+'.csv'),index=False,date_format='%Y-%m-%d')
    # Preserve explicit date types as ISO strings in CSV; full calendar years for DAX time intelligence.
    d=pd.DataFrame({'Date':pd.date_range(f.event_date.min().replace(month=1,day=1),f.event_date.max().replace(month=12,day=31))})
    d['Year']=d.Date.dt.year;d['MonthNo']=d.Date.dt.month;d['MonthName']=d.Date.dt.strftime('%b');d['YearMonth']=d.Date.dt.strftime('%Y-%m');d['YearMonthSort']=d.Year*100+d.MonthNo;d['Quarter']='Q'+d.Date.dt.quarter.astype(str)
    d.to_csv(out/'dim_date.csv',index=False,date_format='%Y-%m-%d')
    print(json.dumps({'records':len(f),'analysis_eligible':int(f.analysis_eligible.sum()),'funnel_eligible':int(f.funnel_eligible.sum()),'missing_dates':int(f.flag_missing_date.sum()),'date_conflicts':int(f.flag_date_month_conflict.sum()),'cost_mismatches':int(f.flag_cost_mismatch.sum()),'issues':len(logs)},indent=2))

if __name__=='__main__':main()
