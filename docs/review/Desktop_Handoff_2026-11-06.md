# Desktop handoff — 6 November 2026

**Update, 7 November 2026.** The author supplied the [complete PBIX](../../powerbi/Wealthsimple_Marketing_Analytics.pbix). The archive integrity check passed. All seven expected pages are visible in the report definition and the embedded data model is present. SHA-256: `860dff3c9d6863ccb3e15b19667959928ed90e9bc4fc4ffbe88d5f6b1de4c1f1`. Step 2 below is complete for file delivery. The remaining work includes supplying the Desktop-saved project folders and testing refresh, measures and slicers in Desktop. The record below describes the original 6 November submission.

## Current delivery status

Seven actual Power BI Desktop screenshots are now available in the [dashboard gallery](../Dashboard_Gallery.md). All seven pages display populated visuals. The author has applied a consistent grey, white and red layout and reduced the visible slicers.

Visible reconciliation evidence:
| Item | Screenshot value |
|---|---:|
| Source records | 2,000 |
| Eligible records | 1,671 |
| Excluded records | 329 |
| Reconstructed-cost records | 72 |
| Marketing spend | CAD 426,714.30 |
| Paying customers | 106 |
| CAC | CAD 4,025.61 |
| Signup-to-paying rate | 0.77% |
| First-month revenue | CAD 4,688.80 |

These observations do not replace DAX execution against the final package. The local Power BI application was not executed by the repository updater, and screenshots cannot verify slicer interactions or every calculation.

## The uploaded file is not the full project

The submitted [Wealthsimple back up.pbip](submissions/2026-11-06/Wealthsimple%20back%20up.pbip) is a **192-byte JSON launcher**. Its report reference is:

```json
{"report": {"path": "Wealthsimple back up.Report"}}
```

The referenced report folder was not included. Neither the matching semantic-model folder nor a final PBIX was uploaded. The launcher is archived unchanged as submission evidence; it cannot reproduce the latest report by itself. The source baseline under `powerbi/` has different report-folder naming and must not be represented as the author's latest saved formatting.

## Included in this repository update

- Seven original PNG screenshots, named in report-page order.
- Dashboard gallery, README preview, screenshot hash manifest and this status record.
- Unchanged submitted launcher, clearly marked incomplete.
- The previously diagnosed PBIR content-version fix: `definition/version.json` changes from `4.0.0` to `2.0.0`. The separate `definition.pbir` version remains `4.0`.
- The source generator retains that version fix; the offline structure checker rejects a regression to the problematic content version.
- Existing data, calculations, reports, slides and authored layout remain intact. No attempt is made to reconstruct the latest editable visuals from screenshots.

## Required next steps

1. **Supply the full current editable source.** In Desktop, save and close the project. In File Explorer, locate `Wealthsimple back up.pbip`. ZIP that launcher together with `Wealthsimple back up.Report` and the semantic-model folder referenced by its `definition.pbir`. Preserve relative folder paths. Include any local report resources. Exclude `.pbi` caches and credentials from a copy of the project, not your working original.
2. **Supply the final PBIX.** Use Desktop → File → Save As → Power BI file (*.pbix), naming it `Wealthsimple_Marketing_Analytics.pbix`. Reopen the PBIX and refresh. Renaming a PBIP extension is not conversion. A PBIX supplies a convenient runnable deliverable; the source ZIP is needed to synchronise the GitHub-editable layout.
3. **Resolve the blank Budget card.** Inspect Above Benchmark Channel Count. Either correct and reconcile it, or bind the card to Selected Channel Benchmark CAC and clearly rename it. Keep the original measure available for diagnosis. Do not report blank as zero.
4. **Run full reconciliation.** Clear filters and run `powerbi/Wealthsimple.SemanticModel/DAXQueries/Reconcile.dax`; also compare the extended expected values in `powerbi/START_HERE.md`. Keep matched revenue, matched ad spend and matched marketing cost distinct. Test no-data selections and undefined CAC.
5. **Test report interactions.** Check each retained slicer, any hidden synced slicers, chart selections, page filters, date coverage, sorting, and tooltips. Confirm totals return when filters clear.
6. **Finish visual corrections.** Correct “Costomer” to “Customer”; label revenue currency; improve the funnel's small-stage readability, table widths and technical headings. Restore overlapping-issue, fictional-data, population, first-month-return and zero-output interpretation notes. Hide backup pages in the presentation.
7. **Recapture clean screenshots.** Deselect visuals, move the pointer outside the canvas and capture the complete page without hover buttons, tab tooltips or clipped borders. Preserve the underlying data and categories.
8. **Synchronise and release.** Replace the authored baseline with the actual Desktop-saved folders, normalise machine-specific source paths to a documented DataRoot parameter, rerun suitable source checks, and update status only after the PBIX reopen/refresh checks pass. Review the original brief's optional or assessor-specific visuals separately.

## Remaining brief-specific review

The [brief checklist](../Brief_Compliance.md) still lists features such as a Canada map, heatmap, drill-through and ranking controls. The screenshots do not demonstrate all of these. Assess them against the actual submission requirements rather than describing them as already complete.

GitHub hosts the source and preview images. Publishing an interactive report to Power BI Service is a separate optional deployment, with its own access and refresh configuration.

