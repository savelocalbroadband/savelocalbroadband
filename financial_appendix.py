#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
financial_appendix.py  --  Board-grade DCF for the Okanogan PUD Tarana upgrade
================================================================================
Sits ON TOP of recovery_model.py and uses the SAME verified inputs (the District's
Tarana workbook + the WA SAO 2024 audit). Adds the analysis a CFO / commissioner
expects and the cost-recovery model did not state explicitly:

   * Discounted cash flow: NPV, IRR, discounted payback (vs. the District's own
     ~3% cost of capital, from its 2020 revenue-bond true-interest-cost).
   * A 10-year incremental pro-forma (Invest vs. Let-Decline).
   * Break-even: the margin / ARPU / customer count at which NPV hits zero.
   * One-at-a-time sensitivity (a tornado, in numbers).

Every input is sourced; nothing is invented. Conservative choices are flagged.
Run:  python financial_appendix.py   (writes financial_appendix_output.json)
"""
import json

# ---- VERIFIED INPUTS (identical to recovery_model.py) -----------------------
CUST        = 878          # customers the 7 upgraded sites serve today (workbook)
RADIOS_PLAN = 1035         # radios the $1.2M already funds (headroom)
TOWER_FIXED = 370_783      # 7-site fixed tower hardware (customer-independent; workbook-footed, synced to montecarlo_v2)
RADIO_COST  = 787          # per served customer (RN $640 + unlock $100 + 1yr mgmt $47)
CAPEX       = 1_178_368    # workbook grand total ("~$1.2M"); ~= TOWER_FIXED + 1035*787
ARPU_YR     = 480.0        # $40/mo, the District's PROPOSED single-tier wholesale rate
ARPU_INFL   = 0.015        # cost-based drift (matches recovery_model)
MARGIN      = 0.45         # wireless CASH margin, audit-anchored (SAO 2024; range .28-.58)
LIFE        = 10           # gear life, yr (Tarana G1; recovery_model uses 8/10/12)
WACC        = 0.04         # discount rate. District 2020 bond TIC ~2.9%; 4% = conservative.

def cashflows(n_cust=CUST, arpu=ARPU_YR, margin=MARGIN, life=LIFE,
              arpu_infl=ARPU_INFL, growth=0.0):
    """Annual incremental wireless cash contribution the upgrade preserves/creates.
    Counterfactual: the District's own memo calls the network 'severely congested
    with no possibility for expansion' and declining, so this served-customer cash
    stream is the at-risk stream the $1.2M protects. (A partial-survival haircut is
    run in sensitivity.)"""
    cfs = []
    s = float(n_cust)
    for t in range(1, life + 1):
        s *= (1.0 + growth)
        rev = s * arpu * (1.0 + arpu_infl) ** (t - 1)
        cfs.append(rev * margin)
    return cfs

def npv(rate, capex, cfs):
    return -capex + sum(cf / (1.0 + rate) ** (t + 1) for t, cf in enumerate(cfs))

def irr(capex, cfs):
    lo, hi = -0.9, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        v = npv(mid, capex, cfs)
        if abs(v) < 1.0:
            return mid
        if v > 0:
            lo = mid
        else:
            hi = mid
    return mid

def discounted_payback(rate, capex, cfs):
    bal = capex
    for t, cf in enumerate(cfs, 1):
        bal -= cf / (1.0 + rate) ** t
        if bal <= 0:
            return t - 1 + (bal + cf / (1.0 + rate) ** t) / (cf / (1.0 + rate) ** t)
    return None

def simple_payback(capex, cfs):
    bal = capex
    for t, cf in enumerate(cfs, 1):
        bal -= cf
        if bal <= 0:
            return t - 1 + (bal + cf) / cf
    return None

# ---- BASE CASE --------------------------------------------------------------
base = cashflows()
base_npv  = npv(WACC, CAPEX, base)
base_irr  = irr(CAPEX, base)
base_dpb  = discounted_payback(WACC, CAPEX, base)
base_spb  = simple_payback(CAPEX, base)

print("=" * 70)
print("BASE CASE  (878 cust, $40/mo, 45%% cash margin, 10-yr life, %.0f%% discount)" % (WACC*100))
print("=" * 70)
print(f"  Capex (t0) ................. ${CAPEX:,.0f}")
print(f"  Yr-1 cash contribution ..... ${base[0]:,.0f}")
print(f"  10-yr undiscounted cash .... ${sum(base):,.0f}")
print(f"  NPV @ {WACC*100:.0f}% ................. ${base_npv:,.0f}")
print(f"  IRR ........................ {base_irr*100:.1f}%")
print(f"  Simple payback ............. {base_spb:.1f} yr")
print(f"  Discounted payback ......... {base_dpb:.1f} yr")
print(f"  Profitability index (PV/Capex) {(base_npv + CAPEX) / CAPEX:.2f}")

# ---- NPV vs DISCOUNT RATE ----------------------------------------------------
print("\nNPV vs discount rate:")
npv_by_rate = {}
for r in (0.03, 0.04, 0.05, 0.06, base_irr):
    npv_by_rate[round(r, 4)] = npv(r, CAPEX, base)
    print(f"   {r*100:.1f}% -> ${npv(r, CAPEX, base):,.0f}")

# ---- 10-YEAR PRO-FORMA (illustration) + COUNTERFACTUAL BREAK-EVEN ------------
# The base case treats the served-customer cash stream as AT RISK without the
# upgrade (the District's memo: 'severely congested, no possibility for
# expansion'). The honest question a skeptic asks: how fast must the no-upgrade
# path erode for the spend to clear its cost of capital? We solve for that decline
# rate rather than assert one. The pro-forma table shows an illustrative -10%/yr
# decline purely for the visual.
DECLINE_ILLUS = -0.10
invest  = cashflows()
decline = cashflows(growth=DECLINE_ILLUS)
proforma = []
for t in range(LIFE):
    proforma.append({"yr": t+1, "invest": round(invest[t]),
                     "decline": round(decline[t]),
                     "incremental": round(invest[t] - decline[t])})

def project_npv_given_decline(d):
    """NPV of the DECISION: -capex + PV(invest stream) - PV(stream you'd keep
    for free if the line survived, eroding at rate d without the upgrade)."""
    dec = cashflows(growth=d)
    inc = [invest[t] - dec[t] for t in range(LIFE)]
    return npv(WACC, CAPEX, inc)

# break-even decline: the d (<0) at which the decision NPV = 0
d_lo, d_hi = -0.60, 0.0
for _ in range(200):
    dm = (d_lo + d_hi) / 2
    v = project_npv_given_decline(dm)
    if abs(v) < 200: break
    # NPV increases as decline gets steeper (more negative d)
    if v < 0: d_hi = dm
    else:     d_lo = dm
be_decline = dm
print(f"\nCounterfactual break-even decline (project NPV @ {WACC*100:.0f}% = 0):")
print(f"   the upgrade clears its cost of capital as long as the no-upgrade path")
print(f"   would lose MORE than ~{abs(be_decline)*100:.0f}%/yr of wireless cash flow.")
print(f"   (illustrative -10%/yr -> decision NPV ${project_npv_given_decline(-0.10):,.0f})")

# ---- BREAK-EVEN --------------------------------------------------------------
# margin at which NPV @ WACC = 0
def npv_at_margin(m): return npv(WACC, CAPEX, cashflows(margin=m))
def npv_at_arpu(a):   return npv(WACC, CAPEX, cashflows(arpu=a))
def npv_at_cust(n):   return npv(WACC, CAPEX, cashflows(n_cust=n))
def bisect(f, lo, hi):
    for _ in range(200):
        mid = (lo+hi)/2
        if abs(f(mid)) < 50: return mid
        if (f(lo) < 0) == (f(mid) < 0): lo = mid
        else: hi = mid
    return mid
be_margin = bisect(npv_at_margin, 0.05, 0.60)
be_arpu   = bisect(npv_at_arpu, 100, 480)
be_cust   = bisect(npv_at_cust, 100, 878)
print(f"\nBreak-even (NPV @ {WACC*100:.0f}% = 0):")
print(f"   cash margin .... {be_margin*100:.1f}%  (base 45%)")
print(f"   ARPU ........... ${be_arpu:.0f}/yr = ${be_arpu/12:.2f}/mo  (base $40)")
print(f"   customers ...... {be_cust:.0f}  (base 878)")

# ---- ONE-AT-A-TIME SENSITIVITY (tornado) ------------------------------------
print(f"\nSensitivity of NPV @ {WACC*100:.0f}% (base ${base_npv:,.0f}):")
sens = []
def add(label, lo_npv, hi_npv):
    sens.append({"label": label, "low": round(lo_npv), "high": round(hi_npv)})
    print(f"   {label:<26}  low ${lo_npv:,.0f}   high ${hi_npv:,.0f}")
add("Cash margin 28%-58%",      npv(WACC,CAPEX,cashflows(margin=0.28)), npv(WACC,CAPEX,cashflows(margin=0.58)))
add("ARPU $31-$45 /mo",         npv(WACC,CAPEX,cashflows(arpu=31*12)),  npv(WACC,CAPEX,cashflows(arpu=45*12)))
add("Customers 685-1035",       npv(WACC,CAPEX,cashflows(n_cust=685)),  npv(WACC,CAPEX,cashflows(n_cust=RADIOS_PLAN)))
add("Gear life 8-12 yr",        npv(WACC,CAPEX,cashflows(life=8)),      npv(WACC,CAPEX,cashflows(life=12)))
add("Discount 6%-3%",           npv(0.06,CAPEX,base),                   npv(0.03,CAPEX,base))
add("Capex +15% / -5%",         npv(WACC,CAPEX*1.15,base),              npv(WACC,CAPEX*0.95,base))

# worst-case stack (all bad at once): 685 cust, 28% margin, $31, 8yr, 6% disc, +15% capex
worst = npv(0.06, CAPEX*1.15, cashflows(n_cust=685, margin=0.28, arpu=31*12, life=8))
worst_irr = irr(CAPEX*1.15, cashflows(n_cust=685, margin=0.28, arpu=31*12, life=8))
print(f"\n  ALL-BAD-AT-ONCE NPV ......... ${worst:,.0f}  (IRR {worst_irr*100:.1f}%)")

# ---- CURRENT-RATE BASE: same case but at the ~$31.2/mo ACTUALLY collected today ----
# (the $40 base is the PROPOSED single-tier rate; show the result at today's rate so the
#  dependency is explicit, not buried.)
CUR_ARPU = 374.4            # ~$31.2/mo blended wholesale, per recovery_model.py
cur = cashflows(arpu=CUR_ARPU)
cur_npv = npv(WACC, CAPEX, cur); cur_irr = irr(CAPEX, cur); cur_spb = simple_payback(CAPEX, cur)
print(f"\nAt the CURRENT realized rate (${CUR_ARPU/12:.2f}/mo, not the proposed $40):")
print(f"   NPV @ {WACC*100:.0f}% ${cur_npv:,.0f} | IRR {cur_irr*100:.1f}% | simple payback {cur_spb:.1f} yr")

# decision-NPV vs the no-upgrade decline rate (the M1 counterfactual, made explicit)
dec_curve = {f"{int(d*100)}": round(project_npv_given_decline(d)) for d in (-0.05, -0.10, -0.20)}
print("Decision NPV by no-upgrade decline:", dec_curve, "| break-even", round(be_decline,3))

# ---- DEBT SERVICE + COVERAGE (DSCR) — the board/bond vocabulary --------------
# The District would bond this the way it bonded its 2010 build (2020 revenue bonds,
# ~2.9% true-interest-cost). Show the annual debt service and how many times the cash
# covers it — the metric a utility board and a bond analyst read FIRST. Two bases:
#   segment  = the whole self-supporting telecom segment's audited surplus (the basis
#              peers report: Mason PUD 3 6.71x, Pend Oreille ~5.5x).
#   upgrade  = ONLY the 878 served customers' own cash contribution (a conservative
#              floor: does the upgrade cover its own debt with nothing else?).
BOND_RATE   = 0.04         # conservative; the District's 2020 revenue-bond TIC was ~2.9%
BOND_TERM   = 15           # revenue-bond term, yr
SEG_SURPLUS = 808_166      # audited SAO 2024 telecom-segment net surplus (self-supporting line)
_af = BOND_RATE / (1.0 - (1.0 + BOND_RATE) ** (-BOND_TERM))     # level-payment annuity factor
debt_service = CAPEX * _af
dscr_segment = SEG_SURPLUS / debt_service
dscr_upgrade = base[0] / debt_service
print(f"\nDebt service on ${CAPEX:,.0f} @ {BOND_RATE*100:.0f}% / {BOND_TERM}yr .. ${debt_service:,.0f}/yr")
print(f"   DSCR, segment ($808K surplus) .. {dscr_segment:.1f}x   |   DSCR, upgrade's own cash .. {dscr_upgrade:.1f}x")

# ---- GRANT OFFSET (BEAD/ReConnect precedent; NONE committed to this refresh) --
grant_offset = {}
for g in (0, 25, 50):
    cx = CAPEX * (1 - g/100.0)
    grant_offset[str(g)] = {"capex": round(cx), "npv": round(npv(WACC, cx, base)),
                            "simple_payback": round(simple_payback(cx, base), 1),
                            "debt_service": round(cx * _af)}
print("\nGrant offset (uncommitted; disclosed upside):",
      {k: f"${v['capex']:,} -> {v['simple_payback']}yr" for k, v in grant_offset.items()})

out = {
  "inputs": {"capex": CAPEX, "cust": CUST, "radios_plan": RADIOS_PLAN,
             "arpu_mo": 40, "margin": MARGIN, "life": LIFE, "wacc": WACC,
             "arpu_infl": ARPU_INFL},
  "base": {"npv": round(base_npv), "irr": round(base_irr,4),
           "simple_payback": round(base_spb,1), "disc_payback": round(base_dpb,1),
           "yr1_cash": round(base[0]), "tot_cash": round(sum(base)),
           "pi": round((base_npv+CAPEX)/CAPEX,2)},
  "npv_by_rate": {str(k): round(v) for k,v in npv_by_rate.items()},
  "proforma": proforma,
  "current_rate": {"arpu_mo": round(CUR_ARPU/12,2), "npv": round(cur_npv),
                   "irr": round(cur_irr,4), "simple_payback": round(cur_spb,1)},
  "counterfactual": {"breakeven_decline": round(be_decline,3),
                     "decision_npv": dec_curve,
                     "illus_decline": DECLINE_ILLUS,
                     "illus_npv": round(project_npv_given_decline(-0.10))},
  "breakeven": {"margin": round(be_margin,3), "arpu_mo": round(be_arpu/12,2), "cust": round(be_cust)},
  "financing": {"bond_rate": BOND_RATE, "bond_term": BOND_TERM, "tic_2020": 0.029,
                "debt_service": round(debt_service), "seg_surplus": SEG_SURPLUS,
                "dscr_segment": round(dscr_segment,1), "dscr_upgrade": round(dscr_upgrade,1)},
  "grant_offset": grant_offset,
  "sensitivity": sens,
  "worst_all_bad": round(worst),
}
with open("financial_appendix_output.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\n[wrote financial_appendix_output.json]")
