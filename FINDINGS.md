# Okanogan PUD Wireless (WISP) Revenue — Findings from the PRA Data
*Prepared for savelocalbroadband.com — analysis of the campaign's PRA Request dataset. Date: 2026-06-14.*

## The headline answer (the number you wanted to pin down)

**Wireless ("WISP") wholesale revenue is ~$1.1 million per year — about ONE-THIRD (≈32–34%) of the PUD's
telecom operating revenue.** This is computed directly from the PUD's own monthly telecom billing reports,
not estimated.

| Year | Wireless $ (billed) | Telecom op. rev (ex-tax) | **Wireless % of telecom** | Wireless % of retail broadband* |
|------|--------------------:|-------------------------:|:-------------------------:|:-------------------------------:|
| 2021 | $1,077,378 | $3,565,066 | **30.2%** | 72.3% |
| 2022 | $1,121,181 | $3,483,143 | **32.2%** | 72.2% |
| 2023 | $1,155,344 | $3,474,530 | **33.3%** | 72.4% |
| 2024 | $1,168,684 | $3,388,426 | **34.5%** | 72.1% |
| 2025 | $1,139,466 | $3,361,413 | **33.9%** | 70.7% |
| 2026 (Jan–May) | $435,352 | $1,351,275 | **32.2%** | 68.3% |

\* "Retail broadband" = wireless + fiber last-mile connections (E-codes), i.e. what RSPs sell to homes/small
businesses — excludes carrier dark-fiber/wavelength/colocation. Among the services households actually buy,
**wireless is ~70%.**

**Other denominators (so you can pick the right framing):**
- % of **total telecom operating revenue** (~$3.25–3.5M/yr): **~33%** ← the relevant number for a "should we keep wireless" decision.
- % of **retail/last-mile broadband** (wireless + fiber-to-home): **~71%**.
- % of the audited **"$2.81M wholesale telecom line"** (2024): **~42%**.
- % of **total PUD revenue, all utilities** (2026 budget = $83.2M): **~1.3%** (technically true but apples-to-oranges; the electric utility dwarfs telecom).

## How this was computed (method)
- Source: the 65 monthly **"… Monthly Telecom Report by Code.xlsx"** files (Jan 2021 – May 2026). Column **J**
  = line revenue (Quantity × Price + one-time NRC).
- Each of the **179 billing codes** was classified by prefix. **Wireless = all "W" codes** (service tiers
  W06–W09 "Cambium Wireless 3/1–20/5", W71–W77 "Broadband Wireless", plus radios W03/W10 and CPE W81–W86).
- **Cross-checked three independent report cuts** (by Code, by RSP, and Total) for multiple months — they
  agree **to the dollar**.
- **Reconciles to the audit:** 2024 ex-tax billed minus one-time build/fees ≈ **$3.25M = the audited "total
  telecom operating revenue."** So the billing reports are a faithful proxy for audited revenue — and they
  break out the wireless/fiber split the audit does **not**.

Output files: `monthly_revenue_by_category.csv`, `yearly_revenue_by_category.csv`.

## What this means for the website's numbers
| Website figure | Status | Correction / note |
|---|---|---|
| "~$1M/yr **estimated** wireless revenue" | **Low & under-stated** | Actual **~$1.1–1.17M/yr**, and — more importantly — **~⅓ of telecom revenue**. No longer an estimate: it's from the PUD's own billing. |
| "$3.25M total telecom operating revenue (2024)" | ✅ Confirmed | Matches audited; our billing reconciles. |
| "$2.81M wholesale telecom line (2024)" | ✅ Audited | Wireless is ~42% of this subset. |
| "$808,166 telecom net surplus (2024)" | ✅ (audited, SAO) | Segment is **profitable**; wireless rates are cost-based by law (RCW 54.16.330), so wireless is at least break-even and contributes to that surplus. |
| "158 access points" / "46 sector sites" | ⚠️ Verify | Not cleanly reproducible from the data yet. Tarana plan names 7 current + 3 future tower sites; `WiFi AP counts and value.xlsx` lists ~70 low-use Cambium APs. Tie these claims to a specific source sheet. |
| "~$1.2M first-phase upgrade cost" | ⚠️ Define scope | Tarana files: **7 current sites network-only = $370,783**; *with* customer Remote Nodes (~$790 each @ 60% take) it's materially higher. State exactly which scope $1.2M covers. |

