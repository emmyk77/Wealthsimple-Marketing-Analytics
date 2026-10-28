# Analytical method and decision limits

## Unit of analysis and identity

The raw workbook has 2,000 campaign records. These are aggregated observations, not individual customers. Recorded customer counts cannot establish deduplicated acquired people. A campaign ID alone is not unique in meaning: 286 IDs map to multiple names. Detailed analysis uses ID plus name (1,841 keys); strategic family analysis uses channel plus name (35 families).

## Cleaning decisions

Raw data remains unchanged. Currency symbols, CAD text and thousands separators are parsed; negative numbers, invalid text and fractional counts become null. No negative is converted to its absolute value. Missing cost can be reconstructed only when ad spend, agency fee and incentive cost are all valid. Total/component mismatches above CAD 0.021 are excluded from comparable cost analysis. A reported total does not override a negative raw component for eligibility.

Channels, provinces, devices and segments use explicit mapping dictionaries. Unknown categories remain visible. Dates use documented explicit formats; date-versus-campaign-month conflicts are flagged without guessing which source is correct. Dates outside the present are synthetic scenario dates, not a realized performance forecast.

## Populations

| Population | Records | Recorded paying customers | Use |
|---|---:|---:|---|
| All source records, numeric counts without sequence validation | 2,000 | 607 | Audit sensitivity only |
| Complete sequential funnel | 1,700 | 108 | Funnel sensitivity |
| Sequential funnel plus usable cost | 1,671 | 106 | Headline comparisons and CAC |
| Headline plus trusted date | 1,495 | 96 | Trusted monthly analysis |

The chain is impressions → clicks → signups → KYC started → KYC completed → funded accounts → paying customers. Enforcing it assumes same-record cohort comparability. With independently timed event counts, this assumption could exclude valid activity; validate cohort definitions before operational deployment. All excluded rows remain available in the audit dataset.

Revenue uses 1,646 headline-eligible records with known nonnegative first-month revenue. ROAS additionally requires known ad spend. Every ratio uses matched population sums and returns undefined when its denominator is zero. CAC uses total marketing cost, while ROAS uses ad spend. CPC and CPS in this project use total marketing cost and are labeled consistently.

## Findings and recommendations

The comparison population totals CAD 426,714.30 and 106 recorded paying customers. Paid Search contributes 69; Email and Referral have lower observed CAC but only nine and 13 customers. This supports capped tests, not a guaranteed scaling result. Nineteen zero-output families account for CAD 337,080.43; investigate lag, objectives and attribution before pausing them.

Monthly analysis excludes CAD 39,958.90 of otherwise eligible cost with missing or conflicting dates. Missing monthly values must not be silently presented as zero spend. First-month revenue does not measure margin, payback, retention or lifetime profit. No causal uplift estimate, industry benchmark or commercial CAC target is inferred from this dataset.

## Reproducibility and ownership

`clean_data.py` creates the audit trail; `analyze.py` provides the common metric source; `make_charts.py` regenerates the static figures. The nine pipeline tests cover material invariants and reconciliations. The authored Power Query implementation must independently reconcile to these outputs in Desktop. Changes to population rules should regenerate the report, slides, charts and model together and be recorded in Git history.
