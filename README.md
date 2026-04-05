# ISRU Construction Patent Analysis — Reproduction Package

**Paper:** "WBS-based patent landscape of ISRU construction: technology convergence and subsystem-level industrial participation pathways"

**Dataset:** 453 unique simple patent families (phase-two synchronized dataset)

**Release:** `v1.0-submission` — snapshot accompanying the Acta Astronautica submission (2026-04-03)

## Directory Structure

```
reproduction_package/
├── README.md
├── DATA_DICTIONARY.md                  ← Field-level schema for phase2_453_families.json
├── requirements.txt                    ← Python dependencies
├── LICENSE                             ← CC BY 4.0
├── CITATION.cff                        ← Machine-readable citation metadata
├── lens_query.txt                      ← Lens.org query logic documentation
├── data/
│   ├── isru_data.py                    ← Core data module (constants, matrices, ITC_RULES)
│   └── phase2_453_families.json        ← 453-family tagged dataset (Lens IDs, CPC, ITC tags, years, jurisdiction)
├── scripts/
│   ├── generate_all_figures.py         ← Figure generation (Figs. 2–5, S1)
│   ├── recompute_tables.py             ← Recompute Tables 4–7 from JSON dataset
│   ├── sensitivity_checks.py           ← Leave-out, classified-only, CN vs non-CN, and shared-anchor inflation checks
│   └── ISRU_Reproducibility_Pipeline.py ← Reusable parameterized analysis pipeline template
└── figures/                            ← Output directory for generated PNGs
```

## Manuscript Figure Mapping

| Manuscript Figure | Content | Source |
|---|---|---|
| Fig. 1 | Overall research framework | Conceptual diagram (not code-generated) |
| Fig. 2 | ITC domain portfolio bar chart | `fig2_portfolio_bar.png` |
| Fig. 3 | Filing-year WBS-layer tag distribution | `fig3_filing_year.png` |
| Fig. 4 | CPC co-classification heatmap | `fig4_cpc_coclass.png` |
| Fig. 5 | Jaccard similarity matrix | `fig5_jaccard_heatmap.png` |
| Fig. S1 | WBS-layer tag-share distribution | `figS1_wbs_stacked.png` (supplementary) |

### Note on Figure 3 counting unit

Figure 3 reports **annual WBS-layer tag counts**, not unique-family counts. Because one family can carry ITC tags in multiple WBS layers, that family contributes one count to each matched layer in a given year. The cumulative line therefore tracks cumulative tag counts. This is consistent with the manuscript caption: "Stacked bars report annual WBS-layer tag counts … cumulative tag counts rather than unique-family counts."

## Core Reproducibility Instrument

The primary reproducibility instrument is the **ITC codebook** (`ITC_RULES` in `isru_data.py`), which maps 15 technology domains across four WBS layers to:

- **41 CPC anchor prefixes** (e.g., 1-1 → C22B, B07B, B02C, B03)
- **102 keyword stems** (e.g., 2-1 → "3d print", "additive manufactur", "extrusion" ...)

**WBS Layer Structure:**
- WBS-1 Materials (domains 1-1 through 1-3)
- WBS-2 Manufacturing (domains 2-1 through 2-4)
- WBS-3 Robotics (domains 3-1 through 3-3)
- WBS-4 Structures & Systems (domains 4-1 through 4-5)

**Tagging logic** (OR-based, deterministic first stage):
1. If any CPC code on a patent starts with an anchor prefix → domain tag assigned
2. Else if any keyword stem matches in title+abstract → domain tag assigned
3. Multi-tagging permitted (a patent can belong to multiple domains)
4. If no domain matches → classified as domain-external

**Scope of the codebook:** `ITC_RULES` encodes the deterministic first stage of the tagging pipeline. The released `itc_codes` were further refined through LLM-assisted adjudication and human review (see manuscript §3.2 and Appendix A); the released tags are authoritative. The codebook enables any researcher to apply a comparable rule-based classification to a new patent retrieval.

## Verifiable Scope

With the data and scripts provided in this package, an independent researcher can verify:

| What | How |
|------|-----|
| **ITC tag-share distribution** (Fig. 2, Table 3) | Run `generate_all_figures.py` or recount `itc_codes` in `phase2_453_families.json` |
| **Filing-year × WBS trajectory** (Fig. 3) | Cross-reference `earliest_priority_year` × `itc_codes` in the JSON, or run `generate_all_figures.py` |
| **CPC co-classification network** (Fig. 4) | Parse the `cpc` field and rebuild the co-occurrence matrix |
| **CPC bridging centrality** (Table 4) | Run `recompute_tables.py`, or verify against `CPC_BRIDGING` in `isru_data.py` (computed from the full 4-char CPC network over all 453 families, binary adjacency, min co-occurrence = 1) |
| **Jaccard similarity pairs** (Fig. 5, Table 5) | Recompute from the `itc_codes` field in the JSON |
| **Descriptive profiles — Post-2020 share** (Table 6) | Filter intersection-set families by `earliest_priority_year >= 2020` |
| **Jurisdiction distribution** | Filter by `jurisdiction` field in JSON |
| **CN vs non-CN sensitivity** (Supplementary Table S2) | Run `sensitivity_checks.py` or filter by `jurisdiction` field |
| **Shared-anchor inflation** (4-1 ↔ 4-4, E04H15) | Run `sensitivity_checks.py` |
| **Priority-year timeline** (alternative to pub-year) | Use `earliest_priority_year` field in JSON |