## The strongest, data-backed arguments
1. **Wireless is a third of the telecom business (~$1.1M/yr), not a rounding error.** You don't abandon a
   line that large that is, by the PUD's own cost-based-rate rule, at least covering its costs.
2. **Revenue is stable, not collapsing.** Monthly wireless revenue ran ~$83K (2021) → ~$98K peak (2024) →
   ~$86K (early 2026). **The last 12 months on record ($91.7K/mo avg) are *higher* than the first 12 ($89.8K/mo).**
   The letter's "subscription rates have steadily declined" is contradicted by the revenue record.
3. **The cost-benefit is favorable.** Network-only upgrade of all 7 current sites = **$371K — under 4 months
   of wireless revenue.** Even a fuller upgrade is on the order of ~1 year of wireless revenue.
4. **7 local ISPs depend on this network**, and for most, wireless is the *majority* of what they buy from
   the PUD (Highland 77%, Will Connect 69%, CommunityNET 68%, Methownet 56%). ~2,700 households/businesses
   are served. Pausing investment hits local businesses and rural customers directly.
5. **The PUD's logic is circular:** the letter says subscribers leave because competitors offer faster
   service — which is the argument *for* upgrading (Tarana 6 GHz), not for freezing the network.
6. **The decline is concentrated in ONE reseller, not the platform.** Per the District's own per-RSP monthly
   reports, **NCI Datacom** (tied to/acquired by out-of-area **Core Fiber**) lost ~25% of its wireless
   subscribers in the past year — **52% of the entire county-wide decline** — concentrated in Dec 2025–Jan 2026
   (≈ three-quarters of the "cliff"). Every other reseller held far steadier and Will Connect lost no net
   customers. **CORRECTION (NCI complaint, well-founded):** those customers did **not** appear on other PUD
   resellers (no other reseller grew) — but that does **NOT** mean they "left the network." NCI also operates its
   **own towers** and buys only ~37% of its PUD spend as wireless, so the most likely read is that NCI **migrated
   those customers onto its own network** (or they churned) — we cannot, and must not, claim they left NCI or the
   county. The defensible fact is narrower: one reseller's **PUD-wholesale book shifted**, concentrated in that
   account — a reseller-level change, not weakening platform-wide demand. **Do NOT use "collapse," "failure," or
   "service collapse," and do not assert WHY customers left NCI.** (A customer leaving a reseller's wholesale
   account ≠ a customer leaving the county.)
7. **It's about reliability, not speed.** Most rural homes need only ~10 Mbps (1080p streaming + email; the
   network tops out at 20 Mbps, ~43% on ≤7 Mbps). Customers leave a connection that doesn't *work*, not one
   that's merely "slow." Across the three reporting providers, Starlink is ~15% of cancellations — a minority
   (though rising in the most recent months) — the case for a reliable, modern network, not for abandoning it.

## Honest caveats / where the PUD has a point
- **Subscriber counts *are* slowly declining:** wireless broadband subs peaked ~3,238 (2022) and are ~2,726
  (May 2026) — about **−7% since 2021, −16% from peak**, and the decline has **accelerated** in 2024–2026.
  Revenue held up via mix-shift to higher tiers, but the customer base is shrinking. **Context (argument #6):
  more than half the *past-year* wholesale decline is concentrated in one reseller's account (NCI/Core Fiber, which also runs its own towers) — a reseller's book shifting, not broad erosion of demand.**
- The "~$1M" the website used isn't *wrong* in magnitude — it's just under-stated and was an estimate; the
  power is in re-basing it on PUD source data and reframing it as a **share**.
- Wireless's true economic value is slightly higher than the W-code line alone, because WISP-RSPs also buy
  internet bandwidth (I-codes) to feed those customers — but keep the headline to W-codes to stay defensible.

## Per-RSP wireless dependence (FY2025)
| RSP | Wireless $/yr | Wireless % of its PUD spend | Avg wireless subs |
|---|---:|---:|---:|
| Highland | $381,489 | 77% | 1,050 |
| NCI Datacom | $269,345 | 37% | 717 |
| CommunityNET | $219,900 | 68% | 542 |
| Methownet.com | $108,941 | 56% | 342 |
| Will Connect | $104,028 | 69% | 249 |
| PC Telecom | $39,831 | 48% | 114 |
| BHPcom | $15,932 | 24% | 33 |
| **Total** | **$1,139,466** | — | **~3,047** |
