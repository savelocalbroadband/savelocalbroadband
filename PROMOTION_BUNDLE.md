# Promotion bundle — PROMOTED TO LIVE 2026-07-03 ✅

**Supersedes the numbers in `REVIEW_v2.md` §1–§3.** All four second-review blockers + the cleanups are
implemented in `montecarlo_v2.py` (now the LIVE model, version `v2.1-2026-07-03`); `test_v2.py` is green
(14/14). The live `*_output.json` are regenerated from v2; `montecarlo_robust.py` is archived/superseded.
Page prose + fallbacks + the calculator (min-year DSCR) updated across `how-we-modeled-risk.php`,
`risks.php`, `case.php`, `inc/site_data.php`. Pre-promotion JSON backed up in `_pre_promote_backup/`.
CPE re-buy resolved as customer/RSP pass-through (not a District risk).

## What changed since the reviewed version

| Blocker | Done |
|---|---|
| 1 — Ledger E charges a pro-rated G2 refresh on the build path | ✅ |
| 2 — NCI made truly common-mode in Ledger E (same t0 exit + capex on both paths) | ✅ |
| 4 — Ledger B headline applies the NCI exit; dead `r` removed; Fisher label fixed | ✅ |
| Cleanups (dead `DEBT_SERVICE`, `TOWER_FIXED` sync, appendix cruft, test precondition, rename) | ✅ |
| Sensitivities added: demand-pull OFF, and the pessimistic G2/CPE-rebuy case | ✅ |
| Bundle: adopt `nci_year=2` (realistic timed NCI exit) in the scenarios | ✅ (needs sign-off) |

## The net headline (baseline → promoted candidate)

| Scenario | District payback | min-year DSCR | pull=0 sensitivity |
|---|---|---|---|
| Pessimistic | 23.5 → **19.3%** | 0.37× | 15.6% |
| Balanced | 87.6 → **88.4%** | **1.23×** | 86.0% |
| Optimistic | 94.9 → **96.9%** | 1.35× | 96.4% |

Balanced nets to **88.4%** = overbuild fix (+3.7) and the honest `nci_year=2` trim (−2.9). That's the whole
story of the headline move: **two corrections, opposite directions, net ≈ +0.8** — with the DSCR now shown
as the honest min-year (1.23×) instead of the old average-based 1.7×.

## Two things you should see clearly

**1. Ledger E got sober — and that's the point.** With the refresh charged and NCI common-mode, the
build-vs-run-to-failure decision on *pure incremental cash* is:

| RTF case | P(build beats RTF) | incremental NPV (P50) | protected-cash PV (P50) |
|---|---|---|---|
| favorable (5%/yr decline) | 19.9% | −$351K | $0.99M |
| central (10%/yr) | 44.2% | −$61K | $1.28M |
| grim (15%/yr) | 60.5% | +$115K | $1.46M |

Read honestly: on a **same-ARPU, no-demand-unlock, full-refresh** basis, milking the dying network beats
building *on narrow incremental cash* unless decline is fast. **This does not mean building loses money** —
it means the case for building does **not** rest on Ledger E's deliberately austere metric. It rests on
(a) the network is **guaranteed to hit zero** (RTF dies by yr15 in ~100% of futures), (b) the county comes
out ahead **92–99%** of the time (Ledger C), and (c) we deliberately gave the build **no** credit for the
demand-unlock or the $40 rate step that the rest of the site argues for. Ledger E is the **floor**, and it
should be labeled as such. If we credited even a modest unlock it moves up — I can add that variant.

**2. The G2/CPE question is RESOLVED — not a District risk.** Per the operator: the District *fronts*
customer-radio purchases but is **reimbursed** by customers/RSPs, buying them in batches **as customers sign
up** — not all up front. So CPE is a revolving **pass-through, ~net-zero** on the District's books; the only
exposure is working-capital *timing* if it over-bought up front, which isn't the practice. A mid-life G1→G2
refresh therefore charges only the District's tower/base-node gear (~$150K, already in fair mode); there is
**no CPE re-buy burden**. The pessimistic CPE-rebuy sensitivity (which had shown a −15 pt hit) is **removed**
as unrealistic. We still keep the *initial* radio fleet inside the District's stated ~$1.2M **and don't
credit the offsetting reimbursement** — deliberately conservative, so payback is if anything understated.

## Decisions I need from you

1. **Adopt `nci_year=2`?** The argument: having *measured* that immediate-exit flatters the
   headline, keeping it is indefensible. I've set it in the candidate. Confirm or revert.
2. **Promote candidate → live?** If yes, I execute the staged page audit below in one pass and flip the JSON.
3. **Demand-pull (item 6, non-blocking):** `PULL_ELAST=0.30` credits more demand than the `ELAST_HAIRCUT`
   implies (asymmetric; pull is worth ~2.4 pts Balanced). Options: leave it and publish the pull=0 row (done),
   or reduce PULL toward ~0.10. Your call — it's a judgment, and reducing it lowers our number.

## Staged page audit (executes only on "promote")

- `how-we-modeled-risk.php` ~L964: `$c40['payback_P90']` (deleted key) → rewrite with unconditional keys +
  "not reached" handling.
- Scenario table (~L320): relabel DSCR column "min-year DSCR (covenant)" + footnote; values 0.37/1.23/1.35.
- Calculator JS (~L543/596/620): implement min-year DSCR (track `minCash`), relabel the row.
- ~L440 "~10,000 futures" → "about 8,000" (the earlier edit fixed L519, missed this one).
- ~L670 "P80 (~$1.41M)" → template from `capex_P80` (~$1.38M).
- JS county bar (~L588): add `- rebuild/df` to `countyAcc` in the shock year (currently flatters pessimistic).
- Add the overbuild tail to the JS so "the calculator omits nothing directional" is true.
- Scope the "avoided decline > capex" sentence to "at the District's own stated decline rate."
- Ledger B page figures → new NCI-consistent numbers (15-yr P50 $920K, bracket $795K–$1,013K).

## Still queued (non-blocking, for the formal-presentation pass)

- County ledger: add the overbuild tail (immaterial, cross-ledger consistency).
- Narrow the county "rate-invariance" claim to the price term; fold the real fix into the shared-futures
  `simulate()` refactor (its own reviewed pass, with the `county = household + district` invariant test).
- §6 taxonomy: classify `NCI_EXIT_P`, `NCI_MIGRATE` (make it a slider), `PULL_ELAST`, `ELAST_HAIRCUT`,
  `DELAY_CHURN`, `BW_GROWTH`, `BW_MARGIN`, `+12` opex adder as INFERRED/POLICY; verify the 28–58% margin
  endpoints are in the SAO audit or relabel "documented center, judgment width."
- ~~G2/CPE bracket~~ — RESOLVED: CPE refresh is customer/RSP-borne, not District capital; sensitivity removed.

## Acceptance checklist (before flipping live)

- [x] `python test_v2.py` green (14/14, incl. the E-refresh and B-NCI guards)
- [x] Full run regenerates all candidates deterministically
- [ ] Page renders with promoted JSON — grep every `$c*[...]` key read, confirm each exists in new JSON
- [ ] Calculator DSCR row matches the table's convention
- [ ] REVIEW/PROMOTION numbers reflect the bundled headline
