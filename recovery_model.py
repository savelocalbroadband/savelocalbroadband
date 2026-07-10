#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery_model.py  —  Cost-recovery model for the Okanogan PUD Tarana upgrade
================================================================================
v2 (2026-06-18): RESCOPED after verifying the District's Tarana workbooks.

WHAT CHANGED AND WHY
--------------------
An earlier version of this model recovered the ~$1.2M upgrade cost out of the
ENTIRE wireless line's revenue (~2,726 subscribers). Reading the District's own
Tarana cost workbooks line by line shows that is wrong: the ~$1.2M covers SEVEN
specific tower sites that today serve 878 customers --- NOT the whole network.
The remaining ~1,848 wireless customers sit on dozens of small "valley-floor"
Cambium access points that are not in this budget. So the cost must be recovered
from the customers the upgrade actually serves. This version does that. It is
LESS rosy than the prior one, on purpose --- it is the defensible number.

VERIFIED INPUTS (District's "Tarana Upgrade costs" workbook, per-site sheets)
-----------------------------------------------------------------------------
  7 sites: Jackass Butte, Coleman, Nortons, Pickens, Number, Eder, Shellrock.
  Per-site cost = FIXED tower hardware + a per-customer RADIO.
    * Fixed tower hardware, 7 sites total ............ $371,323
    * Per-customer radio (RN $640 + BW unlock $100 + 1yr mgmt $47) .. ~$787
    * Current customers on these 7 sites ............. 878
    * Radios planned (headroom for growth) ........... 1,035
    * Workbook grand total ........................... $1,178,368  (~= PUD's stated $1.2M)
  Wholesale revenue per customer ~ $31.2/mo = ~$375/yr (cost-based, stable).
    (= $1.139M 2025 wireless revenue / ~3,040 avg subs / 12; and $85,191 May-2026 / 2,726.)

THE CENTRAL UNCERTAINTY (unchanged, stated honestly)
----------------------------------------------------
The District has never published a WIRELESS-SPECIFIC operating margin --- only the
whole telecom segment's (24.9% NET, after depreciation, including fiber). Wireless
runs on largely-depreciated 2010 plant, so its CASH margin is plausibly higher,
but we don't know it. So margin is the model's central uncertain input: drawn from
a range, not asserted.

THE QUESTION THIS VERSION IS BUILT TO ANSWER
--------------------------------------------
NCI (the 2nd-largest reseller; Highland is larger) may migrate its customers onto its own gear and leave
the PUD wholesale program. Does the upgrade still pay back without NCI? KEY FACT:
the upgrade is fundamentally PER-CUSTOMER --- the District buys a ~$787 radio only
for customers it actually serves. If NCI's customers leave BEFORE the radios are
bought, those radios are never purchased. So NCI's exit removes its REVENUE and its
COST together. The only cost that does NOT scale away is the fixed tower hardware
(~1/3 of the total), which then spreads over fewer customers. We quantify exactly
that effect below.

Run:  python recovery_model.py
"""

import numpy as np
RNG = np.random.default_rng(20260618)

# ---- verified constants ----
CUST          = 878
RADIOS_PLAN   = 1035
TOWER_FIXED   = 371_323          # 7-site tower hardware (customer-independent)
RADIO_COST    = 787              # per customer served
ARPU_YR       = 480.0            # $40/mo wholesale = the District's PROPOSED single-tier rate
                                #   for the upgraded network (legacy blend was ~$31/mo)
ARPU_INFL     = 0.015
NCI_SHARE     = 0.22             # NCI's est. share of these 7 sites (network-wide 20%)

def capex_for(n_customers, headroom=1.0):
    """Cost to upgrade the 7 towers + buy a radio for each served customer.
    Tower hardware is fixed; radios scale with customers actually served."""
    radios = round(n_customers * headroom)
    return TOWER_FIXED + radios * RADIO_COST

def payback_years(n_customers, margin, ann_growth=0.0, headroom=1.0,
                  horizon_mo=240, fin_rate=0.0):
    """Months until cumulative wireless cash contribution repays the capex."""
    capex = capex_for(n_customers, headroom)
    g_m = (1.0 + ann_growth) ** (1/12) - 1.0
    fin_m = fin_rate / 12.0
    s = float(n_customers); bal = float(capex)
    for t in range(horizon_mo):
        s *= (1.0 + g_m)
        arpu = ARPU_YR / 12.0 * (1.0 + ARPU_INFL) ** (t/12.0)
        bal = bal * (1.0 + fin_m) - s * arpu * margin
        if bal <= 0:
            return (t + 1) / 12.0
    return None

# --------------------------------------------------------------------------
# (A) PER-CUSTOMER UNIT ECONOMICS  --  the scope-independent core
# --------------------------------------------------------------------------
def unit_economics():
    print("=" * 78)
    print("(A) UNIT ECONOMICS  --  what one upgraded customer costs and returns")
    print("=" * 78)
    allin_1to1 = capex_for(CUST, headroom=1.0) / CUST
    allin_plan = capex_for(CUST, headroom=RADIOS_PLAN / CUST) / CUST
    print("  Fixed tower cost / customer (878) ...... $%.0f" % (TOWER_FIXED / CUST))
    print("  Radio / customer ....................... $%.0f" % RADIO_COST)
    print("  All-in / customer (1 radio each) ....... $%.0f" % allin_1to1)
    print("  All-in / customer (w/ planned headroom)  $%.0f" % allin_plan)
    print("  Revenue / customer / yr ................ $%.0f" % ARPU_YR)
    print("  --- payback (all-in 1:1) by wireless CASH margin ---")
    print("      (segment cash/EBITDA margin from SAO audit ~ 46-50%)")
    for m in (0.30, 0.40, 0.45, 0.50, 0.58):
        yrs = allin_1to1 / (ARPU_YR * m)
        print("     margin %2.0f%% -> %.1f yr" % (m*100, yrs))

# --------------------------------------------------------------------------
# (B) WITH NCI vs WITHOUT NCI  --  the question the user asked
# --------------------------------------------------------------------------
def nci_comparison():
    print("\n" + "=" * 78)
    print("(B) DOES IT STILL PAY BACK IF NCI LEAVES THE PROGRAM?")
    print("=" * 78)
    n_with = CUST
    n_without = round(CUST * (1 - NCI_SHARE))
    print("  With NCI:    %d customers, capex $%s" % (n_with, f"{capex_for(n_with):,.0f}"))
    print("  Without NCI: %d customers, capex $%s  (NCI's radios never bought)"
          % (n_without, f"{capex_for(n_without):,.0f}"))
    print("  --- payback (years), no growth ---")
    print("   margin |  with NCI | without NCI |  slower by")
    for m in (0.25, 0.30, 0.40, 0.50):
        a = payback_years(n_with, m)
        b = payback_years(n_without, m)
        if a and b:
            print("    %2.0f%%   |   %4.1f    |    %4.1f     |   +%.0f%%"
                  % (m*100, a, b, (b/a - 1) * 100))
        else:
            print("    %2.0f%%   |   %s | %s" % (m*100, a, b))
    print("\n  Why so close: the District only buys radios for customers it serves,")
    print("  so NCI's exit removes its revenue AND its ~$787/radio cost together.")
    print("  Only the fixed tower hardware (~1/3 of cost) re-spreads over fewer")
    print("  customers -- which is the entire size of the penalty.")

# --------------------------------------------------------------------------
# (B2) GROWTH -> RECOVERY  --  hypothetical ADDED sign-ups on the same towers
# --------------------------------------------------------------------------
def growth_projection():
    """What do additional sign-ups do to recovery? The upgrade is next-gen fixed
    wireless (Tarana): it reaches NLOS homes the old line-of-sight gear couldn't,
    and the District's own Jackass Butte test measured ~160 deg of usable coverage
    from a 90-deg-designed sector. Crucially, the $1.2M ALREADY funds radios for
    RADIOS_PLAN (1,035) customers -- 157 (+18%) more than the 878 served today.
    So customers 879..1,035 add ~$0 capex (radios bought, towers fixed) = pure
    acceleration; beyond 1,035 each adds one RADIO_COST radio. Reported at the
    conservative plan values: $40/mo ($480/yr) wholesale, 45% cash margin.

    Expected output (matches the website data + case + flyer):
        today (878) .................... ~6.2 yr   (baseline)
        +100 would-return (978) ........ ~5.6 yr   +$216,000 / 10 yr
        fill budgeted radios (1,035) ... ~5.3 yr   +$339,120 / 10 yr   (~$0 added cost)
        +25% NLOS reach (1,098) ........ ~5.2 yr   +$475,200 / 10 yr
    """
    print("\n" + "=" * 78)
    print("(B2) GROWTH -> RECOVERY  --  hypothetical added sign-ups, $40 / 45% margin")
    print("=" * 78)
    m = 0.45
    per_yr = ARPU_YR * m                       # $216 cash per customer per year
    budget = capex_for(CUST, RADIOS_PLAN / CUST)   # the $1.2M as scoped (1,035 radios)
    def capex_n(n):
        return budget if n <= RADIOS_PLAN else budget + (n - RADIOS_PLAN) * RADIO_COST
    print("  budgeted capex (1,035 radios): $%s | cash/customer/yr: $%.0f" % (f"{budget:,.0f}", per_yr))
    print("  scenario                          subs   payback    +$/yr      +$/10yr")
    for label, n in [("today", CUST), ("+100 would-return", 978),
                     ("fill budgeted radios (1,035)", RADIOS_PLAN), ("+25% NLOS reach", 1098)]:
        pb = capex_n(n) / (n * per_yr)
        add_yr = (n - CUST) * per_yr
        print("   %-32s %5d   %4.1f yr   +$%-8s +$%s"
              % (label, n, pb, f"{add_yr:,.0f}", f"{add_yr * 10:,.0f}"))
    print("  Why it accelerates: the towers are fixed cost and the radios for 1,035")
    print("  customers are already in the budget -- so added sign-ups are nearly")
    print("  pure margin against an already-committed capex.")

# --------------------------------------------------------------------------
# (C) MONTE CARLO  --  probability of payback within the gear's life
# --------------------------------------------------------------------------
def montecarlo(n=200_000, with_nci=True, life_yr=10):
    n_cust = CUST if with_nci else round(CUST * (1 - NCI_SHARE))
    # margin: the CASH (EBITDA-like) margin -- the right concept for repaying
    # capital, since depreciation is non-cash. Anchored on the District's OWN
    # audited 2024 telecom segment (WA SAO): operating income $647,484 + telecom
    # depreciation ~$0.85-1.0M on $16.9M plant => operating cash flow ~$1.5M on
    # $3.249M revenue = ~46-50% cash margin. (The widely-quoted 24.9% is the NET
    # margin, AFTER depreciation -- too conservative for a payback question.)
    # Centered 0.45, wide, since the wireless-vs-fiber split of opex is unknown.
    margin = RNG.normal(0.45, 0.08, n).clip(0.28, 0.58)
    # growth of the served base post-upgrade: centered ~flat, modest spread.
    growth = RNG.normal(0.00, 0.04, n).clip(-0.12, 0.10)
    # NCI share uncertainty only matters in the without-NCI run
    pays = np.zeros(n, dtype=bool); yrs = np.full(n, np.nan)
    for i in range(n):
        y = payback_years(n_cust, margin[i], growth[i], horizon_mo=life_yr*12)
        if y is not None:
            pays[i] = True; yrs[i] = y
    p = pays.mean() * 100
    med = np.nanmedian(yrs) if pays.any() else float('nan')
    tag = "WITH NCI (878)" if with_nci else "WITHOUT NCI (%d)" % n_cust
    print("\n  [%s | %d-yr gear life | n=%d]" % (tag, life_yr, n))
    print("     P(pay back within life) : %.1f%%" % p)
    print("     median payback          : %.1f yr" % med)
    return p, med

def run_montecarlo():
    print("\n" + "=" * 78)
    print("(C) MONTE CARLO  --  margin + growth uncertainty, by gear life")
    print("=" * 78)
    for life in (8, 10, 12):
        montecarlo(with_nci=True, life_yr=life)
        montecarlo(with_nci=False, life_yr=life)

if __name__ == "__main__":
    unit_economics()
    nci_comparison()
    growth_projection()
    run_montecarlo()

    # emit curves for the website chart: PERCENT of the upgrade cost recovered
    # over time, across the REAL uncertainty -- the wireless CASH margin (the
    # driver that swings payback). Scoped to the 878 customers the $1.2M serves.
    # NCI staying-vs-leaving is only a ~9% wrinkle, reported in the caption, not
    # drawn as a co-equal line.
    import json
    GEAR_LIFE_YR = 10
    MONTHS = 132
    def curve(n_start, margin, arpu_yr, n_cap=None, ramp_mo=30):
        # n_cap set => customers ramp linearly from n_start to n_cap over ramp_mo,
        # and capex covers the full capacity (radios for n_cap).
        cap_n = n_cap if n_cap else n_start
        capex = capex_for(cap_n); s = float(n_start); c = 0.0; pct = []; pay = None
        for t in range(MONTHS):
            if n_cap:
                s = n_start + (cap_n - n_start) * min(t / ramp_mo, 1.0)
            arpu = arpu_yr/12.0 * (1.0 + ARPU_INFL)**(t/12.0)
            c += s * arpu * margin
            pct.append(round(c/capex*100))
            if pay is None and c >= capex: pay = (t+1)/12.0
        return pct, (round(pay,1) if pay else None)
    step = 3
    mo = list(range(1, MONTHS+1, step))
    NO_NCI = round(CUST * (1 - NCI_SHARE))   # 878 less NCI's share = 685
    CAP    = RADIOS_PLAN                      # 1,035 = the District's own budgeted capacity
    # Five lines, each adding one lever, all at the $40 base unless noted:
    #  WORST  = 38% margin AND a full NCI exodus (floor).
    #  PLAN   = the proposed single $40 tier at the audited ~45% cash margin.
    #  GROWTH = SAME $40 / same margin, sign-ups ramp to the budgeted 1,035 radios.
    #           Isolates the subscriber-growth lever (NLOS reach) on its own.
    #  TIERED = +tiering, blended ~$45 (premium 500Mb tier; ~34% chose the TOP legacy tier).
    #  POPULAR= +tiering +growth to the budgeted 1,035 capacity +top-of-range 55% margin.
    #  BEST   = premium tiering (~$48 blend / $576) + 58% margin + growth to ~1,200 (returning
    #           customers PLUS new NLOS-reached homes, +37%). The optimistic ceiling.
    CAP_BEST = 1200
    # (name, n_start, margin, arpu, n_cap, dash, color)
    SC = [("Worst case — 38% margin + full NCI exodus", NO_NCI, 0.38, 480, None,  '',     '#c8521f'),
          ("District's single-tier plan ($40)",          CUST,   0.45, 480, None,  '',     '#2e7d52'),
          ("More sign-ups, same $40 price (fills to 1,035)", CUST, 0.45, 480, CAP,  '5 3',  '#3457b3'),
          ("With tiered pricing",                         CUST,   0.45, 540, None,  '2 4',  '#356a72'),
          ("If it's popular — tiering + growth",          CUST,   0.55, 540, CAP,   '8 4',  '#b8860b'),
          ("Best case — premium tiering + growth into the new coverage", CUST, 0.58, 576, CAP_BEST, '10 4', '#a21caf')]
    out = {"gear_life_yr": GEAR_LIFE_YR, "months": mo, "scenarios": []}
    for nm, ns, m, ar, ncap, dash, col in SC:
        pct, pay = curve(ns, m, ar, ncap)
        out["scenarios"].append({"name": nm, "pay_yr": pay, "color": col, "dash": dash,
                                 "end_pct": pct[-1],
                                 "pct": [pct[i] for i in range(0, MONTHS, step)]})
    with open("recovery_model_output.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("\n[wrote recovery_model_output.json]  scenarios:",
          [(s["name"], s["pay_yr"], "end %d%%" % s["end_pct"]) for s in out["scenarios"]])
