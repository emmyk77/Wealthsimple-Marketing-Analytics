# Wealthsimple Marketing Analytics

Fictional training data, not actual Wealthsimple business results.

## Power BI dashboard preview

Seven report pages have been opened and populated in Power BI Desktop, as shown in the author's screenshots submitted on 6 November 2026. The screenshots below are actual Desktop captures, not generated design mockups.

![Marketing Spend and CAC dashboard](docs/screenshots/02_spend_and_cac.png)

**[Download the corrected Power BI project](https://github.com/emmyk77/Wealthsimple-Marketing-Analytics/archive/refs/heads/main.zip)** · **[View all seven dashboard pages](docs/Dashboard_Gallery.md)** · **[Check the benchmark and filter results](docs/Budget_Benchmark_Checks.md)**

Extract the repository ZIP and open `powerbi/desktop/Wealthsimple.pbip` on Windows. Set DataRoot to the extracted repository folder and refresh. The revised project distinguishes a valid count of zero from an undefined benchmark. The [7 November Desktop export](powerbi/Wealthsimple_Marketing_Analytics.pbix) and original screenshots predate this model correction.

## Analysis

The source contains 2,000 campaign records. A conservative comparison population of 1,671 records has complete, nonnegative and sequential funnel counts, including KYC, and usable marketing costs.

| Metric | Comparable population |
|---|---:|
| Marketing cost (CAD) | 426,714.30 |
| Signups | 13,700 |
| Funded accounts | 1,673 |
| Recorded paying customers | 106 |
| Signup-to-paying rate | 0.77% |
| CAC (CAD) | 4,025.61 |

![Channel comparison](docs/images/channel_allocation.png)

## Method and limitations

Raw data is preserved. Negative numbers become null, never their absolute values. Missing total cost is reconstructed only when all three components are available. Inconsistent funnel records remain in the dataset with explicit eligibility flags. Costs and customer counts use the same population. Ratios use aggregate numerators and denominators. Zero customers produce undefined CAC.

The sequential funnel assumes each record describes a comparable cohort. This assumption requires validation before real-world use. Counts are recorded events and cannot establish unique acquired people without customer identifiers. Revenue covers only the first month. Zero revenue is not evidence of missing attribution, and revenue less marketing cost is not accounting profit. Campaign IDs map to multiple names in 286 cases, so the composite ID and name is used for detailed grouping. Campaign families are separately defined by channel and name.

Date conflicts with the campaign ID month are retained but excluded from trusted trends. This does not prove which date is correct. There are 102 missing or invalid dates and 107 month conflicts. The supplied date range includes future scenario records and must not be described as completed company performance.

## Reproduce

```bash
pip install -r requirements.txt
python scripts/clean_data.py
python scripts/analyze.py
python scripts/make_charts.py
python -m unittest discover -s tests -v
```

## Files

- `data/raw/`: unchanged input workbook.
- `data/processed/`: cleaned records, field profile, date table and record-level audit log.
- `data/analysis/`: reconciled metrics by channel, campaign, family, objective, product, device, segment and province, plus sensitivity analysis.
- `docs/images/`: seven regenerated analytical charts.
- `docs/screenshots/`: seven unaltered Power BI Desktop captures, with a source/hash manifest.
- `docs/Dashboard_Gallery.md`: dashboard previews and page-specific review notes.
- `scripts/`: portable Python pipeline and category mappings.
- `tests/`: nine integrity and reconciliation tests.

## Deliverables and Power BI status

- [Two-page recommendation report](reports/Wealthsimple_Recommendation_Report.docx)
- [Executive presentation — ten editable slides](reports/Wealthsimple_Executive_Deck.pptx)
- [Power BI source project and Desktop instructions](powerbi/START_HERE.md)
- [55-measure DAX catalogue](powerbi/DAX_Measures.md)
- [Brief compliance and submission checklist](docs/Brief_Compliance.md)
- [Analysis methodology](docs/Analysis_Methodology.md)

The author's screenshots show all seven pages populated in the earlier Desktop export. The corrected project's budget measure has been checked against the campaign records for unfiltered, single-channel, multi-channel, family and month selections. The next Desktop check is to refresh that project, run the supplied DAX query, test the slicers and save and reopen a new PBIX. [Expected values and Desktop steps](docs/Budget_Benchmark_Checks.md).

The Power BI source reads the unchanged Excel workbook through Power Query; the processed Python outputs provide the independent validation baseline. No Power BI Service deployment or public interactive dashboard is claimed.

