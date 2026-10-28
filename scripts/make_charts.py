"""Publication charts from the reconciled analysis. All amounts CAD."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/images';OUT.mkdir(parents=True,exist_ok=True)
R=json.loads((ROOT/'data/analysis/findings.json').read_text());T=R['totals'];Q=R['quality']
NAVY='#17324D';TEAL='#007F78';AMBER='#C98623';RED='#B44A49';GRAY='#65758A';BG='#F6F8FA'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':NAVY,'axes.labelcolor':NAVY,'xtick.color':GRAY,'ytick.color':NAVY,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
def save(fig,name,title,sub):
    fig.suptitle(title,x=.04,ha='left',y=.98,fontsize=20,fontweight='bold',color=NAVY)
    fig.text(.04,.91,sub,fontsize=10,color=GRAY)
    fig.text(.04,.025,'Source: fictional Wealthsimple training data. Same eligible records for costs and funnel counts.',fontsize=9,color=GRAY)
    fig.subplots_adjust(top=.83,bottom=.14,left=.21,right=.93)
    fig.savefig(OUT/(name+'.png'),dpi=170);plt.close(fig)

def main():
    g=pd.DataFrame(R['groups']['channel']).sort_values('spend')
    fig,(ax,bx)=plt.subplots(1,2,figsize=(14,7),gridspec_kw={'width_ratios':[1.1,1]})
    ax.barh(g.marketing_channel,g.spend,color=NAVY,height=.65);ax.set_xlabel('Eligible marketing cost (CAD)');ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'${x/1000:.0f}k'))
    bx.barh(g.marketing_channel,g.paying,color=TEAL,height=.65);bx.set_yticks([]);bx.set_xlabel('Recorded paying customers');bx.set_xlim(0,85)
    for i,v in enumerate(g.paying):bx.text(v+1,i,f'{v:.0f}',va='center',fontsize=10)
    fig.subplots_adjust(wspace=.18)
    save(fig,'channel_allocation','Paid Search records 69 of 106 paying customers','1,671 eligible campaign records. Six channels have no paying customers in this population.')
    fig,ax=plt.subplots(figsize=(12,6.5));good=g[g.cac.notna()].sort_values('cac',ascending=False)
    ax.barh(good.marketing_channel,good.cac,color=TEAL,height=.58)
    for i,v in enumerate(good.cac):ax.text(v+40,i,f'${v:,.0f}',va='center')
    ax.axvline(T['cac'],color=GRAY,ls='--');ax.text(T['cac']-40,4.4,f'Blended ${T["cac"]:,.0f}',ha='right',color=GRAY)
    ax.set_xlim(0,4600);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'${x:,.0f}'));ax.set_xlabel('Marketing cost per recorded paying customer (CAD)')
    save(fig,'cac_channel','Email and Referral have the lowest observed CAC','Only channels with paying customers are plotted. Zero-customer channels have undefined CAC, not zero CAC.')
    fig,ax=plt.subplots(figsize=(13,6.5))
    labels=['Impressions to clicks','Clicks to signups','Signups to funded','Funded to paying']
    rates=[T['ctr'],T['click_signup'],T['signup_funded'],T['funded_paying']]
    ax.barh(labels[::-1],[100*x for x in rates[::-1]],color=[TEAL,TEAL,NAVY,NAVY],height=.6);ax.set_xlim(0,17);ax.set_xlabel('Conversion to next stage (%)')
    for i,v in enumerate(rates[::-1]):ax.text(100*v+.25,i,f'{v:.2%}',va='center',fontweight='bold')
    sub=f'{T["impressions"]:,.0f} impressions / {T["clicks"]:,.0f} clicks / {T["signups"]:,.0f} signups / {T["funded"]:,.0f} funded / {T["paying"]:,.0f} paying'
    save(fig,'conversion_rates',f'{T["paid_conversion"]:.2%} of signups become recorded paying customers',sub)
    m=pd.DataFrame(R['monthly']);fig,(ax,bx)=plt.subplots(2,1,figsize=(13,7),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    ax.plot(m.year_month,m.spend/1000,color=TEAL,marker='o');ax.set_ylabel('Eligible cost (CAD thousands)');ax.grid(axis='y',alpha=.15)
    bx.bar(m.year_month,m.eligible_records,color=NAVY);bx.set_ylabel('Records');bx.tick_params(axis='x',rotation=60,labelsize=9)
    save(fig,'monthly_coverage','Monthly trends use dates that agree with the campaign month',f'{Q["trusted_dated_eligible_records"]:,} eligible dated records. CAD {Q["eligible_undated_spend"]:,.0f} eligible cost excluded from this trend.')
    fig,ax=plt.subplots(figsize=(12,6.5));labels=['Eligible for comparison','Missing or invalid funnel counts','Funnel sequence violations','Missing / invalid date','Date vs campaign-month conflict'];values=[Q['analysis_eligible'],Q['funnel_missing'],Q['funnel_order'],Q['missing_dates'],Q['date_month_conflicts']]
    ax.barh(labels[::-1],values[::-1],color=[AMBER]*4+[TEAL],height=.6)
    for i,v in enumerate(values[::-1]):ax.text(v+20,i,f'{v:,}',va='center')
    ax.set_xlim(0,2000);ax.set_xlabel('Campaign records')
    save(fig,'data_quality','83.55% of records meet the comparison rules','2,000 source records retained. Issue categories overlap and must not be added together.')
    s=pd.DataFrame(R['sensitivity']);fig,ax=plt.subplots(figsize=(12,6.5));labs=['Known numeric counts','Consistent funnel','Funnel and usable cost','Also requires trusted date'];ax.barh(labs[::-1],s.paying.iloc[::-1],color=[TEAL,TEAL,GRAY,AMBER],height=.6)
    for i,v in enumerate(s.paying.iloc[::-1]):ax.text(v+8,i,f'{v:,.0f}',va='center')
    ax.set_xlim(0,700);ax.set_xlabel('Recorded paying customers')
    save(fig,'population_sensitivity','The customer total changes materially after validation','The raw total of 607 includes three records with 100 paying customers and zero funded accounts each.')
    reg=pd.DataFrame(R['groups']['region']);reg=reg[reg.province!='Unknown'].sort_values('paying');fig,ax=plt.subplots(figsize=(12,7));ax.barh(reg.province,reg.paying,color=TEAL,height=.6)
    for i,v in enumerate(reg.paying):ax.text(v+.25,i,f'{v:.0f}',va='center')
    ax.set_xlim(0,20);ax.set_xlabel('Recorded paying customers')
    save(fig,'regional_customers','Regional results are small samples, not scaling mandates','Quebec records 17 paying customers, Manitoba 15, and Newfoundland & Labrador 13.')

if __name__=='__main__':main()
