# Brief compliance and final submission checklist

Basis: supplied “FinTech Marketing Spend Efficiency, Customer Acquisition Cost, and Paid Customer Conversion Analysis in Wealthsimple Canada” project brief. This is a fictional training exercise. The original brief's June 2026 dates are historical; this revision is dated 28 October 2026 and makes no on-time submission claim.

## Deliverables

| Brief requirement | Delivered evidence | Status |
|---|---|---|
| Short recommendation report, 1–2 pages | `reports/Wealthsimple_Recommendation_Report.docx` | Completed; two pages visually checked |
| Executive summary PPTX or PDF | `reports/Wealthsimple_Executive_Deck.pptx` | Completed; ten editable slides |
| Data cleaning, standardized categories, auditable issues | Python pipeline, processed records and issue log | Completed and reconciled |
| Power Query cleaning | `powerbi/powerquery/` and model partitions | Authored; Desktop execution pending |
| DAX measures and data model | `powerbi/DAX_Measures.md`, model.bim | Authored; Desktop execution pending |
| Seven interactive dashboard pages | Native PBIR pages in `powerbi/Wealthsimple.Report/definition/` | Authored; rendering and interactions pending |
| Final `.pbix` | Not supplied | Requires Desktop refresh, checks and Save As |

## Seven-page coverage

| Page | Source project includes | Desktop refinements / acceptance criteria |
|---|---|---|
| Data Quality | Source/eligible/excluded/rebuilt cards; issue bars; missing field and diagnostic tables | Add conditional background colors to make the table a heatmap; add raw-versus-standardized channel comparison from Python field profile. Explicitly distinguish completeness from validity; retain overlapping issue labels. |
| Spend and CAC | Cost/CAC/CPC/CPS cards; channel cost and CAC; trusted monthly trend; campaign family table | Add region drill-down and spend-share donut if required by assessor; sort cost descending, show blank CAC as undefined; test family selection. |
| Conversion Funnel | Seven stages including KYC; four conversion cards; channel/segment conversion bars; detailed campaign table | Ensure stage sorting follows helper Sort; show stage drop-off in tooltips or additional cards; validate filters preserve the same population. |
| Channel and Campaign | Channel scorecard; family customer ranking; cost/customer scatter; objective/status table | Add top/bottom ranking controls and drill-through. Efficiency ratio is defined relative to selected-channel blended CAC, not an invented weighted score. |
| Revenue and ROAS | Revenue/ROAS/ARPC/gap cards; trusted revenue trend; revenue and ROAS bars; matched family table | Add matched cost to the revenue trend if desired using an explicitly matched dated-cost measure. Add low-ROAS counts with a clearly labeled 1x first-month revenue/ad-spend threshold. Avoid calling positive revenue-cost gap accounting profit. |
| Segment and Region | Province customer bar; segment/device/product tables; conversion/CAC/ROAS cards | Add a Canada map using full province names and country Canada; verify geocoding. Include province ROAS and product filters. Bar remains a readable map fallback. |
| Budget Optimization | Zero-output cost/count/share; above-blended-CAC count; objective review queue; channel test candidates | Add an explicitly hypothetical reallocation parameter only if requested by assessor. Set assumptions visibly; do not forecast causal uplift from historical CAC. No automatic pause/scale recommendations. |

Shared slicers cover channel, campaign family, province, segment, device, product and period. Detailed campaign keys are available in the funnel table; add a campaign-key slicer when record-level campaign filtering is required. Family is a deliberate grouping, not a claim that campaign IDs are unique.

## Interpretation changes from the earlier draft

- Replace the unvalidated 607-customer headline and 3.7% signup conversion with 106 recorded customers and 0.77% in the stated comparison population. Keep the sensitivity analysis visible; the strict cohort assumption is not a proven fact about the business.
- Replace absolute-value repair of negative costs with null plus audit flags. Do not translate arbitrary words into numbers.
- Do not label the late-period spend fall as a real business cut: dates are synthetic and some conflict with campaign identifiers.
- Replace unconditional “wasted spend” with “zero-output spend requiring review”; objectives, lag and attribution need validation.
- Replace an arbitrary CAD 400 CAC target with finance-approved payback economics. Relative CAC is descriptive only.
- Report first-month return separately from lifetime profitability and distinguish zero revenue from missing revenue.

## Sign-off before submitting the PBIX

- [ ] Refresh M queries successfully from the unchanged workbook.
- [ ] Run DAX reconciliation with slicers cleared; all expected counts and amounts match.
- [ ] Test every slicer, cross-filter, sort order, tooltip and empty selection.
- [ ] Verify the seven page refinements above against the assessor's visual checklist.
- [ ] Label synthetic data, CAD, populations and first-month revenue on report pages.
- [ ] Confirm no personal paths, credentials or caches are included in the published source.
- [ ] Save and reopen the PBIX; export real dashboard screenshots.
- [ ] Update README status only after successful Desktop validation.
