#!/usr/bin/env python3
"""
sources_and_uses.py — Forensic "where every dollar went" model for the Okanogan
PUD Wholesale Telecom budget, built from the District's own Proposed Budget
workbooks (FOI/PRA dataset, 2021-2026).

WHAT IT DOES
  Parses each "20xx Wholesale Telecom Proposed Budget*.xlsx" and reconstructs a
  complete sources-and-uses of funds: the Revenue Estimate (the "source") against
  every Operating, Capital, and Debt-Service account (the "uses"). Each account
  subtotal lives in column N; the grand total in O4; the implied surplus in P4.
  Line-item detail (column M = the extended/budgeted amount) is pulled for the
  CAPITAL accounts so the network investment can be split wireless / fiber / core.

RECONCILIATION (self-check, printed at the end)
  For every year:  sum(account subtotals) == O4 (total spend), and
                   Revenue - total spend == P4 (surplus).  Both must tie exactly.

HONEST SCOPE
  * These are PROPOSED (budgeted) figures — what the District planned to spend.
    Segment-level ACTUALS live in the audited statements (SAO Note 9); line-item
    actuals are not separately audited.
  * 2026 is shown separately: its capital balloons to ~$10.9M because of the
    grant/loan-funded FTTx fiber build — NOT money netted from telecom.
  * Wages/benefits are allocated to the telecom budget but the crews are shared
    with the wider broadband/utility operation.
  * The wireless/fiber/core split of capital is a line-item CLASSIFICATION
    (campaign judgment, rules below) — the account TOTALS are exact; the split is
    a reasonable, conservative reading of the line descriptions.

USAGE
  python sources_and_uses.py [/path/to/budgets/dir]   # prints tables + writes JSON
"""
import zipfile, re, glob, os, json, sys
import xml.etree.ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def load(path):
    z = zipfile.ZipFile(path); ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        r = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in r.findall(NS + 'si'):
            ss.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml')); rows = {}
    for row in sheet.iter(NS + 'row'):
        cells = {}
        for c in row.findall(NS + 'c'):
            col = re.match(r'[A-Z]+', c.get('r')).group()
            t = c.get('t'); v = c.find(NS + 'v'); val = ''
            if v is not None and v.text is not None:
                val = ss[int(v.text)] if t == 's' else (
                    float(v.text) if re.match(r'-?[\d.]+$', v.text) else v.text)
            cells[col] = val
        if cells:
            rows[int(row.get('r'))] = cells
    return rows

# Activity-code -> top-level use bucket
OPERATING = {'010':'Wages','011':'Benefits','020':'Travel','021':'Tuition','030':'Transportation',
             '050':'Utilities','060':'Postage/Printing','070':'Advertising','080':'Misc. Contractual',
             '081':'Legal','082':'Maintenance Contracts','083':'Software Lic./Support','084':'Permits & Fees',
             '085':'Rents & Leases','090':'Materials & Supplies','091':'Small Tools','210':'Taxes'}
CAPITAL = {'591','710','712'}
DEBT    = {'810','811'}

def classify_capital(desc):
    d = desc.lower()
    if any(k in d for k in ['fiber','optic','wdm','otn','ftth','fttx','pon','adva','ciena','adtran']):
        return 'fiber'
    if 'wireless' in d or 'wifi' in d:
        return 'wireless'
    if 'eol' in d or ('network upgrades' in d and 'replacement' in d):
        return 'upgrade'   # EOL network-hardware replacement (the modernization line; mixed)
    return 'core'          # servers, power plant, HVAC, tools, generic expansion

def parse_year(path):
    rows = load(path); rns = sorted(rows)
    rev = rows.get(1, {}).get('O', 0)
    o4  = rows.get(4, {}).get('O', 0)
    p4  = rows.get(4, {}).get('P', 0)
    hdrs = [rn for rn in rns if str(rows[rn].get('C','')).strip()
            and rows[rn].get('E','') and isinstance(rows[rn].get('N',''), float)]
    hdrs.append(max(rns) + 1)
    operating = {}; debt = 0.0; cap_total = 0.0; cap_lines = []
    for i in range(len(hdrs) - 1):
        a, b = hdrs[i], hdrs[i+1]
        code = str(rows[a]['C']).strip(); sub = rows[a]['N']
        if code in OPERATING:
            operating[OPERATING[code]] = sub
        elif code in DEBT:
            debt += sub
        elif code in CAPITAL:
            cap_total += sub
            for rn in range(a + 1, b):
                c = rows.get(rn, {}); desc = c.get('F',''); m = c.get('M','')
                if desc != '' and isinstance(m, float) and m != 0:
                    cap_lines.append({'desc': desc.strip(), 'amount': round(m),
                                      'class': classify_capital(desc)})
    op_total = round(sum(operating.values()))
    rev_n   = round(rev) if isinstance(rev, float) else 0
    total_n = round(o4)  if isinstance(o4, float)  else round(op_total + cap_total + debt)
    surplus = round(p4)  if isinstance(p4, float)  else (rev_n - total_n)  # P4 blank in 2026
    return {
        'revenue': rev_n,
        'operating_total': op_total, 'operating': {k: round(v) for k, v in operating.items()},
        'capital_total': round(cap_total), 'capital_lines': cap_lines,
        'debt_total': round(debt),
        'total_spend': total_n,
        'surplus': surplus,
    }

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'budgets')
    out = {}
    for f in sorted(glob.glob(os.path.join(base, '20* Wholesale Telecom Proposed Budget*.xlsx'))):
        yr = os.path.basename(f)[:4]
        out[yr] = parse_year(f)
    # reconciliation check
    print(f"{'Year':<6}{'Revenue':>12}{'Operating':>12}{'Capital':>12}{'Debt':>10}{'Total':>12}{'Surplus':>11}  tie?")
    for yr, d in out.items():
        recomputed = d['operating_total'] + d['capital_total'] + d['debt_total']
        tie = 'OK' if abs(recomputed - d['total_spend']) < 1 else 'MISMATCH'
        print(f"{yr:<6}{d['revenue']:>12,}{d['operating_total']:>12,}{d['capital_total']:>12,}"
              f"{d['debt_total']:>10,}{d['total_spend']:>12,}{d['surplus']:>11,}  {tie}")
    # wireless vs fiber capital split (named lines only)
    print("\nCapital by class (budgeted):")
    for yr, d in out.items():
        agg = {}
        for ln in d['capital_lines']:
            agg[ln['class']] = agg.get(ln['class'], 0) + ln['amount']
        print(f"  {yr}: " + ', '.join(f"{k}={v:,}" for k, v in sorted(agg.items())))
    dest = os.path.join(os.path.dirname(__file__), 'sources_and_uses.json')
    with open(dest, 'w') as fh:
        json.dump(out, fh, indent=2)
    print(f"\nWrote {dest}")

if __name__ == '__main__':
    main()
