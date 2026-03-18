# ECP Design Project

## What This Is
JSW One TMT ECP (Ex-Channel Partner) price creative updater. When steel prices change,
this project parses the new Excel, edits Canva design templates via the Canva MCP API,
exports PNGs per state, and saves them locally.

## Project Structure
```
ECP-Deployment/
  CLAUDE.md                          -- This file
  tools/
    parse_ecp_prices.py              -- Excel parser (openpyxl), outputs JSON
    extract_canva_elements.py        -- Canva element extractor (truncation workaround helper)
  workflows/
    update_ecp_prices.md             -- Step-by-step SOP for the full workflow
  excel files/                       -- Place new Excel files here
  ECP_{date}/                        -- Output folder per price update session
    Fe 550/                          -- 15 state PNGs (Fe 550 grade)
    Fe 550D/                         -- 5 state PNGs (Fe 550D grade)
```

## Key Canva Resources
- **ECP Backup Claude** folder: `FAHDLGc585Q` (contains the master designs)
- **Fe 550 master:** `DAHARiU82lw` (15 pages, one per state)
- **Fe 550D master:** `DAHARr6J6gc` (5 pages, one per state)
- We edit the masters directly. The folder name "ECP Backup Claude" IS the backup
  mechanism, plus Canva has built-in version history.

## Quick Start
```bash
# 1. Parse the new Excel (effective_date is REQUIRED)
python tools/parse_ecp_prices.py "excel files/<filename>.xlsx" "<effective_date>"

# 2. Follow the workflow in workflows/update_ecp_prices.md
#    (Edit via Canva MCP tools -> export PNGs -> save locally)
```

## Critical API Limitation: Response Truncation

The Canva `start-editing-transaction` response truncates at approximately 100K characters.
For Fe 550 (15 pages x ~27 elements each), **pages 13-15 are cut off** and their element IDs
are invisible in the response.

### Workaround (mandatory for Fe 550 design):
1. Open a **TEMPORARY** editing transaction on the Fe 550 design
2. Use `perform-editing-operations` to **delete TEXT elements from pages 1-4**
   (this reduces the response payload enough to reveal pages 13-15)
3. The response from step 2 now contains element IDs for pages 13-15 -- **record them**
4. **Cancel** this temporary transaction (design is unchanged)
5. Open a **FRESH** editing transaction
6. Edit pages 1-12 normally (their element IDs are visible)
7. For pages 13-15, use the element IDs recorded in step 3

**This workaround is NOT needed for Fe 550D** (only 5 pages, fits within response limit).

The utility `tools/extract_canva_elements.py` can help parse large API responses
to extract element IDs and generate delete operations.

## Excel Format
The Excel (e.g. `Book 69.xlsx`) has **ONE sheet** named `Sheet1` with 18 regional pricing
blocks arranged **side-by-side** in columns. It does NOT have separate sheets per grade.
See `tools/parse_ecp_prices.py` for the exact column-to-region mapping (REGION_COLUMNS dict).

Key rows (same across all regions):
- Row 20: Discount % as decimal (e.g. 0.03 = 3%)
- Rows 28-33: ECP per-bar prices for 12mm, 10mm, 8mm, 16mm, 20mm, 25mm

## Export Strategy
- Export PNGs in **batches of ~6 pages** per `export-design` API call
- Download exported files via `curl -L -o <filename> <canva_download_url>`
- Naming: `{StateName}_Fe550.png` or `{StateName}_Fe550D.png`

## Edge Cases
- Price values may have **trailing spaces** (e.g. "835 ") -- `find_and_replace_text` handles this
- Price values may have **leading spaces** (e.g. " 387") -- always read first, match exact
- The **discount % element** varies by page (standalone vs. inline) -- always read first
- Himachal Pradesh (page 10) has a slightly different layout but same logic works
- If a price like "385" appears in multiple elements on same page, target by `element_id`
- **Negative discounts** in Excel: use `abs()` (e.g. Sonipat Fe550D = -0.01 -> 1%)
- **Zero discounts**: keep as 0% (e.g. Himachal Fe 550)

## Page-to-State Mapping
See `workflows/update_ecp_prices.md` for the complete mapping.

## Python Environment
- Python 3.x with openpyxl installed
- Install dependencies: `pip install openpyxl`