**Not independently verifiable from this package alone:** Table 7 descriptive profiles beyond jurisdiction and Post-2020 share (dominant CPC prefixes and core keywords require CPC subclass look-up and qualitative judgment not included in this release).

**CPC field format:** The `cpc` field in the JSON is a `;;`-delimited string (not an array). Parse with `record['cpc'].split(';;')`. See `DATA_DICTIONARY.md` for full schema.

**Data quality:** Appendix A reports the stratified precision audit (88.3 % overall) and sensitivity analysis.

## Scope of This Package

This package supports **computational replication of the released analytical layer**: running the provided scripts reproduces the code-generated manuscript figures (Figs. 2–5, S1) and the quantitative values directly derived from the released dataset, matrices, and constants (Tables 3–6 tag counts, Jaccard pairs, and CPC centrality). It also provides a **reusable parameterized pipeline template** (`ISRU_Reproducibility_Pipeline.py`) that demonstrates how the same analytical workflow can be applied to a new patent dataset. The WBS-based ITC codebook (`ITC_RULES`) and the final tagged dataset (`itc_codes`) constitute the core reproducibility instruments.

## Requirements

```bash
pip install -r requirements.txt
```

Python 3.9+

## Quick Start

### Reproduce Figures

```bash
cd scripts
python generate_all_figures.py
```

### Recompute Tables 3–6

```bash
cd scripts
python recompute_tables.py
```

### Run Sensitivity Checks

```bash
cd scripts
python sensitivity_checks.py
```

This runs four checks:
1. Leave-out sensitivity excluding rescue families
2. CPC bridging sensitivity (classified-only vs all)
3. Jurisdiction-stratified sensitivity (CN vs non-CN subsets, corresponding to Supplementary Table S2)
4. Shared-anchor inflation check (4-1 ↔ 4-4 Jaccard excluding E04H15-only families)

### Run Full Analysis Pipeline on Your Own Data

```bash
# 1. Edit ISRU_Reproducibility_Pipeline.py — set DATA_FILE to your CSV
# 2. Optionally modify ITC_RULES to refine CPC anchors or keywords
# 3. Run:
python ISRU_Reproducibility_Pipeline.py
```

The pipeline produces:
- Excel workbook (6 sheets): Portfolio, Network, Jaccard, CPC Communities, Leadership, Pairs
- Publication-quality figures (300 DPI PNG)
- Console summary report

**Jaccard mode:** The pipeline's `compute_jaccard()` supports two modes: `'family'` (default, manuscript method: Jaccard over family sets) and `'cpc'` (Jaccard over pooled CPC-code sets). The manuscript reports family-based Jaccard.

## Data Source

| Item | Value |
|------|-------|
| Database | Lens.org Scholarly & Patent Search |
| Search date | 2026-03-28 |
| Initial retrieval | 1,093 patent records |
| Validated core | 511 records / 443 families |
| Phase-two dataset | 453 unique simple patent families |
| Tagged families | 373 (82.3%) |
| Domain-external | 80 (17.7%) |
| Total ITC tags | 795 |
| Deduplication | Lens Simple Family ID, union-find grouping |

## Data Module (`isru_data.py`)

| Object | Description |
|--------|-------------|
| `ITC_RULES` | CPC anchors + keyword stems per domain (reproducibility instrument) |
| `ITC_DOMAINS` | List of 15 domain codes (1-1 through 4-5) |
| `ITC_LABELS` | Human-readable labels |
| `PORTFOLIO` | Tag counts per domain (N = 795) |
| `FILING_YEAR_WBS` | Year × WBS-layer tag-count matrix (publication year, fallback for Figure 3) |
| `FILING_YEAR_BY_PRIORITY` | Year × WBS-layer tag-count matrix (earliest priority year, manuscript default) |
| `JACCARD_MATRIX` | 15×15 Jaccard similarity (phase-two) |
| `CPC_TOP25` | Top 25 CPC codes by frequency |
| `CPC_COOCCURRENCE` | 25×25 co-occurrence matrix |
| `CPC_BRIDGING` / `CPC_CENTRALITY` | Degree and betweenness centrality for top 10 CPC bridging codes (Table 4; computed from full CPC network over all 453 families, aliased for compatibility) |
| `TOP_JACCARD_PAIRS` | Ranked inter-domain Jaccard pairs |

## Domain-External Families

80 of the 453 families (17.7%) have `is_classified: false` and received no ITC domain tag, classified as domain-external. These families are **included** in Figure 3 only to the extent that they carry at least one ITC tag (they do not, by definition). They are included in the JSON for completeness and for any researcher who wishes to reclassify them under a refined taxonomy. They contribute to CPC-level analyses (Fig. 4, Table 5) where the analysis unit is CPC codes, not ITC tags.

## Citation

> Lee, T. S., & Lee, Y.-S. (2026). WBS-based patent landscape of ISRU construction: technology convergence and subsystem-level industrial participation pathways. *Acta Astronautica* (under review).

## License

CC BY 4.0 — provided for academic and research purposes.
