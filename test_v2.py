#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_v2.py -- regression guards for montecarlo_v2.py
Run:  python test_v2.py    (exits non-zero on failure)

These are behavioral guards for the v2 corrections, not a full test suite. They
pin the two things most likely to silently regress: the one-time overbuild step
and the NCI-timing default (which must leave the headline untouched).
"""
import re, numpy as np, montecarlo_v2 as m

fails = []
def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + (("  -- " + detail) if detail and not ok else ""))
    if not ok: fails.append(name)

# 1) OVERBUILD IS ONE-TIME. Replicate the model's subs-step semantics over 15 yr with a
#    15% loss at year 5, zero growth/churn. Correct (==): a single 15% step that persists
#    as a level shift -> final = 0.85. Buggy (>=): re-applied every year -> 0.85**11.
def evolve(op, loss=0.15, hit_yr=5, H=15):
    subs = 1.0
    for t in range(1, H + 1):
        if (t == hit_yr) if op == "==" else (t >= hit_yr):
            subs *= (1.0 - loss)
    return subs
step, compound = evolve("=="), evolve(">=")
check("overbuild one-time step == 0.85", abs(step - 0.85) < 1e-9, f"got {step:.4f}")
check("buggy >= would compound to 0.85**11", abs(compound - 0.85 ** 11) < 1e-9, f"got {compound:.4f}")
check("the fix materially differs from the bug", abs(step - compound) > 0.6)

# 2) THE SOURCE USES THE FIXED FORM (guards against a copy/paste reverting it).
src = open("montecarlo_v2.py", encoding="utf-8").read()
ob = re.search(r"overbuild & \(t (==|>=) overbuild_yr\)", src)
check("model source uses `t == overbuild_yr`", bool(ob) and ob.group(1) == "==",
      f"found `{ob.group(1) if ob else '???'}`")

# 3) NCI-TIMING DEFAULT IS A NO-OP. cost_recovery_mc with nci_year=0 (default) must equal
#    the same run with the key absent -> the headline is unchanged by the new option.
a = m.cost_recovery_mc(n=40_000, verbose=False, scn={'rate_track': 0.6})
b = m.cost_recovery_mc(n=40_000, verbose=False, scn={'rate_track': 0.6, 'nci_year': 0})
check("nci_year=0 default is a no-op", a['p_payback'] == b['p_payback'],
      f"{a['p_payback']} vs {b['p_payback']}")

# 4) UNCONDITIONAL PERCENTILE HONESTY: when the success rate is below a percentile, that
#    unconditional percentile must report 'not reached', never a finite year.
lowp = m.cost_recovery_mc(n=40_000, verbose=False, scn={'rate_track': 0.0, 'starlink': 0.02, 'shock': 0.20, 'cliff': True})
check("test-4 precondition: this scenario pays back <90%", lowp['p_payback'] < 90, f"p={lowp['p_payback']}%")
check("uncond P90 = 'not reached' when <90% pay back", lowp['payback_P90_uncond'] == "not reached",
      f"p={lowp['p_payback']}%, uncondP90={lowp['payback_P90_uncond']}")

# 5) RUN-TO-FAILURE: the status quo is guaranteed to die; protected-cash PV is large.
r = m.build_vs_rtf_mc("central", n=40_000)
check("RTF shuts down by yr15 in ~all futures", r['p_rtf_shutdown_by_yr15'] >= 99.0,
      f"{r['p_rtf_shutdown_by_yr15']}%")
check("protected-cash PV is large & positive", r['protected_cash_PV_P50'] > 500_000,
      f"${r['protected_cash_PV_P50']:,}")

# 6) BLOCKER 1 — Ledger E charges a pro-rated G2 refresh (source guard + effect).
check("E source charges `g2_cost * frac_used`", bool(re.search(r"g2_cost \* frac_used", src)))
check("E central incremental NPV P50 < 50k (refresh + NCI common-mode active)",
      r['incremental_NPV_P50'] < 50_000, f"${r['incremental_NPV_P50']:,}")

# 7) BLOCKER 2 — NCI is common-mode in Ledger E (same start applied to both paths).
check("E source starts both paths from NCI-adjusted `start`",
      bool(re.search(r"subs_b = start\.copy\(\); subs_r = start\.copy\(\)", src)))

# 8) BLOCKER 4 — Ledger B headline (NCI applied) sits below the no-exit bracket end.
bh = m.run_benefit()
h15 = bh['horizons']['15']
check("B 15-yr headline (NCI) < no-exit bracket", h15['P50'] < h15['P50_no_exit'],
      f"P50={h15['P50']:,} vs no_exit={h15['P50_no_exit']:,}")
check("B dead `r` param removed", not re.search(r"def benefit_mc\([^)]*\br\b", src))

print()
if fails:
    print(f"{len(fails)} FAILED: " + ", ".join(fails)); raise SystemExit(1)
print("all guards passed.")
