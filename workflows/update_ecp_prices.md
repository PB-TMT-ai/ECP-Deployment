# Workflow: Update ECP Price Creatives

## Objective
Update JSW One TMT ECP price creatives in Canva with new prices, discount percentages, and effective dates after each price announcement. Export updated designs and organize into dated folders.

## Required Inputs
1. **Excel file** placed in `ECP-Deployment/` with updated prices (see format below)
2. User confirmation to proceed with the update

## Source Designs (Templates — DO NOT EDIT DIRECTLY)
Located in Canva folder **"ECP Backup Claude"** (`FAHDLGc585Q`):

| Design | ID | Pages | Grade |
|--------|-----|-------|-------|
| ECP_Jan_Fe 550_All_3rd Feb | `DAHARiU82lw` | 15 | Fe 550 |
| ECP_Jan_Fe 550D_All_3rd Feb | `DAHARr6J6gc` | 5 | Fe 550D |

## Page-to-State Mapping

### Fe 550 (15 pages)
| Page | State |
|------|-------|
| 1 | Bihar |
| 2 | Jharkhand |
| 3 | West Bengal |
| 4 | Odisha |
| 5 | Madhya Pradesh |
| 6 | Chattisgarh |
| 7 | Jammu |
| 8 | Kashmir |
| 9 | Uttarakhand |
| 10 | Himachal Pradesh |
| 11 | Uttar Pradesh |
| 12 | Delhi |
| 13 | Haryana |
| 14 | Rajasthan |
| 15 | Punjab |

### Fe 550D (5 pages)
| Page | State |
|------|-------|
| 1 | Uttar Pradesh |
| 2 | Delhi |
| 3 | Haryana |
| 4 | Rajasthan |
| 5 | Punjab |

## Excel Format
The Excel (e.g. `Book 69.xlsx`) has **ONE sheet** named `Sheet1` with **18 regional pricing blocks** arranged side-by-side in columns (Agra in col B, Delhi in col H, Sonipat in col N, etc.).

Key rows (same across all regions):
- Row 20: Discount % as decimal (e.g. 0.03 = 3%), in Fe550/Fe550D discount columns
- Row 28: ECP for one 12mm bar
- Row 29: ECP for one 10mm bar
- Row 30: ECP for one 8mm bar
- Row 31: ECP for one 16mm bar
- Row 32: ECP for one 20mm bar
- Row 33: ECP for one 25mm bar

See `tools/parse_ecp_prices.py` `REGION_COLUMNS` dict for exact column-to-region mapping.
The parser handles all extraction; no manual reading of the Excel is needed.

## Execution Steps

### Step 1: Parse Excel
```bash
python tools/parse_ecp_prices.py "excel files/<filename>.xlsx" "<effective_date>"
```
The `effective_date` is **required** (e.g. `"6th March 2026"`). Outputs JSON with all prices organized by grade and state.

### Step 2: Edit Master Designs Directly
Edit the master designs in-place. The Canva folder "ECP Backup Claude" serves as the
backup mechanism, and Canva has built-in version history for rollback.

**Do NOT duplicate** — duplication adds complexity with no practical benefit.
If a backup is truly needed, use `merge-designs` with `create_new_design` BEFORE editing,
but this is optional.

### Step 3: Read Current Content
For each duplicated design:
1. `start-editing-transaction` with the new design ID
2. Read the text elements to identify element IDs for prices, discount, and date

### Step 3a: Truncation Workaround (Fe 550 ONLY)
The `start-editing-transaction` response truncates at ~100K characters. For Fe 550
(15 pages x ~27 text elements), **pages 13-15** (Haryana, Rajasthan, Punjab) are
cut off and their element IDs are not returned.

**Workaround procedure:**
1. Open a TEMPORARY `start-editing-transaction` on Fe 550
2. Use `perform-editing-operations` to delete TEXT elements from pages 1-4
   (reduces payload enough to reveal pages 13-15)
3. The response now contains element IDs for pages 13-15 — **record them**
4. `cancel-editing-transaction` (discards deletions, design unchanged)
5. Open a FRESH `start-editing-transaction` — edit pages 1-12 normally
6. For pages 13-15, use the element IDs recorded in step 3

The utility `tools/extract_canva_elements.py` can help parse large API responses.

**This workaround is NOT needed for Fe 550D** (5 pages fits within response limit).

### Step 4: Edit Prices
Use `perform-editing-operations` with `find_and_replace_text` operations:

**Per page, replace:**
- Each of 6 old prices → new prices (match exact old value from read)
- Old discount % number → new discount %
- Old discount footnote → new footnote (e.g., `*3% flat discount...` → `*5% flat discount...`)
- Old date → new date (e.g., `1st February 2026` → `6th March 2026`)

**Important:** Batch operations per page — send all replacements for a page in one `perform-editing-operations` call.

### Step 5: Commit Changes
After editing all pages:
- Show user thumbnails for verification
- On confirmation, `commit-editing-transaction`

### Step 6: Export
Export PNGs in **batches of ~6 pages** per `export-design` API call:
```
Batch 1: pages: [1, 2, 3, 4, 5, 6]
Batch 2: pages: [7, 8, 9, 10, 11, 12]
Batch 3: pages: [13, 14, 15]
```
Each batch returns download URLs. Download files using curl:
```bash
curl -L -o "{StateName}_Fe550.png" "<canva_export_download_url>"
```

### Step 7: Create Folders & Save

**Canva:**
- `create-folder` named `ECP_{date}` under root
- `move-item-to-folder` to move both designs into the new folder

**Local:**
```
ECP-Deployment/ECP_{date}/
  ├── Fe 550/
  │   ├── Bihar_Fe550.png
  │   ├── Jharkhand_Fe550.png
  │   └── ...
  └── Fe 550D/
      ├── Uttar Pradesh_Fe550D.png
      └── ...
```

Download each exported PNG using the download URLs from Step 6.

## Edge Cases & Lessons Learned
- **Price values with spaces:** Some prices in the designs have leading spaces (e.g., " 387"). Use the exact text from the `get-design-content` read when doing find_and_replace.
- **Discount % position varies:** On some pages the discount number appears as a standalone text element, on others it's inline. Always read first.
- **Himachal Pradesh layout differs slightly:** The discount text position is different on page 10. Same find_and_replace logic still works.
- **Batch edits carefully:** The Canva API processes `find_and_replace_text` across the entire element. If a price value (e.g., "385") appears in multiple elements on the same page, match by element_id to target correctly.
- **API response truncation:** Fe 550 (15 pages) exceeds the ~100K char response limit. Pages 13-15 are invisible. See Step 3a for the workaround.
- **Trailing spaces in prices:** Values like `"₹ 835 "` (with trailing space) still match correctly with `find_and_replace_text` — no need to trim.
- **Export batching:** Exporting all 15 pages in a single call may timeout. Use batches of ~6 pages.
- **Download method:** Use `curl -L -o <filename> <url>` to download exported PNGs from Canva.
- **Negative discounts in Excel:** Use `abs()` value (e.g., Sonipat Fe550D = -0.01 → 1%).
- **Zero discounts:** Keep as 0% and update the design accordingly (e.g., Himachal Fe 550).

## Tools Used
- `tools/parse_ecp_prices.py` — Excel parser (Python, openpyxl)
- Canva MCP tools: merge-designs, start-editing-transaction, perform-editing-operations, commit-editing-transaction, export-design, create-folder, move-item-to-folder

## Output
- Updated designs in Canva (in dated folder)
- PNG files locally in `ECP-Deployment/ECP_{date}/`
