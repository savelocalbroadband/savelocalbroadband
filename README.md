# The Save Local Broadband risk model

This repository contains the **Monte Carlo financial model** behind [savelocalbroadband.com](https://savelocalbroadband.com) — the Okanogan County, WA ratepayer campaign for public review of the PUD's pause on its rural wireless broadband network.

When the campaign says the ~$1.2M wireless upgrade is likely to pay for itself, that claim is the output of the code in this repository — published here in full so anyone can inspect it, challenge it, or re-run it.

## Reproduce every published figure

```bash
python montecarlo_v2.py
```

The only dependency is NumPy. The random seed is locked (`20260629`) and every configuration runs 200,000 iterations, so a re-run reproduces the published numbers **exactly** — there is no lucky run to fish for. The script prints each ledger's summary and rewrites the six output JSON files, which should come back byte-identical to the committed copies. Since v2.2 every output embeds the model version, seed, NumPy/Python versions, and the model file's SHA-256.

`test_v2.py` runs the guard suite: source-level guards on every audit correction, the runtime `county = household + district` identity, monotonicity checks (stress must hurt, upside must help), a 3-seed stability sweep, and an n-ladder convergence check. `sensitivity_levers.py` regenerates the published lever table (`sensitivity_levers_output.json`) from the live model.

## What the model answers — five ledgers

| Ledger | Question |
|---|---|
| **A · Cost recovery** | Does the wireless line's *own* discounted cash earn the ~$1.2M back within the 15-year asset life (one wear-out refresh charged; the stricter before-wear-out test is published alongside)? |
| **B · Ratepayer benefit** | How much do households avoid overpaying because the cost-based public rate disciplines the market? |
| **C · County value** | Counting A and B honestly (the public rate cancels out): does the county come out ahead? |
| **D · Scenarios** | How do A and C look under three coherent worldviews — pessimistic, balanced, optimistic? |
| **E · Build vs run-to-failure** | How does building now compare against spending nothing and letting the end-of-life network decline? |

Results from different ledgers are never summed — they answer different payees' questions.

## Documentation

The model is documented at three depths — plain English, a decision-maker's briefing, and a full technical reference covering every distribution, formula, and audit correction:

- **Live:** [savelocalbroadband.com/model-docs.php](https://savelocalbroadband.com/model-docs.php)
- **In this repo:** [`docs/model-documentation.html`](docs/model-documentation.html) (a self-contained snapshot — download and open in any browser)

There is also a [live calculator](https://savelocalbroadband.com/how-we-modeled-risk.php#calc) that runs a lightweight version of the model in your browser, with a slider for every major assumption.

## Repository layout

| File(s) | Role |
|---|---|
| `montecarlo_v2.py` | **The model** (v2.2). Ledgers A–E plus the cost-of-waiting delay sweep; writes the six output JSONs. |
| `*_output.json`, `scenarios_output*.json` | The published results this code produces (version + seed + environment + SHA-256 embedded). |
| `test_v2.py` | The guard suite: audit-correction guards, ledger identity, monotonicity, seed stability, convergence. |
| `FINDINGS.md`, `REVIEW_v2.md`, `PROMOTION_BUNDLE.md` | The adversarial review records — the audit trail of corrections. |
| `montecarlo_robust.py`, `recovery_model.py` | Superseded earlier versions, kept public so the improvement is auditable. |
| `financial_appendix.py` | The deterministic DCF companion analysis. |
| `sensitivity_levers.py` | The one-lever-at-a-time sensitivity table. |
| `sources_and_uses.py` / `.json` | The funding-plan arithmetic. |
| `parse_all.py`, `*.csv` | Parsing of the District's billing/budget records (obtained by public-records request) into the datasets the model's inputs are anchored to. |

## Is it rigged? Check the direction of the corrections.

A tuned model's headline only ever improves. This one's history runs the other way: adding the labor and contingency a board member asked about dropped the headline from the 90s into the 70s; two adversarial audit passes flattened the growth assumption, discounted the recovery stream, and moved the second-largest reseller's exit to a timing that *strands* capital instead of saving it. The v2.2 release (2026-07-10) continued the pattern after a third-party review and an internal consistency audit: the sensitivity-table generator was found still pointed at the superseded model (every stale lever number had drifted in the *favorable* direction — all corrected downward), the year-2 exit stranding was extended to the county ledger, the macro-stress factor and overbuild tail were carried into every ledger, sales tax was extended to growth radios and the refresh, a fixed-vs-variable operating-cost bracket was published (−9 to −15 points at its ends), and the literal 15-year rate freeze — harsher than the model's own floor scenario — was published as its own sensitivity (~25%). Every markdown was kept and every markup is documented with its reason — the review records are in this repository, and the full correction log is [§3.15 of the documentation](https://savelocalbroadband.com/model-docs.php#s3-15).

Every input is tagged **DOCUMENTED** (from the District's own workbook, the Washington State Auditor's 2024 audit, or billing records) or **INFERRED** (a labeled modeling judgment, bounded wide, leaning against the campaign's conclusion). The two numbers only the District can publish — a firm tower-labor figure and the wireless-only cost split — are modeled as wide ranges and are the subject of an open records request.

## Corrections

If you find an error — in the code, the inputs, or the documentation — [tell us](https://savelocalbroadband.com/action.php). Corrections get made and logged, whichever direction they move the number.
