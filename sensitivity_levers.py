"""One-off: exact lever-table deltas from the CURRENT balanced base (how-we-modeled-risk §08).
Runs cost_recovery_mc on the balanced config with one lever perturbed at a time.
Reproducible (same SEED as the model). Not wired into the site build; regenerate the
§08 table by hand from this output."""
from montecarlo_robust import cost_recovery_mc, SCENARIOS

BAL = dict(SCENARIOS['balanced'])   # headline base = always-on conservative bandwidth (never pinned)

def run(label, **over):
    scn = dict(BAL); scn.update(over)
    p = cost_recovery_mc(scn=scn, verbose=False)['p_payback']
    return label, p

base = cost_recovery_mc(scn=dict(BAL), verbose=False)['p_payback']
rows = [
    run('FEAR  Starlink surge (+2%/yr churn)',      starlink=0.02),
    run('FEAR  Reseller/market shock (~20%)',       shock=0.20),
    run('FEAR  NCI price war (-2 pts, 3yr)',        pricewar=0.02),
    run('CHOICE District freezes rate flat (RT0)',  rate_track=0.0),
    run('CHOICE Strictest wear-out accounting',     cliff=True),
    run('SKEPTIC Strip retention+funded-growth',    sticky=0.0, community=0.0, coverage=0.0),
    run('STRESS bandwidth hypothetically zero',     bw_mbps=0.0),
    run('UPSIDE bandwidth at documented 2.8 Mbps',  bw_mbps=2.8),
    run('WHATIF price drops $1.50->$1.00',          bw_price=1.00),
    run('ALL THREE FEARS together',                 starlink=0.02, shock=0.20, pricewar=0.02),
    run('DELAY  build delayed 1 year',              delay=1.0),
    run('DELAY  build delayed 2 years',             delay=2.0),
    run('DELAY  build delayed 3 years',             delay=3.0),
    # --- card-specific settings (fear/upside rebuttal cards on the page) ---
    run('CARD  Starlink surge +3%/yr',              starlink=0.03),
    run('CARD  market shock 25% one-time',          shock=0.25),
    run('CARD  remove stickiness only',             sticky=0.0),
    run('CARD  remove community only',              community=0.0),
]

print(f"\nBALANCED BASE : {base:.1f}%\n" + "-"*54)
for label, p in rows:
    print(f"  {label:44s} {p:5.1f}%   ({p-base:+.1f})")
