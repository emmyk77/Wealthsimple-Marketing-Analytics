# Measure catalogue

Generated with the source model. Use aggregate ratios, never average row CAC. BLANK means undefined, not zero. CPC uses total marketing cost; Ad Spend is separately available. Efficiency ratio = selected-channel blended CAC / channel CAC; it is a descriptive relative measure, not a commercial target.

## Source Records

```dax
Source Records = COUNTROWS(Fact_Campaigns)
```

## Eligible Records

```dax
Eligible Records = CALCULATE(COUNTROWS(Fact_Campaigns), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Excluded Records

```dax
Excluded Records = [Source Records] - [Eligible Records]
```

## Eligible Share

```dax
Eligible Share = DIVIDE([Eligible Records],[Source Records])
```

## Total Spend

```dax
Total Spend = CALCULATE(SUM(Fact_Campaigns[total_marketing_cost_cad]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Ad Spend

```dax
Ad Spend = CALCULATE(SUM(Fact_Campaigns[ad_spend_cad]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Impressions

```dax
Impressions = CALCULATE(SUM(Fact_Campaigns[impressions]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Clicks

```dax
Clicks = CALCULATE(SUM(Fact_Campaigns[clicks]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Signups

```dax
Signups = CALCULATE(SUM(Fact_Campaigns[signups]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## KYC Started

```dax
KYC Started = CALCULATE(SUM(Fact_Campaigns[kyc_started]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## KYC Completed

```dax
KYC Completed = CALCULATE(SUM(Fact_Campaigns[kyc_completed]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Funded Accounts

```dax
Funded Accounts = CALCULATE(SUM(Fact_Campaigns[funded_accounts]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## Paying Customers

```dax
Paying Customers = CALCULATE(SUM(Fact_Campaigns[paying_customers]), KEEPFILTERS(Fact_Campaigns[analysis_eligible] = TRUE()))
```

## CAC

```dax
CAC = DIVIDE([Total Spend],[Paying Customers])
```

## CPC

```dax
CPC = DIVIDE([Total Spend],[Clicks])
```

## CPS

```dax
CPS = DIVIDE([Total Spend],[Signups])
```

## CTR

```dax
CTR = DIVIDE([Clicks],[Impressions])
```

## Click to Signup

```dax
Click to Signup = DIVIDE([Signups],[Clicks])
```

## Signup to Funded

```dax
Signup to Funded = DIVIDE([Funded Accounts],[Signups])
```

## Funded to Paying

```dax
Funded to Paying = DIVIDE([Paying Customers],[Funded Accounts])
```

## Signup to Paying

```dax
Signup to Paying = DIVIDE([Paying Customers],[Signups])
```

## KYC Completion

```dax
KYC Completion = DIVIDE([KYC Completed],[KYC Started])
```

## First Month Revenue

```dax
First Month Revenue = CALCULATE(SUM(Fact_Campaigns[first_month_revenue_cad]), KEEPFILTERS(Fact_Campaigns[revenue_eligible] = TRUE()))
```

## Matched Cost

```dax
Matched Cost = CALCULATE(SUM(Fact_Campaigns[total_marketing_cost_cad]), KEEPFILTERS(Fact_Campaigns[revenue_eligible] = TRUE()))
```

## Matched Paying Customers

```dax
Matched Paying Customers = CALCULATE(SUM(Fact_Campaigns[paying_customers]), KEEPFILTERS(Fact_Campaigns[revenue_eligible] = TRUE()))
```

## ROAS

```dax
ROAS = DIVIDE(CALCULATE(SUM(Fact_Campaigns[first_month_revenue_cad]),KEEPFILTERS(Fact_Campaigns[roas_eligible] = TRUE())),CALCULATE(SUM(Fact_Campaigns[ad_spend_cad]),KEEPFILTERS(Fact_Campaigns[roas_eligible] = TRUE())))
```

## Revenue to Marketing Cost

```dax
Revenue to Marketing Cost = DIVIDE([First Month Revenue],[Matched Cost])
```

## Revenue Cost Gap

```dax
Revenue Cost Gap = [First Month Revenue] - [Matched Cost]
```

## Revenue per Paying Customer

```dax
Revenue per Paying Customer = DIVIDE([First Month Revenue],[Matched Paying Customers])
```

## Revenue Records

```dax
Revenue Records = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[revenue_eligible]=TRUE()))
```

## Missing Dates

```dax
Missing Dates = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_missing_date]=TRUE()))
```

## Date Conflicts

```dax
Date Conflicts = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_date_month_conflict]=TRUE()))
```

## Incomplete Funnels

```dax
Incomplete Funnels = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_missing_funnel]=TRUE()))
```

## Funnel Violations

```dax
Funnel Violations = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_funnel_order]=TRUE()))
```

## Missing Names

```dax
Missing Names = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_missing_name]=TRUE()))
```

## Missing Channels

```dax
Missing Channels = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_missing_channel]=TRUE()))
```

## Missing Segments

```dax
Missing Segments = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_missing_segment]=TRUE()))
```

## Negative Spend Records

```dax
Negative Spend Records = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_negative_spend]=TRUE()))
```

## Missing Revenue

```dax
Missing Revenue = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_missing_revenue]=TRUE()))
```

## Identity Conflict Records

```dax
Identity Conflict Records = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[flag_campaign_id_conflict]=TRUE()))
```

## Known Cost All Rows

```dax
Known Cost All Rows = SUM(Fact_Campaigns[total_marketing_cost_cad])
```

## Excluded Known Cost

```dax
Excluded Known Cost = [Known Cost All Rows]-[Total Spend]
```

## Reconstructed Costs

```dax
Reconstructed Costs = CALCULATE(COUNTROWS(Fact_Campaigns),KEEPFILTERS(Fact_Campaigns[cost_basis]="complete component sum"))
```

## Trusted Monthly Spend

```dax
Trusted Monthly Spend = CALCULATE([Total Spend],KEEPFILTERS(Fact_Campaigns[date_eligible]=TRUE()))
```

## Trusted Monthly Revenue

```dax
Trusted Monthly Revenue = CALCULATE([First Month Revenue],KEEPFILTERS(Fact_Campaigns[date_eligible]=TRUE()))
```

## Undated or Conflicted Spend

```dax
Undated or Conflicted Spend = [Total Spend]-[Trusted Monthly Spend]
```

## Zero Output Family Spend

```dax
Zero Output Family Spend = SUMX(FILTER(VALUES(Fact_Campaigns[campaign_family]),[Eligible Records]>0 && NOT ISBLANK([Paying Customers]) && [Paying Customers]=0),[Total Spend])
```

## Zero Output Families

```dax
Zero Output Families = COUNTROWS(FILTER(VALUES(Fact_Campaigns[campaign_family]),[Eligible Records]>0 && NOT ISBLANK([Paying Customers]) && [Paying Customers]=0))
```

## Zero Output Spend Share

```dax
Zero Output Spend Share = DIVIDE([Zero Output Family Spend],[Total Spend])
```

## Review Status

```dax
Review Status = SWITCH(TRUE(),[Eligible Records]=0,"No eligible records",ISBLANK([Paying Customers]),"Missing output",[Paying Customers]=0,"Investigate objective and lag","Evaluate with controlled test")
```

## Funnel Value

```dax
Funnel Value = SWITCH(SELECTEDVALUE(Funnel_Stages[Stage]),"Impressions",[Impressions],"Clicks",[Clicks],"Signups",[Signups],"KYC started",[KYC Started],"KYC completed",[KYC Completed],"Funded accounts",[Funded Accounts],"Paying customers",[Paying Customers])
```

## Quality Issue Records

```dax
Quality Issue Records = SWITCH(SELECTEDVALUE(Quality_Issues[Issue]),"Missing dates",[Missing Dates],"Date conflicts",[Date Conflicts],"Incomplete funnels",[Incomplete Funnels],"Funnel violations",[Funnel Violations],"Missing names",[Missing Names],"Missing channels",[Missing Channels],"Missing segments",[Missing Segments],"Negative spend",[Negative Spend Records],"Missing revenue",[Missing Revenue])
```

## Selected Channel Benchmark CAC

```dax
Selected Channel Benchmark CAC = CALCULATE([CAC],ALLSELECTED(Fact_Campaigns[marketing_channel]))
```

## Above Benchmark Channel Count

```dax
Above Benchmark Channel Count = VAR Benchmark=[Selected Channel Benchmark CAC] RETURN COUNTROWS(FILTER(ALLSELECTED(Fact_Campaigns[marketing_channel]),NOT ISBLANK([CAC]) && [CAC]>Benchmark))
```

## Observed Efficiency Ratio

```dax
Observed Efficiency Ratio = DIVIDE([Selected Channel Benchmark CAC],[CAC])
```

