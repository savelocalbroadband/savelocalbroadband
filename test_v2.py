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

# ============================ v2.2 guards (audit release) ============================

# 9) LEDGER COHERENCE IS REAL, NOT CLAIMED: the county engine implements nci_year, carries
#    the macro factor + overbuild, and enforces the accounting identity in-source.
cvm = src[src.index("def county_value_mc"):src.index("def run_county")]
check("C implements nci_year", "nci_year" in cvm)
check("C carries macro factor Z", "0.0015 * Z" in cvm and "0.004 * Z" in cvm)
check("C carries the overbuild tail", "overbuild_yr" in cvm)
check("C enforces county = household + district", "np.allclose(cnty, hh + dist)" in cvm)
check("C dead `r` param removed", not re.search(r"def county_value_mc\([^)]*\br=", src))
bmc = src[src.index("def benefit_mc"):src.index("def run_benefit")]
check("B takes the $40 elasticity haircut", "ELAST_HAIRCUT" in bmc)
check("B carries macro factor Z + overbuild", "0.0015 * Z" in bmc and "overbuild_yr" in bmc)
check("E build path charges the bathtub", bool(re.search(r"opex_b\s*=\s*opex0 \* \(1\.0 \+ g_opex\) \*\* t \* \(1\.0 \+ BATHTUB_RATE", src)))
check("growth radios are taxed", "RADIO_DEFLATION) ** (t - 1) * (1.0 + SALES_TAX)" in src)

# 10) MONOTONICITY (behavioral, n=30k, shared seed): stress must hurt, upside must help.
N = 30_000
base30 = m.cost_recovery_mc(n=N, verbose=False, scn=dict(m.SCENARIOS['balanced']))['p_payback']
worse  = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'starlink': 0.02})['p_payback']
better = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'sticky': 0.008})['p_payback']
delayd = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'delay': 2.0})['p_payback']
bw0    = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'bw_mbps': 0.0})['p_payback']
bwfull = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'bw_mbps': 2.8})['p_payback']
check("more Starlink churn lowers payback odds", worse < base30, f"{worse} !< {base30}")
check("more retention raises payback odds", better > base30, f"{better} !> {base30}")
check("delay lowers payback odds", delayd < base30, f"{delayd} !< {base30}")
check("more bandwidth cannot hurt", bwfull > bw0, f"{bwfull} !> {bw0}")

# 11) THE LITERAL FREEZE IS HARSHER THAN THE RT=0 FLOOR (the v2.2 floor-language correction).
floor30  = m.cost_recovery_mc(n=N, verbose=False)['p_payback']
freeze30 = m.cost_recovery_mc(n=N, verbose=False, scn={'freeze_rate': 1})['p_payback']
check("true freeze scores below the RT=0 floor", freeze30 < floor30, f"{freeze30} !< {floor30}")

# 12) FIXED-SHARE BRACKET: runs clean, and at fixed_share=0 exactly reproduces the base.
fx0 = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'fixed_share': 0.0})['p_payback']
fx5 = m.cost_recovery_mc(n=N, verbose=False, scn={**m.SCENARIOS['balanced'], 'fixed_share': 0.5})['p_payback']
check("fixed_share=0 is a no-op", fx0 == base30, f"{fx0} vs {base30}")
check("fixed_share=0.5 returns a valid probability", 0.0 <= fx5 <= 100.0, f"{fx5}")

# 13) SEED STABILITY + CONVERGENCE: the headline is a property of the model, not the seed.
p_s = [m.cost_recovery_mc(n=N, seed=m.SEED + k, verbose=False, scn=dict(m.SCENARIOS['balanced']))['p_payback'] for k in (0, 1, 2)]
check("3-seed spread < 1.5 pts at n=30k", max(p_s) - min(p_s) < 1.5, f"seeds -> {p_s}")
p_small = m.cost_recovery_mc(n=10_000, verbose=False, scn=dict(m.SCENARIOS['balanced']))['p_payback']
p_big   = m.cost_recovery_mc(n=100_000, verbose=False, scn=dict(m.SCENARIOS['balanced']))['p_payback']
check("n=10k vs n=100k within 1.5 pts", abs(p_small - p_big) < 1.5, f"{p_small} vs {p_big}")

# 14) COUNTY IDENTITY EXERCISED AT RUNTIME (the in-source assert fires on every call).
cq = m.county_value_mc(10, n=N, scn=dict(m.SCENARIOS['balanced']))
check("county engine runs with the identity assert live", 0.0 <= cq['p_county_ahead'] <= 100.0)

# 15) THE ARCHIVED v1 CANNOT CLOBBER LIVE OUTPUTS ANYMORE.
rsrc = open("montecarlo_robust.py", encoding="utf-8").read()
check("archived model writes pre_v2.* filenames only",
      'open("scenarios_output.json"' not in rsrc and 'open("pre_v2.scenarios_output.json"' in rsrc)

# 16) THE LEVER-TABLE GENERATOR IMPORTS THE LIVE MODEL (root cause of the stale published levers).
lsrc = open("sensitivity_levers.py", encoding="utf-8").read()
check("sensitivity_levers imports montecarlo_v2", "from montecarlo_v2 import" in lsrc and "from montecarlo_robust import" not in lsrc)

print()
if fails:
    print(f"{len(fails)} FAILED: " + ", ".join(fails)); raise SystemExit(1)
print("all guards passed.")
