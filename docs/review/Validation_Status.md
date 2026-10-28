# Validation record — 28 October 2026

- Python pipeline: all nine integrity and reconciliation tests pass.
- Recommendation report: two rendered pages visually inspected; layout and tables checked.
- Executive deck: ten rendered slides visually inspected; package, layout, native chart workbook and import checks pass. Three editable charts and six native tables retained. Native Microsoft PowerPoint execution was not tested.
- PBIR: 117 schema-bearing JSON/project files validated against Microsoft public schemas, zero schema errors.
- Model references: 105 native visual bindings, page bounds, non-overlap and relationship endpoints checked.
- Power Query, DAX runtime evaluation, Desktop import/rendering, slicer interaction and refresh: **not executed here**.
- Final PBIX: **not created or certified**. Follow powerbi/START_HERE.md and docs/Brief_Compliance.md.

The rendered document and presentation checks establish their readability in the available rendering tools; they do not validate the Power BI report. The schema and reference checks establish source structure only.

## Syntax correction after Desktop import feedback

The Fact_Campaigns M expression contained a mismatched closing delimiter in Record.Combine. Microsoft Power Query parser 4.0.1 reproduced the failure before the fix. The generator, standalone query and model partition are now corrected. All six embedded M expressions and all three standalone .m files pass lexical and syntax parsing. The 105 visual binding, bounds and relationship checks also pass. Desktop refresh and DAX execution remain pending; syntax validation is not runtime validation.

Run `npm install --no-save @microsoft/powerquery-parser@4.0.1`, then `node scripts/check_powerquery.cjs` from the repository root to repeat the syntax check.

## Column and measure naming correction

Desktop reported that Impressions conflicted with the impressions column. The same case-insensitive collision also affected Clicks and Signups. The model columns are now raw_impressions, raw_clicks and raw_signups; sourceColumn remains the unchanged Power Query field name. The three aggregation expressions and DAX catalogue use the renamed model columns. Dashboard measure names and visual bindings remain unchanged. The generator produces the same targeted fix. The structural validator now rejects case-insensitive column/measure collisions. The original model fails that check; the corrected model has no collisions. All fully qualified Fact_Campaigns column references resolve, and all 105 visual bindings and layout checks pass. Desktop import and refresh still require user verification.
