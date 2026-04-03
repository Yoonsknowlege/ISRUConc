# Data Dictionary — `phase2_453_families.json`

This document describes each field in the released 453-family dataset.

## File format

JSON array of 453 objects. One object per unique simple patent family.

## Fields

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `lens_id` | string | `"172-275-795-866-748"` | Lens.org unique identifier for the patent family representative record. |
| `title` | string | `"Autonomous mobile mechanically deployed spaceport …"` | Patent title (English). |
| `abstract` | string | `"An autonomous mobile mechanically …"` | Patent abstract (English). May be empty for a small number of records. |
| `cpc` | string | `"B64G5/00;;B64G1/002;;B64G1/1071"` | CPC (Cooperative Patent Classification) codes assigned to the patent. Multiple codes are delimited by `;;` (double semicolon). Parse with `cpc.split(';;')` to obtain a list. |
| `itc_codes` | array[string] | `["4-3", "4-4"]` | ITC (Integrated Technology Classification) domain codes assigned by the CPC-anchor + keyword tagging logic described in the manuscript and `isru_data.py`. Empty array `[]` for domain-external families (80 records). |
| `itc_names` | array[string] | `["Landing Pads", "Deployable Structures"]` | Human-readable labels corresponding one-to-one with `itc_codes`. |
| `source` | string | `"r2_keep"` or `"rescue"` | Provenance within the screening pipeline. `r2_keep` = passed both round-1 and round-2 validation (443 families). `rescue` = initially excluded but rescued during precision audit (10 families). |
| `publication_year` | integer | `2022` | Publication year of the representative patent document, as reported by Lens.org. Range in this dataset: 2000–2026. Note: this reflects the Lens publication date (grant or application publication), not the earliest priority date. |

## Delimiter convention

The `cpc` field uses `;;` as a delimiter because individual CPC codes may contain commas or semicolons in some export formats. To parse:

```python
cpc_list = record['cpc'].split(';;')
```

## Known limitations

- **No jurisdiction field:** Country-level analyses (e.g., CN-share in Table 7) require the original Lens.org export, which includes a `Jurisdiction` column not released here.
- **No earliest-priority-date field:** Priority-date-based timelines require the original export.
- **Domain-external families:** 80 records have `itc_codes: []`. These are retained for completeness and CPC-level analyses.
- **Residual false positives:** The dataset may contain edge-case false positives from LLM-assisted screening. See manuscript Appendix A.6 for the precision audit protocol.
