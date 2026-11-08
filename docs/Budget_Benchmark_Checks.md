# Budget benchmark and funnel checks

The report uses fictional training data. For each selection, the benchmark is eligible marketing spend divided by eligible recorded paying customers. A channel qualifies for the count only if it has a defined CAC above that benchmark. This is a comparison within the selected data, not a target acquisition cost.

Across all channels, the benchmark is CAD 4,025.61. Only five channels recorded paying customers. Their CACs range from CAD 326.52 for Email to CAD 2,432.72 for Affiliate. Every one is below the pooled benchmark, which includes eligible spending on channels that recorded no paying customers. The count is therefore **0**. In the previous model, DAX COUNTROWS returned blank for the empty set of qualifying channels. The corrected model returns 0 for this valid comparison and preserves BLANK when the benchmark itself is undefined.

## Independent control totals

These values were recalculated from the cleaned campaign records, with the same eligible cohort for spend and funnel measures. Month filters use the active trusted-date relationship. Costs and ratios are displayed in CAD.

| Selection | Source rows | Eligible | Spend | Signups | Funded | Paying | Benchmark CAC | Channels above |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All records | 2,000 | 1,671 | 426,714.30 | 13,700 | 1,673 | 106 | 4,025.61 | 0 |
| Paid Search | 372 | 307 | 60,856.81 | 4,344 | 726 | 69 | 881.98 | 0 |
| Paid Search + Email | 526 | 432 | 63,795.53 | 5,183 | 835 | 78 | 817.89 | 1 |
| Paid Social | 390 | 327 | 86,675.16 | 2,500 | 226 | 0 | Undefined | Undefined |
| Trade Account Search family, Paid Search | 98 | 81 | 17,024.90 | 1,326 | 258 | 36 | 472.91 | 0 |
| January 2025 | 108 | 86 | 21,840.75 | 759 | 100 | 6 | 3,640.125 | 0 |

Paid Search is the one channel above the two-channel benchmark. Selecting Paid Social alone leaves both the benchmark and count undefined.

## Open and verify in Power BI Desktop

1. Extract the repository and open `powerbi/desktop/Wealthsimple.pbip`. Set the DataRoot parameter to the extracted repository root, then choose **Close & Apply** and **Refresh**.
2. In DAX query view, paste and run the [control query](../powerbi/Budget_Benchmark_Checks.dax). Compare its six rows with the table above. Exact ratios appear before currency formatting.
3. Open Budget Optimization. Clear all slicers, then select each channel, channel pair, family and period in the table. The count should read 0, 1 or blank according to the comparison.
4. Save a new PBIX, close and reopen it, repeat the two-channel selection, and export the refreshed Budget page.

The original PBIX package was reopened as an archive and checked for integrity, seven pages, its embedded model and its Budget card binding. The corrected DAX is in the editable project and generated baseline. The control totals were checked independently of Desktop. A native refresh, UI slicer test and new PBIX export still require Power BI Desktop on Windows. The gallery retains the original Desktop capture.
