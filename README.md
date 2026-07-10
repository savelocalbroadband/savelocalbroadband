# The Save Local Broadband risk model

This repository contains the **Monte Carlo financial model** behind [savelocalbroadband.com](https://savelocalbroadband.com) — the Okanogan County, WA ratepayer campaign for public review of the PUD's pause on its rural wireless broadband network.

When the campaign says the ~$1.2M wireless upgrade is likely to pay for itself, that claim is the output of the code in this repository — published here in full so anyone can inspect it, challenge it, or re-run it.

## Reproduce every published figure

```bash
python montecarlo_v2.py
```

The only dependency is NumPy. The random seed is locked (`20260629`) and every configuration runs 200,000 iterations, so a re-run reproduces the published numbers **exactly** — there is no lucky run to fish for. The script prints each ledger's summary and rewrites the five output JSON files, which should come back byte-identical to the committed copies.

`test_v2.py` runs the model's invariance checks (including the rate-independence of the county total).

## What the model answers — five ledgers

| Ledger | Question |
|---|---|
| **A · Cost recovery** | Does the wireless line's *own* discounted cash earn the ~$1.2M back within the equipment's life? |
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
| `montecarlo_v2.py` | **The model** (v2.1). Ledgers A–E; writes the five output JSONs. |
| `*_output.json`, `scenarios_output*.json` | The published results this code produces (version + seed embedded). |
| `test_v2.py` | Invariance checks. |
| `FINDINGS.md`, `REVIEW_v2.md`, `PROMOTION_BUNDLE.md` | The adversarial review records — the audit trail of corrections. |
| `montecarlo_robust.py`, `recovery_model.py` | Superseded earlier versions, kept public so the improvement is auditable. |
| `financial_appendix.py` | The deterministic DCF companion analysis. |
| `sensitivity_levers.py` | The one-lever-at-a-time sensitivity table. |
| `sources_and_uses.py` / `.json` | The funding-plan arithmetic. |
| `parse_all.py`, `*.csv` | Parsing of the District's billing/budget records (obtained by public-records request) into the datasets the model's inputs are anchored to. |

## Is it rigged? Check the direction of the corrections.

A tuned model's headline only ever improves. This one's history runs the other way: adding the labor and contingency a board member asked about dropped the headline from the 90s into the 70s; two adversarial audit passes flattened the growth assumption, discounted the recovery stream, and moved the largest reseller's exit to a timing that *strands* capital instead of saving it. Every markdown was kept and every markup is documented with its reason — the review records are in this repository, and the full correction log is [§3.15 of the documentation](https://savelocalbroadband.com/model-docs.php#s3-15).

Every input is tagged **DOCUMENTED** (from the District's own workbook, the Washington State Auditor's 2024 audit, or billing records) or **INFERRED** (a labeled modeling judgment, bounded wide, leaning against the campaign's conclusion). The two numbers only the District can publish — a firm tower-labor figure and the wireless-only cost split — are modeled as wide ranges and are the subject of an open records request.

## Corrections

If you find an error — in the code, the inputs, or the documentation — [tell us](https://savelocalbroadband.com/action.php). Corrections get made and logged, whichever direction they move the number.
