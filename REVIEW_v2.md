> ⚠️ **Superseded by `PROMOTION_BUNDLE.md`** for final numbers. After the second review, four blockers were
> implemented (pro-rated refresh + NCI common-mode in Ledger E, NCI-consistent Ledger B, `nci_year=2` bundle),
> which moved Balanced to **88.4%** and made Ledger E more conservative. The narrative below is the original
> v2 review; the tables in §1–§3 are the pre-promotion figures.

# Monte Carlo v2 — review package

**Model:** `montecarlo_v2.py` (version `v2-2026-07-02`) · **Tests:** `python test_v2.py` · **Run:** `python montecarlo_v2.py`

**Nothing live changed.** The live model (`montecarlo_robust.py`) and the JSON the site reads
(`scenarios_output.json`) are **untouched**. v2 writes to `*.candidate.json`. Baseline snapshot for
diffing: `scenarios_output.baseline.json`. Promotion to live is a **separate decision** after review.

Two live *page* edits were made, both purely factual and independent of any number: the calculator
caption "~10,000 iterations" → "about 8,000" (the JS actually runs 8,000). See the "same futures" note
in §4 — I did **not** change that sentence, because it's correct for what it describes.

---

## 1. Headline movement — and it's all one bug

The only published number that moves is the District payback, and **100% of the movement is the
overbuild fix** (the fiber-overbuild loss was being re-applied every year instead of once). County
numbers are byte-identical because overbuild never existed in that ledger.

| Scenario | District payback (baseline → candidate) | Driver |
|---|---|---|
| Pessimistic | 23.5% → **24.4%** (+0.9) | overbuild one-time fix |
| Balanced | 87.6% → **91.3%** (+3.7) | overbuild one-time fix |
| Optimistic | 94.9% → **98.1%** (+3.2) | overbuild one-time fix |

Direction is *toward* us, because the bug was over-penalizing. It is nonetheless a **correct** fix
(regression-guarded in `test_v2.py`: a 15% overbuild now produces one 15% step, not `0.85^n`).

Everything else below is **new disclosure**, not a re-baselining of an existing number.

---

## 2. New honest disclosures

**Payback timing is now reported two ways** (it was silently conditional-on-success before):
- *Conditional* (among futures that recover): Balanced P50 **8.6 yr**, P80 **9.8 yr** — unchanged meaning, now labeled.
- *Unconditional* (across all futures; "not reached" when the success rate is below the percentile):
  Balanced P80 **11.9 yr**, P90 exists (91% recover); **Pessimistic P80/P90 = "not reached"** (only 24% ever recover — the old finite `payback_P90` was misleading here).
- *Recovered-by-year* (all futures): Balanced **66% by yr10, 91% by yr15**; Pessimistic **19%/24%**.

**DSCR is now annual, not a horizon average.** The old "1.7×" for Balanced was average-cash ÷ debt
service — it hid low-coverage years. New:

| Scenario | DSCR yr-1 | DSCR **min-year** (covenant metric) | P(min < 1.0) |
|---|---|---|---|
| Pessimistic | 1.32× | **0.39×** | 95.5% |
| Balanced | 1.39× | **1.27×** | 25.7% |
| Optimistic | 1.41× | **1.38×** | 7.8% |

Debt service is now sized on the **funded P80 capex ($1.38M)**, not the $1.178M sticker. This is
strictly more conservative and it's the number a bond analyst reads. The old average figure is retained
but renamed `avg_cash_coverage`.

**Bandwidth is now an overlap bracket, not a clean claim.** We can't derive an access-only margin
(no cost allocation — the other model was right). So we bracket how much of the $193K bandwidth line the
audited *segment* margin might already contain:

| Overlap assumed | Balanced payback | Meaning |
|---|---|---|
| 100% (margin already holds all of it) | **81.0%** | overlap-proof floor — add *no* separate bandwidth |
| 50% | **93.4%** | add half |
| 0% (margin holds none) | **98.2%** | add the full documented ~2.8 Mbps |

The published 1.0-Mbps headline sits at **~64% assumed overlap** — i.e. already conservative. Even the
overlap-proof floor (add zero bandwidth) is **81%** for Balanced.

---

## 3. Build-now vs run-to-failure — the incremental decision (NEW, ledger E)

This is the analysis you asked for. Both paths run on the **same drawn future**; NCI is common-mode and
cancels; same ARPU on both (we do **not** credit "build" with the $40 rate step); the build path uses the
**conservative** growth (mode 0, can be negative — it does *not* credit the demand-unlock you described).
Decline rate and remaining life are **bracketed scenarios**, and the seasonal recovery-decay is a
**labeled inferred** parameter — none of it is dressed up as documented.

| Run-to-failure case | median death yr | P(build beats RTF) | incremental NPV (P50) | avoided-decline PV (P50) |
|---|---|---|---|---|
| status-quo favorable (5%/yr) | yr 8 | 25.6% | **−$291K** | $1.09M |
| central (10%/yr) | yr 5 | 52.5% | **+$28K** | $1.41M |
| status-quo grim (15%/yr) | yr 3 | 68.1% | **+$223K** | $1.60M |

**Read this honestly — it is not a slam dunk, and that's what makes it credible:**

- The status quo is **guaranteed to die** (RTF shuts down by year 15 in ~100% of futures, all cases).
- On **pure incremental cash**, the case for building *depends on how fast the old network declines.*
  If you assume it limps along 8 years keeping most customers (the "favorable" case), building **loses**
  on NPV — you'd have collected much of that cash anyway without spending $1.2M.
- **But that favorable case contradicts the District's own deck** — "lost 39 in February, ~10/week"
  (≈13%/yr) and "no possibility for expansion." At the **documented** decline rate (central/grim),
  building is coin-flip-to-favorable *and* protects **$1.4–1.6M** of avoided decline.
