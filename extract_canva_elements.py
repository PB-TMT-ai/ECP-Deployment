"""
extract_canva_elements.py — Parses Canva editing API responses to extract element IDs.

Used for the Fe 550 truncation workaround: when the start-editing-transaction response
exceeds ~100K chars and pages 13-15 are cut off, this tool helps extract element IDs
and generate delete operations.

Usage:
  # List all elements grouped by page
  python tools/extract_canva_elements.py <json_file>

  # Generate delete operations for TEXT elements on pages 1-4
  python tools/extract_canva_elements.py <json_file> --deletable 1-4

  # Extract element IDs + text for pages 13-15
  python tools/extract_canva_elements.py <json_file> --extract 13-15

The <json_file> should contain the raw JSON response from start-editing-transaction
or perform-editing-operations (saved from Claude's tool-results).

To save a tool response as JSON:
  1. Find the tool-results file in Claude's project cache
  2. Copy it to a working location
  3. Run this script on it
"""

import json
import re
import sys
import os


def parse_range(range_str):
    """Parse a page range string like '1-4' or '13-15' into a set of page numbers."""
    parts = range_str.split("-")
    if len(parts) == 2:
        return set(range(int(parts[0]), int(parts[1]) + 1))
    elif len(parts) == 1:
        return {int(parts[0])}
    else:
        raise ValueError(f"Invalid range: {range_str}")


def extract_elements(text):
    """Extract element entries from the API response text.

    Returns a list of dicts: {page, element_id, type, text}
    """
    elements = []
    parts = text.split('"page_index":')

    for part in parts[1:]:
        # Parse page number
        comma = part.find(",")
        if comma < 0:
            continue
        try:
            page = int(part[:comma])
        except ValueError:
            continue

        # Find element_id
        eid_start = part.find('"element_id":"')
        if eid_start < 0:
            continue
        eid_val = part[eid_start + 14:]
        eid_end = eid_val.find('"')
        if eid_end < 0:
            continue
        element_id = eid_val[:eid_end]

        # Get container type (SHAPE or TEXT)
        type_match = re.search(r'"type":"(SHAPE|TEXT)"', part[:eid_start])
        container_type = type_match.group(1) if type_match else "UNKNOWN"

        # Find text content in regions
        text_matches = re.findall(r'"text":"([^"]*?)"', part[:eid_start])
        text_content = " | ".join(
            t for t in text_matches if t not in ("character", "SHAPE", "TEXT")
        )

        elements.append({
            "page": page,
            "element_id": element_id,
            "type": container_type,
            "text": text_content,
        })

    return elements


def load_response_text(filepath):
    """Load the text content from a Claude tool-results JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "text" in item:
                return item["text"]
    elif isinstance(data, dict) and "text" in data:
        return data["text"]

    # If the file is just raw text
    if isinstance(data, str):
        return data

    raise ValueError("Could not find text content in JSON file")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/extract_canva_elements.py <json_file> [--deletable|--extract <range>]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    text = load_response_text(filepath)
    elements = extract_elements(text)

    # Determine mode
    mode = "list"
    page_filter = None
    if len(sys.argv) >= 4:
        if sys.argv[2] == "--deletable":
            mode = "deletable"
            page_filter = parse_range(sys.argv[3])
        elif sys.argv[2] == "--extract":
            mode = "extract"
            page_filter = parse_range(sys.argv[3])

    if mode == "list":
        # List all elements grouped by page
        pages = sorted(set(e["page"] for e in elements))
        for page_num in pages:
            page_elements = [e for e in elements if e["page"] == page_num]
            print(f"\n=== PAGE {page_num} ({len(page_elements)} elements) ===")
            for e in page_elements:
                text_preview = f'  "{e["text"]}"' if e["text"] else ""
                print(f"  [{e['type']}] {e['element_id']}{text_preview}")
        print(f"\nTotal: {len(elements)} elements across {len(pages)} pages")

    elif mode == "deletable":
        # Output delete operations for TEXT elements in specified pages
        deletable = [
            e for e in elements
            if e["page"] in page_filter and e["type"] == "TEXT"
        ]
        ops = [{"type": "delete_element", "element_id": d["element_id"]} for d in deletable]
        print(json.dumps(ops, indent=2))
        print(f"\n# {len(ops)} delete operations for TEXT elements on pages {sys.argv[3]}", file=sys.stderr)

    elif mode == "extract":
        # Extract element IDs + text for specified pages
        filtered = [e for e in elements if e["page"] in page_filter]
        for page_num in sorted(page_filter):
            page_elements = [e for e in filtered if e["page"] == page_num]
            print(f"\n=== PAGE {page_num} ===")
            for e in page_elements:
                if e["text"]:
                    print(f"  {e['element_id']}")
                    print(f"    text: '{e['text']}'")


if __name__ == "__main__":
    main()
