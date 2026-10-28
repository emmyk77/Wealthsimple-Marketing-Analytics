# Open and validate the Power BI project

This is an authored source project, not a Desktop-tested PBIX. It contains seven pages, 105 native visual definitions, 55 DAX measures and Power Query transformations. No credentials, service connection or embedded data cache is included. The supplied workbook is fictional training data.

## Desktop steps

1. Download the **whole repository** using GitHub → Code → Download ZIP, then extract it. Keep its folder structure.
2. Install/open a current Power BI Desktop on Windows with Power BI project and enhanced report format support. Open `powerbi/Wealthsimple.pbip`. If your installed version rejects the source format, update Desktop; do not rename PBIP to PBIX.
3. Open Transform data → Manage parameters. Set `DataRoot` to the extracted repository folder, for example `C:/Projects/Wealthsimple-Marketing-Analytics`. The folder must contain `data/raw/Power_BI_project.xlsx`. The initial `C:/CHANGE_ME/...` path is deliberately a placeholder.
4. Refresh the queries and Close & Apply. `Raw_Campaigns` reads Sheet1 from the workbook. `Fact_Campaigns` performs the transformations in Power Query; it does not import the pre-cleaned CSV. The Python CSV is an independent reference for reconciliation.
5. Import `Wealthsimple_Theme.json` through View → Themes → Browse for themes. It is supplied separately to avoid an unverified theme resource reference.
6. Check Model view: one active, single-direction relationship from `Dim_Date[Date]` (one) to `Fact_Campaigns[trend_date]` (many). Mark Dim_Date as the date table using Date. The funnel and quality helper tables are intentionally disconnected.
7. Clear all slicers. Run `Wealthsimple.SemanticModel/DAXQueries/Reconcile.dax` in DAX Query view and compare every value against the table below. Stop and investigate any difference; do not edit displayed totals to force agreement.
8. Visit all seven pages. Confirm cards, bars, tables, funnel, scatter and line charts render; confirm each slicer filters the intended visuals and stays synchronized across pages. If Desktop changes a native visual role during import, rebind it using the page specification. Set slicers to dropdowns for compactness. Format currency as CAD and percentages as percentages.
9. Follow `../docs/Brief_Compliance.md` for the remaining presentation refinements, especially the Canadian map, heatmap, drill-through and final accessibility checks. The source project covers the analytical pages but does not claim every requested visual treatment is complete.
10. Add the persistent page footer **“Fictional training data · CAD · Comparable cohort unless stated”**. Add a tooltip explaining eligibility and first-month revenue. Test keyboard navigation, titles, scrolling tables, blank CAC, and a single-channel/single-month selection.
11. Save the project, then use Save As to create `Wealthsimple_Marketing_Analytics.pbix`. Reopen that PBIX, refresh again, and export screenshots for the README. Only after these checks mark the Power BI deliverable complete.

## Reconciliation with all filters cleared

| Measure | Expected |
|---|---:|
| Source Records | 2,000 |
| Eligible Records | 1,671 |
| Total Spend | CAD 426,714.30 |
| Paying Customers | 106 |
| CAC | CAD 4,025.6066 |
| Signups | 13,700 |
| Funded Accounts | 1,673 |
| Signup to Paying | 0.7737226% |
| First Month Revenue | CAD 4,688.80 |
| Revenue Records | 1,646 |
| ROAS (revenue / ad spend, matched rows) | 0.0135336183x |
| Zero Output Family Spend | CAD 337,080.43 |
| Zero Output Families | 19 |
| Trusted Monthly Spend | CAD 386,755.40 |
| Undated or Conflicted Spend | CAD 39,958.90 |
| Missing Dates | 102 |
| Date Conflicts | 107 |
| Incomplete Funnels | 169 |
| Funnel Violations | 142 |
| Reconstructed Costs | 72 |

Money tolerance: CAD 0.01; count tolerance: zero. Ratios may differ only in display rounding. Issue counts overlap. The date relationship uses trusted dates: selecting a period intentionally removes records without an unconflicted date, so filtered cards will differ from all-period totals. Monthly revenue and spend are separate measures with separately stated coverage; use ROAS for a matched return ratio.

## Model and calculation notes

`Raw_Campaigns` is an M expression available to Fact_Campaigns, not a loaded model table. The model contains Fact_Campaigns, Dim_Date, Funnel_Stages and Quality_Issues. Campaign key is ID + name; campaign family is channel + name. A family can span objectives and dates, so inspect those filters before deciding on a budget action.

Funnel eligibility requires all seven nonnegative stages in order, including KYC. This assumes a comparable cohort in each record and must be confirmed with a real source owner. Cost eligibility requires a known total, no negative raw component and no material component mismatch. Missing totals are reconstructed only from all three valid components. Revenue and ROAS use additional availability flags, keeping numerator and denominator populations aligned. Undefined CAC remains blank. Zero recorded output is a review signal, not proof of waste.

The supplied Power Query implements the analytical subset used in the report. Additional Python audit fields such as UTM normalization, CRM flags and 3-IQR review flags remain available in the processed CSV and issue log; they are not all loaded into the compact Power BI model. Do not present Power Query as a byte-for-byte copy of all Python audit columns.

## Credentials and publishing

This is a local-file analytics project with no application login, API tokens or authentication middleware. Desktop reads the workbook using the current user's file permissions. Do not commit `.pbi` caches, local settings, tokens or passwords. A Power BI Service deployment is a separate step: configure a supported refresh source/gateway and access controls there; GitHub publication does not publish an interactive report to Power BI Service. No service deployment has been performed.

## Technical references

- [Microsoft: Power BI Desktop projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Microsoft: semantic model files and model.bim](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset)
- [Microsoft: PBIR report files](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)

Microsoft's public JSON schemas are referenced by the report definition files. JSON validation can check structure; it cannot prove that M, DAX, visual roles or refresh behavior execute correctly in Desktop.