- The build side is deliberately under-credited (no demand-unlock, no rate step, conservative growth), so
  these are **floors**. Crediting the unlock would move them up.

**One site claim needs a caveat as a result:** the page says the PV of avoided decline "is larger than
the capex itself." That's true at the documented decline rate (central/grim: $1.4–1.6M > ~$1.27M capex),
but **roughly break-even** in the slow-decline favorable case ($1.09M). Recommend scoping that sentence to
"at the District's own stated decline rate."

---

## 4. Corrections to my own earlier audit (honesty log)

- **NCI exit timing** — I predicted immediate exit was conservative and timing "would help." **Measured,
  it's the opposite:** a realistic timed exit strands purchased radios, trimming Balanced payback from
  91.2% (t0 default) to ~88–89% (exit yr 2–3). Small, but the current default slightly *flatters* the
  headline. Added as a scn option (`nci_year`, default 0 = current behavior, so the headline is unchanged
  unless we choose to adopt it).
- **"Same futures" sentence (page line 512)** — I agreed too fast that this was a misstatement. It
  describes the **interactive calculator**, and the JS computes both bars in one shared-draw loop, so it's
  **correct**. The real (narrower) gap is that the *Python* model's published District vs county numbers
  use different seeds — an internal-consistency item, not a website error. Left the sentence alone.
- **Phasing** — I cautioned per-site data might not exist. **It does** (`site_data.php:249`, per-tower
  customers + cost). Phasing is buildable. Cost-per-customer ranking, lowest first:
  Eder $1,139 · Jackass Butte $1,187 · Coleman $1,338 · Number Hill $1,361 · Nortons $1,504 · Pickens
  $1,509 · Shellrock $2,122. (Top 3 = 543 of 878 customers, 62%, for $658K = 56% of capex.)

---

## 5. Status of the 9 code-audit findings

| # | Finding | Status in v2 |
|---|---|---|
| 1 | Overbuild re-applied yearly | **Fixed** + regression test |
| 2 | Obsolescence hazard claimed, not implemented | **Removed the claim** (would double-count effective life) |
| 3 | NCI exit timing absent | **Added as option**, measured (§4); default unchanged |
| 4 | Percentiles conditional, described as unconditional | **Both reported**, "not reached" honored |
| 5 | District/county use different draws | **Not yet unified** (Python); calculator already shares — see §7 |
| 6 | Refresh = base-node only; capex includes CPE | **Open engineering question** — see §7 |
| 7 | Bandwidth may double-count segment margin | **Reframed as overlap bracket** (§2) |
| 8 | DSCR = average, not minimum | **Fixed** — annual + min, sized on funded P80 (§2) |
| 9 | Stale comments | **Cleaned** (p=0.4→0.85, obsolescence claim, iteration count) |

---

## 6. Input taxonomy (as requested — preserved)

- **Documented (PUD records):** capex $1.178M bottom-up + per-site costs/customers; 878 customers; $40
  proposed rate; ~$31.2 current rate; $1.14M access + $193K bandwidth lines; ~10/week loss, 39 in Feb,
  ~16% off peak; audited segment margin range 28–58%; 2020 bond TIC ~2.9%.
- **Calculated:** payback/NPV/DSCR/percentiles; per-customer implied ~2.8 Mbps; cost-per-customer ranking.
- **Inferred (labeled):** run-to-failure decline rates + remaining-life brackets; seasonal recovery-decay;
  bandwidth overlap fraction; AACE contingency shape; Starlink churn ramp.
- **Policy judgments:** rate-track lever (flat vs cost-recovering); for-profit premium; cliff vs full-life
  accounting.
- **User-adjustable (calculator sliders):** ARPU, margin, overrun, inflation, gear life, NCI prob, delay,
  rate-track, premium, bandwidth Mbps + price.

---

## 7. Decisions / open items for the second review

1. **Promote candidate → live?** The overbuild fix is correct and moves Balanced 87.6→91.3. If we promote,
   we should also decide whether to adopt the **NCI-timing** trim (91.3→~89) and switch the site's DSCR to
   the honest **min-year** figure (1.7→1.27) at the same time, so the net headline is presented cleanly.
2. **The "avoided decline > capex" sentence** — scope it to the documented decline rate (§3).
3. **G2/CPE refresh (finding #6)** — needs a vendor/engineering fact: do G1 customer radios work on G2 base
   nodes, or must CPE be re-bought at refresh? If CPE swaps, the ~$150K refresh is understated and the
   fair-method (Balanced) payback is optimistic. **I can't resolve this from the records.**
4. **Python shared-futures unification (finding #5)** — the clean fix is one `simulate()` drawing the shared
   primitives once, feeding District + county, with an invariant test `county = household + district`. It's
   a real refactor of a working model; I recommend it as its **own** reviewed pass, not folded in here.
5. **Phasing (now confirmed buildable)** — one more module: rank sites by cost-per-customer, compare
   build-all-now vs phase-best-3-first vs run-to-failure on shared futures. Ready to build on your word.

---

## 8. Files

- **New:** `montecarlo_v2.py`, `test_v2.py`, `run_to_failure_output.candidate.json`, this doc,
  `scenarios_output.baseline.json`.
- **Candidate outputs:** `scenarios_output.candidate.json`, `county_value_output.candidate.json`,
  `montecarlo_robust_output.candidate.json`, `ratepayer_benefit_output.candidate.json`.
- **Live edits:** `how-we-modeled-risk.php` (iteration-count text only).
- **Untouched live:** `montecarlo_robust.py`, `scenarios_output.json` and the other live JSON.
