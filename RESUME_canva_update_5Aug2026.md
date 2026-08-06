# RESUME PLAN — ECP Poster Update (effective 5th August 2026)

**Status:** Prepared and ready to execute. **Blocked** only on the Canva connector being
enabled *in the chat session* (`enabledInChat: true`). The live Canva designs are currently
**unchanged** — no edits have been committed.

## Inputs (decided with user)
- **Excel:** `ECP_Analysis.xlsx`, tab **`ECP Mar 25`** (user-selected).
- **Effective date to print:** `With effect from: 5th August 2026` (replaces `6th July 2026`).
- **Discount source:** the `Fe550 discount` / `Fe550D discount` columns (row-19 header,
  row-20 decimal) per representative city — NOT computed. See `ecp_prices_mar25.json`.
- **Representative city per state** (validated: their sheet prices match the live posters):
  UP=Agra, Haryana=Sonipat, Punjab=Punjab (except Chandigarh), Odisha=Orissa; others = own name.

## Key facts discovered
- The `ECP Mar 25` tab's **prices are identical** to what is already live on the posters,
  **except Kashmir Fe 550** (see below). So Fe 550 is effectively date-only + Kashmir prices.
- The real changes are **Fe 550D discounts** (5 pages) + the effective date everywhere.
- Fe 550D design now has **6 pages** (a Bihar page was added) — include it.
- Kashmir Fe 550 legitimately carries a **13% discount** (already on the poster) — keep it.

## Designs
| Design | ID | Pages | Notes |
|--------|----|-------|-------|
| Fe 550  | `DAHARiU82lw` | 15 | title stale ("...20th April"); pages are FIXED, editable |
| Fe 550D | `DAHARr6J6gc` | 6  | title stale; pages FIXED, editable |

Per-page edit uses `edit-design` with `is_responsive:false, is_editable:true, is_empty:false`.
Open a transaction via `read-design(open_transaction:true)`; commit is the tool's
verify/commit step after thumbnail check. Element locator IDs below are design-stable.

---

## FE 550D — `DAHARr6J6gc` (6 pages) — element IDs + ops

Ops legend: `date` = find_and_replace_text `6th July 2026`→`5th August 2026`;
`foot` = find_and_replace_text on footnote element (`N% flat`→`M% flat`);
`big#` = replace_text on the big white 32.8px number element.

| Pg | State | Page ID | big# element / new val | footnote element / change | date element |
|----|-------|---------|------------------------|---------------------------|--------------|
| 1 | Uttar Pradesh | `PByt888ZZHqSDt2l` | *(unchanged, 3)* | *(unchanged, 3%)* `-LBFbHjHqSy5qRfmd` | `-LBwPgJ8TwrRzm0yY` |
| 2 | Delhi | `PBScfwKzFp9XqgYd` | `-LBGs3tWXx5YlTy2x` → **4** | `-LB0DVsSsb6LpSZRT` 3%→**4%** | `-LBQTysq7y4kb84SY` |
| 3 | Haryana | `PBPBsPZDfC1x2v6Z` | `-LBq0zRP9Vx4BZcQh` → **3** | `-LBj8BHW3bW8bQcNj` 4%→**3%** | `-LBspPq3SSmMbKjDx` |
| 4 | Rajasthan | `PB9MXrZXR1xSFmHM` | `-LB93bFGJnQXKJs5k` → **3** | `-LBCNtNfHQ5d6lwBq` 4%→**3%** | `-LBCz27f2Zy6cbwbs` |
| 5 | Punjab | `PBQCPk3WY6Y8bxzB` | `-LB4SsgVMRrnKZXHg` → **3** | `-LBTTSfgRz1BwQXrs` 4%→**3%** | `-LBKbsQzknsjR1yfm` |
| 6 | Bihar | `PBh51Dv5WhpJ8v7p` | `-LBH20DkCBdnmZCTp` → **4** | `-LBCHgSCJWhRRBWCR` 3%→**4%** | `-LBP7Rl0LjBX38WL1` |

Full element_id = `<Page ID>` + `<suffix>` (e.g. `PBScfwKzFp9XqgYd-LBGs3tWXx5YlTy2x`).
Footnote full text = `*<N>% flat discount applicable on recommended price`.
Fe 550D prices are unchanged from live — do not edit price cells.

---

## FE 550 — `DAHARiU82lw` (15 pages) — plan

Element IDs must be re-read at run time (needs the **pages 13–15 truncation workaround**:
open a throwaway transaction, delete text on pages 1–4 to reveal IDs for pages 13–15, record
them, cancel, then edit fresh). Target values per page below (8/10/12/16/20/25 mm | discount):

| Pg | State | Prices (8/10/12/16/20/25) | Disc | vs live |
|----|-------|---------------------------|------|---------|
| 1 | Bihar | 383/584/828/1472/2300/3593 | 3% | same → date only |
| 2 | Jharkhand | 383/584/828/1472/2300/3593 | 3% | same → date only |
| 3 | West Bengal | 382/583/826/1468/2294/3584 | 4% | same → date only |
| 4 | Odisha | 380/580/822/1461/2283/3567 | 3% | same → date only |
| 5 | Madhya Pradesh | 380/580/822/1461/2283/3567 | 3% | same → date only |
| 6 | Chattisgarh | 371/566/802/1426/2228/3480 | 4% | same → date only |
| 7 | Jammu | 385/588/834/1483/2317/3619 | 3% | same → date only |
| 8 | **Kashmir** | **417/637/904/1607/2511/3923** | 13% | **PRICES CHANGE** (live 419/640/909/1616/2525/3945) + date |
| 9 | Uttarakhand | 378/576/817/1452/2269/3545 | 3% | same → date only |
| 10 | Himachal Pradesh | 385/588/834/1483/2317/3619 | 3% | same → date only |
| 11 | Uttar Pradesh | 384/586/831/1477/2308/3606 | 3% | same → date only |
| 12 | Delhi | 379/578/819/1456/2275/3554 | 3% | same → date only |
| 13 | Haryana | 379/578/819/1456/2275/3554 | 4% | same → date only |
| 14 | Rajasthan | 382/583/827/1470/2297/3589 | 3% | same → date only |
| 15 | Punjab | 377/574/814/1447/2261/3532 | 4% | same → date only |

At run time: read each page, replace `6th July 2026`→`5th August 2026`; for any bar price
or discount that differs from the table above, find_and_replace to the table value
(only Kashmir prices are expected to differ). Prices are shown as `₹ <value>` (with a space).

---

## After editing both designs
1. Thumbnail-verify every edited page, then commit each transaction.
2. `export-design` PNGs in batches (~6 pages); download via `curl -L -o`.
   Naming: `<State>_Fe550.png` / `<State>_Fe550D.png`.
3. `create-folder` `ECP_5th August 2026`; `move-item-to-folder` both designs into it.
4. Save PNGs locally under `ECP_5th August 2026/Fe 550/` and `/Fe 550D/`;
   commit them to the repo branch so the user can pull them.

## Progress log
- Fe 550D pages 1–2 were once staged in transaction `6847109172776726229`, but that
  transaction died when the connector dropped. **Nothing committed.** Re-apply from scratch.
