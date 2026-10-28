"""Generate reviewable PBIP source. Desktop refresh/visual validation is still required."""
from pathlib import Path
import json, uuid
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'powerbi'
def write(p,s):
 p=OUT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def dump(p,x):write(p,json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def mq(s):return '"'+s.replace('"','""')+'"'
maps=json.loads((ROOT/'scripts/category_maps.json').read_text())
mmap='['+', '.join('#'+mq(k)+' = ['+', '.join('#'+mq(a)+' = '+mq(b) for a,b in v.items())+']' for k,v in maps.items())+']'
counts=['impressions','clicks','website_sessions','app_installs','signups','kyc_started','kyc_completed','funded_accounts','paying_customers']
money=['ad_spend_cad','agency_fee_cad','incentive_cost_cad','total_marketing_cost_cad','first_month_revenue_cad','projected_ltv_cad','avg_first_deposit_cad']
texts=['campaign_record_id','campaign_id','campaign_name','marketing_channel','customer_segment','province','device_type','product_focus','campaign_objective','crm_status']
flags=['flag_missing_date','flag_date_month_conflict','date_eligible','flag_cost_mismatch','flag_negative_component','flag_missing_funnel','flag_funnel_order','funnel_eligible','cost_eligible','analysis_eligible','revenue_eligible','roas_eligible','flag_missing_name','flag_missing_channel','flag_missing_segment','flag_negative_spend','flag_missing_revenue','flag_campaign_id_conflict']
# Keep source workbook separate so raw values can always be inspected.
raw='''let
    Workbook = Excel.Workbook(File.Contents(DataRoot & "/data/raw/Power_BI_project.xlsx"), null, true),
    Sheet = Workbook{[Item="Sheet1",Kind="Sheet"]}[Data],
    Headers = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true])
in Headers'''
write(Path('powerquery/Raw_Campaigns.m'),raw)
m='''let
    Source = Raw_Campaigns,
    Maps = __MAPS__,
    Norm = (v as any) as text => Text.Combine(List.Select(Text.SplitAny(Text.Lower(Text.Trim(if v = null then "" else Text.From(v))), " _-#(tab)#(cr)#(lf)"), each _ <> ""), " "),
    Num = (v as any) as nullable number => let s = if v = null then "" else Text.Trim(Text.Replace(Text.Replace(Text.Replace(Text.Upper(Text.From(v)), "CAD", ""), "$", ""), ",", "")), n = try Number.FromText(s,"en-US") otherwise null in n,
    CleanNum = (v as any, integer as logical) as nullable number => let n=Num(v) in if n=null then null else if n<0 or (integer and Number.RoundDown(n)<>n) then null else n,
    Map = (v as any, dict as record) as text => Record.FieldOrDefault(dict,Norm(v),"Unknown"),
    ParseDate = (v as any) as nullable date => if v=null then null else if Value.Is(v,type date) or Value.Is(v,type datetime) then Date.From(v) else List.First(List.RemoveNulls(List.Transform({"yyyy-MM-dd HH:mm:ss","yyyy-MM-dd","dd/MM/yyyy","dd.MM.yyyy","dd-MM-yyyy"}, (fmt)=>try Date.FromText(Text.From(v),[Format=fmt,Culture="en-GB"]) otherwise null)),null),
    CountNames = __COUNTS__,
    MoneyNames = __MONEY__,
    Chain = {"impressions","clicks","signups","kyc_started","kyc_completed","funded_accounts","paying_customers"},
    Identity = Table.Group(Source,{"campaign_id"},{{"Names", each List.Count(List.Distinct([campaign_name])),Int64.Type}}),
    ConflictIds = Table.SelectRows(Identity,each [Names]>1)[campaign_id],
    Records = List.Transform(Table.ToRecords(Source),(r)=>let
        numeric=Record.FromList(List.Transform(CountNames,each CleanNum(Record.Field(r,_),true)) & List.Transform(MoneyNames,each CleanNum(Record.Field(r,_),false)),CountNames & MoneyNames),
        channel=Map(r[marketing_channel],Maps[channel_map]), segment=Map(r[customer_segment],Maps[seg_map]),
        provinceCode=Map(r[province],Maps[prov_map]), province=Record.FieldOrDefault(Maps[prov_full],provinceCode,"Unknown"),
        day=ParseDate(r[event_date_raw]), id=if r[campaign_id]=null then "Unknown" else Text.Trim(Text.From(r[campaign_id])),
        name=if r[campaign_name]=null or Text.Trim(Text.From(r[campaign_name]))="" then "Unknown" else Text.Trim(Text.From(r[campaign_name])),
        month=if Text.StartsWith(id,"CMP-") and Text.Length(id)>=11 then Text.Range(id,4,6) else null,
        dateConflict=day<>null and month<>null and Date.ToText(day,"yyyyMM")<>month,
        components={numeric[ad_spend_cad],numeric[agency_fee_cad],numeric[incentive_cost_cad]},
        componentTotal=if List.NonNullCount(components)=3 then Number.Round(List.Sum(components),2) else null,
        reported=numeric[total_marketing_cost_cad], total=if reported=null then componentTotal else reported,
        mismatch=if reported=null or componentTotal=null then false else Number.Abs(reported-componentTotal)>0.021,
        negativeComponent=List.AnyTrue(List.Transform({"ad_spend_cad","agency_fee_cad","incentive_cost_cad"}, each let n=Num(Record.Field(r,_)) in n<>null and n<0)),
        seq=List.Transform(Chain,each Record.Field(numeric,_)), missing=List.NonNullCount(seq)<>List.Count(seq),
        badOrder=List.AnyTrue(List.Transform({0..5}, each let a=seq{_},b=seq{_+1} in if a=null or b=null then false else b>a)),
        funnel=not missing and not badOrder, cost=total<>null and not mismatch and not negativeComponent,
        eligible=funnel and cost, dated=day<>null and not dateConflict,
        rev=eligible and numeric[first_month_revenue_cad]<>null,
        original=Record.SelectFields(r,__TEXTS__),
        clean=Record.Combine({original,numeric,[campaign_id=id,campaign_name=name,marketing_channel=channel,customer_segment=segment,province=province,province_code=provinceCode,device_type=Map(r[device_type],Maps[device_map]),
            total_marketing_cost_cad=total,reported_cost_cad=reported,component_total_cad=componentTotal,cost_basis=if reported=null and componentTotal<>null then "complete component sum" else "reported",
            event_date=day,trend_date=if dated then day else null,campaign_key=id & " | " & name,campaign_family=channel & " | " & name,
            flag_missing_date=day=null,flag_date_month_conflict=dateConflict,date_eligible=dated,flag_cost_mismatch=mismatch,flag_negative_component=negativeComponent,
            flag_missing_funnel=missing,flag_funnel_order=badOrder,funnel_eligible=funnel,cost_eligible=cost,analysis_eligible=eligible,revenue_eligible=rev,roas_eligible=rev and numeric[ad_spend_cad]<>null,
            flag_missing_name=name="Unknown",flag_missing_channel=channel="Unknown",flag_missing_segment=segment="Unknown",flag_negative_spend=let n=Num(r[ad_spend_cad]) in n<>null and n<0,
            flag_missing_revenue=numeric[first_month_revenue_cad]=null,flag_campaign_id_conflict=List.Contains(ConflictIds,r[campaign_id])]})
    in clean),
    Result = Table.FromRecords(Records),
    Typed = Table.TransformColumnTypes(Result,__TYPES__,"en-CA")
in Typed'''
alltext=texts+['province_code','cost_basis','campaign_key','campaign_family']
allmoney=money+['reported_cost_cad','component_total_cad']
types=[(x,'type text') for x in alltext]+[(x,'Int64.Type') for x in counts]+[(x,'type number') for x in allmoney]+[(x,'type logical') for x in flags]+[(x,'type date') for x in ['event_date','trend_date']]
for a,b in {'__MAPS__':mmap,'__COUNTS__':'{'+','.join(map(mq,counts))+'}','__MONEY__':'{'+','.join(map(mq,money))+'}','__TEXTS__':'{'+','.join(map(mq,texts))+'}','__TYPES__':'{'+','.join('{'+mq(k)+','+v+'}' for k,v in types)+'}'}.items():m=m.replace(a,b)
write(Path('powerquery/Fact_Campaigns.m'),m)
date='''let
 Dates=List.Dates(#date(2025,1,1),730,#duration(1,0,0,0)),
 T=Table.FromList(Dates,Splitter.SplitByNothing(),{"Date"}),
 Typed=Table.TransformColumnTypes(T,{{"Date",type date}}),
 Year=Table.AddColumn(Typed,"Year",each Date.Year([Date]),Int64.Type),
 Month=Table.AddColumn(Year,"YearMonth",each Date.ToText([Date],"yyyy-MM"),type text)
in Month'''
write(Path('powerquery/Dim_Date.m'),date)
measures=[]
def measure(n,e,fmt='#,0',folder='Overview'):measures.append(dict(name=n,expression=e,formatString=fmt,displayFolder=folder))
def total(n,col):measure(n,f'CALCULATE(SUM(Fact_Campaigns[{col}]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))','"CAD "#,0.00' if 'Spend' in n else '#,0')
measure('Source Records','COUNTROWS(Fact_Campaigns)')
measure('Eligible Records','CALCULATE(COUNTROWS(Fact_Campaigns), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))')
measure('Excluded Records','[Source Records] - [Eligible Records]')
measure('Eligible Share','DIVIDE([Eligible Records],[Source Records])','0.0%')
for n,c in [('Total Spend','total_marketing_cost_cad'),('Ad Spend','ad_spend_cad'),('Impressions','impressions'),('Clicks','clicks'),('Signups','signups'),('KYC Started','kyc_started'),('KYC Completed','kyc_completed'),('Funded Accounts','funded_accounts'),('Paying Customers','paying_customers')]:total(n,c)
for n,a,b in [('CAC','Total Spend','Paying Customers'),('CPC','Total Spend','Clicks'),('CPS','Total Spend','Signups'),('CTR','Clicks','Impressions'),('Click to Signup','Signups','Clicks'),('Signup to Funded','Funded Accounts','Signups'),('Funded to Paying','Paying Customers','Funded Accounts'),('Signup to Paying','Paying Customers','Signups'),('KYC Completion','KYC Completed','KYC Started')]:measure(n,f'DIVIDE([{a}],[{b}])','"CAD "#,0.00' if n in ['CAC','CPC','CPS'] else '0.00%','Efficiency')
for n,c in [('First Month Revenue','first_month_revenue_cad'),('Matched Cost','total_marketing_cost_cad'),('Matched Paying Customers','paying_customers')]:measure(n,f'CALCULATE(SUM(Fact_Campaigns[{c}]), KEEPFILTERS(Fact_Campaigns[revenue_eligible] = TRUE()))','#,0.00','Revenue')
measure('ROAS','DIVIDE(CALCULATE(SUM(Fact_Campaigns[first_month_revenue_cad]),KEEPFILTERS(Fact_Campaigns[roas_eligible] = TRUE())),CALCULATE(SUM(Fact_Campaigns[ad_spend_cad]),KEEPFILTERS(Fact_Campaigns[roas_eligible] = TRUE())))','0.0000"x"','Revenue')
measure('Revenue to Marketing Cost','DIVIDE([First Month Revenue],[Matched Cost])','0.0000"x"','Revenue')
measure('Revenue Cost Gap','[First Month Revenue] - [Matched Cost]','"CAD "#,0.00','Revenue')
measure('Revenue per Paying Customer','DIVIDE([First Month Revenue],[Matched Paying Customers])','"CAD "#,0.00','Revenue')
measure('Revenue Records','CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[revenue_eligible]=TRUE()))','#,0','Revenue')
for n,flag in [('Missing Dates','flag_missing_date'),('Date Conflicts','flag_date_month_conflict'),('Incomplete Funnels','flag_missing_funnel'),('Funnel Violations','flag_funnel_order'),('Missing Names','flag_missing_name'),('Missing Channels','flag_missing_channel'),('Missing Segments','flag_missing_segment'),('Negative Spend Records','flag_negative_spend'),('Missing Revenue','flag_missing_revenue'),('Identity Conflict Records','flag_campaign_id_conflict')]:measure(n,f'CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[{flag}]=TRUE()))','#,0','Data Quality')
measure('Known Cost All Rows','SUM(Fact_Campaigns[total_marketing_cost_cad])','"CAD "#,0.00','Data Quality')
measure('Excluded Known Cost','[Known Cost All Rows]-[Total Spend]','"CAD "#,0.00','Data Quality')
measure('Reconstructed Costs','CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[cost_basis]="complete component sum"))','#,0','Data Quality')
for n,base in [('Trusted Monthly Spend','Total Spend'),('Trusted Monthly Revenue','First Month Revenue')]:measure(n,f'CALCULATE([{base}],KEEPFILTERS(Fact_Campaigns[date_eligible]=TRUE()))','"CAD "#,0.00','Time')
measure('Undated or Conflicted Spend','[Total Spend]-[Trusted Monthly Spend]','"CAD "#,0.00','Time')
measure('Zero Output Family Spend','SUMX(FILTER(VALUES(Fact_Campaigns[campaign_family]),[Eligible Records]>0 && NOT ISBLANK([Paying Customers]) && [Paying Customers]=0),[Total Spend])','"CAD "#,0.00','Budget Review')
measure('Zero Output Families','COUNTROWS(FILTER(VALUES(Fact_Campaigns[campaign_family]),[Eligible Records]>0 && NOT ISBLANK([Paying Customers]) && [Paying Customers]=0))','#,0','Budget Review')
measure('Zero Output Spend Share','DIVIDE([Zero Output Family Spend],[Total Spend])','0.0%','Budget Review')
measure('Review Status','SWITCH(TRUE(),[Eligible Records]=0,"No eligible records",ISBLANK([Paying Customers]),"Missing output",[Paying Customers]=0,"Investigate objective and lag","Evaluate with controlled test")','', 'Budget Review')
measure('Funnel Value','SWITCH(SELECTEDVALUE(Funnel_Stages[Stage]),"Impressions",[Impressions],"Clicks",[Clicks],"Signups",[Signups],"KYC started",[KYC Started],"KYC completed",[KYC Completed],"Funded accounts",[Funded Accounts],"Paying customers",[Paying Customers])','#,0','Funnel')
measure('Quality Issue Records','SWITCH(SELECTEDVALUE(Quality_Issues[Issue]),"Missing dates",[Missing Dates],"Date conflicts",[Date Conflicts],"Incomplete funnels",[Incomplete Funnels],"Funnel violations",[Funnel Violations],"Missing names",[Missing Names],"Missing channels",[Missing Channels],"Missing segments",[Missing Segments],"Negative spend",[Negative Spend Records],"Missing revenue",[Missing Revenue])','#,0','Data Quality')
measure('Selected Channel Benchmark CAC','CALCULATE([CAC],ALLSELECTED(Fact_Campaigns[marketing_channel]))','"CAD "#,0.00','Efficiency')
measure('Above Benchmark Channel Count','VAR Benchmark=[Selected Channel Benchmark CAC] RETURN COUNTROWS(FILTER(ALLSELECTED(Fact_Campaigns[marketing_channel]),NOT ISBLANK([CAC]) && [CAC]>Benchmark))','#,0','Efficiency')
measure('Observed Efficiency Ratio','DIVIDE([Selected Channel Benchmark CAC],[CAC])','0.00"x"','Efficiency')
# Tabular column and measure names share a case-insensitive namespace.
raw_column_names = {'impressions':'raw_impressions','clicks':'raw_clicks','signups':'raw_signups'}
for item in measures:
 for original, renamed in raw_column_names.items():
  item['expression'] = item['expression'].replace('Fact_Campaigns['+original+']', 'Fact_Campaigns['+renamed+']')
write(Path('DAX_Measures.md'),'# Measure catalogue\n\nGenerated with the source model. Use aggregate ratios, never average row CAC. BLANK means undefined, not zero. CPC uses total marketing cost; Ad Spend is separately available. Efficiency ratio = selected-channel blended CAC / channel CAC; it is a descriptive relative measure, not a commercial target.\n\n'+''.join('## '+x['name']+'\n\n```dax\n'+x['name']+' = '+x['expression']+'\n```\n\n' for x in measures))
# TMSL model, native M partitions.
def table(n,cols,expr,**extra):return dict(name=n,columns=cols,partitions=[dict(name=n,mode='import',source=dict(type='m',expression=expr))],**extra)
def col(n,t,**extra):return dict(name=n,dataType=t,sourceColumn=n,summarizeBy='none',**extra)
fcols=[col(n,'string') for n in alltext]+[col(n,'int64') for n in counts]+[col(n,'double') for n in allmoney]+[col(n,'boolean',isHidden=True) for n in flags]+[col(n,'dateTime',formatString='yyyy-MM-dd') for n in ['event_date','trend_date']]
for c in fcols:
 if c['name'] in raw_column_names:
  c['name'] = raw_column_names[c['name']]  # sourceColumn keeps the Power Query field name.
stages=['Impressions','Clicks','Signups','KYC started','KYC completed','Funded accounts','Paying customers']
issues=['Missing dates','Date conflicts','Incomplete funnels','Funnel violations','Missing names','Missing channels','Missing segments','Negative spend','Missing revenue']
stageM='#table(type table [Stage=text, Sort=Int64.Type],{'+','.join('{'+mq(n)+','+str(i)+'}' for i,n in enumerate(stages,1))+'})'
issueM='#table(type table [Issue=text],{'+','.join('{'+mq(n)+'}' for n in issues)+'})'
model={'name':'WealthsimpleMarketing','compatibilityLevel':1567,'model':{'culture':'en-CA','defaultPowerBIDataSourceVersion':'powerBI_V3','expressions':[{'name':'DataRoot','kind':'m','expression':'"C:/CHANGE_ME/Wealthsimple-Marketing-Analytics" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}, {'name':'Raw_Campaigns','kind':'m','expression':raw}], 'tables':[table('Fact_Campaigns',fcols,m,measures=measures),table('Dim_Date',[col('Date','dateTime',isKey=True,formatString='yyyy-MM-dd'),col('Year','int64'),col('YearMonth','string')],date,dataCategory='Time'),table('Funnel_Stages',[col('Stage','string',sortByColumn='Sort'),col('Sort','int64',isHidden=True)],stageM),table('Quality_Issues',[col('Issue','string')],issueM)],'relationships':[{'name':'CampaignDate','fromTable':'Fact_Campaigns','fromColumn':'trend_date','toTable':'Dim_Date','toColumn':'Date','crossFilteringBehavior':'oneDirection'}]}}
dump(Path('Wealthsimple.SemanticModel/model.bim'),model)
dump(Path('Wealthsimple.SemanticModel/definition.pbism'),{'version':'1.0','settings':{}})
dump(Path('Wealthsimple.pbip'),{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'Wealthsimple.Report'}}],'settings':{'enableAutoRecovery':True}})
dump(Path('Wealthsimple.Report/definition.pbir'),{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Wealthsimple.SemanticModel'}}})
def schema(n,v):return f'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/{n}/{v}/schema.json'
base=Path('Wealthsimple.Report/definition')
dump(base/'version.json',{'$schema':schema('versionMetadata','1.0.0'),'version':'4.0.0'})
dump(base/'report.json',{'$schema':schema('report','2.1.0'),'themeCollection':{},'settings':{'useStylableVisualContainerHeader':True}})
dump(Path('Wealthsimple_Theme.json'),{'name':'Wealthsimple training analytics','dataColors':['#007F78','#17324D','#D99A2B','#64748B','#C2463C','#7B61A8'],'background':'#FFFFFF','foreground':'#17324D','tableAccent':'#007F78'})
# Native PBIR visuals, stable names; no screenshots pretending to be interactive visuals.
def field(n):
 if n in [x['name'] for x in measures]:return {'Measure':{'Expression':{'SourceRef':{'Entity':'Fact_Campaigns'}},'Property':n}}
 t,c=n.split('.',1) if '.' in n else ('Fact_Campaigns',n)
 return {'Column':{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def proj(n):
 f=field(n);p=next(iter(f.values()));return {'field':f,'queryRef':p['Expression']['SourceRef']['Entity']+'.'+p['Property']}
def visual(page,name,kind,title,roles,pos,sync=None):
 v={'visualType':kind,'query':{'queryState':{r:{'projections':[proj(n) for n in ns]} for r,ns in roles.items()}},'visualContainerObjects':{'title':[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},'text':{'expr':{'Literal':{'Value':"'"+title.replace("'","''")+"'"}}}}}]},'drillFilterOtherVisuals':True}
 if sync:v['syncGroup']={'groupName':sync,'fieldChanges':True,'filterChanges':True}
 x,y,w,h,z=pos
 dump(base/'pages'/page/'visuals'/name/'visual.json',{'$schema':schema('visualContainer','2.1.0'),'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':z,'tabOrder':z},'visual':v})
def bar(title,cat,val):return ('clusteredBarChart',title,{'Category':[cat],'Y':[val]})
def tab(title,fields):return ('tableEx',title,{'Values':fields})
def line(title,vals):return ('lineChart',title,{'Category':['Dim_Date.YearMonth'],'Y':vals})
pages=[('01_quality','Data Quality',['Source Records','Eligible Records','Excluded Records','Reconstructed Costs'],[bar('Issue counts overlap; do not add','Quality_Issues.Issue','Quality Issue Records'),bar('Excluded records by channel','marketing_channel','Excluded Records'),tab('Missing fields by channel',['marketing_channel','Missing Names','Missing Channels','Missing Segments','Missing Revenue']),tab('Date and funnel diagnostics',['marketing_channel','Missing Dates','Date Conflicts','Incomplete Funnels','Funnel Violations'])]),
('02_spend','Spend and CAC',['Total Spend','CAC','CPC','CPS'],[bar('Marketing cost by channel','marketing_channel','Total Spend'),bar('CAC; zero output is undefined','marketing_channel','CAC'),line('Trusted dates only: monthly cost',['Trusted Monthly Spend']),tab('Campaign spend and relative efficiency',['campaign_family','Total Spend','Paying Customers','CAC','Observed Efficiency Ratio'])]),
('03_funnel','Conversion Funnel',['CTR','Click to Signup','Signup to Funded','Funded to Paying'],[('funnel','Comparable cohort including KYC',{'Category':['Funnel_Stages.Stage'],'Y':['Funnel Value']}),bar('Signup to paying by channel','marketing_channel','Signup to Paying'),bar('Signup to paying by segment','customer_segment','Signup to Paying'),tab('Campaign funnel detail',['campaign_key','Signups','KYC Started','KYC Completed','Funded Accounts','Paying Customers'])]),
('04_channels','Channel and Campaign',['Paying Customers','First Month Revenue','CAC','Signup to Paying'],[tab('Channel scorecard',['marketing_channel','Total Spend','Paying Customers','CAC','ROAS','Observed Efficiency Ratio']),bar('Recorded paying customers','campaign_family','Paying Customers'),('scatterChart','Cost versus customers: association only',{'Category':['marketing_channel'],'X':['Total Spend'],'Y':['Paying Customers'],'Size':['Signups']}),tab('Campaign review status',['campaign_family','campaign_objective','Review Status','Total Spend','Paying Customers'])]),
('05_revenue','Revenue and ROAS',['First Month Revenue','ROAS','Revenue per Paying Customer','Revenue Cost Gap'],[line('Matched revenue; trusted dates',['Trusted MonthlyRevenue'.replace('MonthlyRevenue','Monthly Revenue')]),bar('First-month revenue by channel','marketing_channel','First Month Revenue'),bar('Matched revenue / ad spend','marketing_channel','ROAS'),tab('First-month return; not lifetime profit',['campaign_family','First Month Revenue','Matched Cost','Revenue Cost Gap','ROAS'])]),
('06_audience','Segment and Region',['Paying Customers','Signup to Paying','CAC','ROAS'],[bar('Recorded paying customers by province','province','Paying Customers'),tab('Segment comparison',['customer_segment','Paying Customers','Signup to Paying','CAC']),tab('Device comparison',['device_type','Paying Customers','Signup to Paying','CAC']),tab('Product comparison',['product_focus','Total Spend','Paying Customers','CAC','ROAS'])]),
('07_budget','Budget Optimization',['Zero Output Family Spend','Zero Output Families','Zero Output Spend Share','Above Benchmark Channel Count'],[bar('Zero-output cost: review, not proven waste','marketing_channel','Zero Output Family Spend'),tab('Review queue: validate lag and objective',['campaign_family','campaign_objective','Total Spend','Paying Customers','Review Status']),tab('Controlled-test candidates; no guaranteed uplift',['marketing_channel','Paying Customers','CAC','Signup to Paying']),tab('Coverage and benchmark context',['Eligible Records','Excluded Records','Undated or Conflicted Spend','Selected Channel Benchmark CAC'])])]
filters=[('marketing_channel','Channel'),('campaign_family','Campaign family'),('province','Province'),('customer_segment','Segment'),('device_type','Device'),('product_focus','Product'),('Dim_Date.YearMonth','Period')]
for pid,label,cards,charts in pages:
 dump(base/'pages'/pid/'page.json',{'$schema':schema('page','2.0.0'),'name':pid,'displayName':label,'displayOption':'FitToPage','width':1600,'height':1100})
 for i,(f,t) in enumerate(filters):visual(pid,'filter_'+str(i),'slicer',t,{'Values':[f]},(20+i*225,20,215,105,i),sync=f.replace('.','_'))
 for i,n in enumerate(cards):visual(pid,'kpi_'+str(i),'card',n,{'Values':[n]},(20+i*395,145,380,125,10+i))
 for i,(kind,title,roles) in enumerate(charts):visual(pid,'chart_'+str(i),kind,title,roles,(20+(i%2)*790,290+(i//2)*390,770,370,20+i))
dump(base/'pages/pages.json',{'$schema':schema('pagesMetadata','1.0.0'),'pageOrder':[p[0] for p in pages],'activePageName':pages[0][0]})
write(Path('Wealthsimple.SemanticModel/DAXQueries/Reconcile.dax'),'EVALUATE\nROW("Records",[Source Records],"Eligible",[Eligible Records],"Cost",[Total Spend],"Paying",[Paying Customers],"CAC",[CAC],"Revenue",[First Month Revenue],"ROAS",[ROAS],"Zero output cost",[Zero Output Family Spend])\n')
print('Generated',len(measures),'measures,',len(pages),'pages and 105 native visuals. Desktop validation pending.')

