# ISRU Construction Patent Analysis — Documentation and Figure-Reproduction Package

**Paper:** "Exploring Work Breakdown Structures of in-situ resource utilization construction: technology convergence, cross-domain coupling, and private-sector entry opportunities based on the patent landscape"

**Dataset:** 453 unique simple patent families (phase-two synchronized dataset)

**Release:** `v1.0-submission` — snapshot accompanying the Acta Astronautica submission (2026-04-03)

## Directory Structure

```
reproduction_package/
├── README.md
├── DATA_DICTIONARY.md                  ← Field-level schema for phase2_453_families.json
├── data/
│   ├── isru_data.py                    ← Core data module (constants, matrices, ITC_RULES)
│   └── phase2_453_families.json        ← 453-family tagged dataset (Lens IDs, CPC, ITC tags, pub year)
├── scripts/
│   ├── generate_all_figures.py         ← Figure generation (Figs. 2–5, S1)
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

**Tagging logic** (OR-based):
1. If any CPC code on a patent starts with an anchor prefix → domain tag assigned
2. Else if any keyword stem matches in title+abstract → domain tag assigned
3. Multi-tagging permitted (a patent can belong to multiple domains)
4. If no domain matches → classified as domain-external

Any researcher who applies these rules to a comparable Lens.org retrieval should obtain a comparable domain distribution.

## Verifiable Scope

With the data and scripts provided in this package, an independent researcher can verify:

| What | How |
|------|-----|
| **ITC tag-share distribution** (Fig. 2, Table 5) | Run `generate_all_figures.py` or recount `itc_codes` in `phase2_453_families.json` |
| **Filing-year × WBS trajectory** (Fig. 3) | Cross-reference `publication_year` × `itc_codes` in the JSON, or run `generate_all_figures.py` |
| **Jaccard similarity pairs** (Fig. 5, Table 6) | Recompute from the `itc_codes` field in the JSON |
| **CPC co-classification network** (Fig. 4) | Parse the `cpc` field and rebuild the co-occurrence matrix |
| **CPC bridging centrality** (Table 8) | Derive degree centrality from the co-occurrence matrix |

**Not independently verifiable from this package alone:** Table 7 descriptive profiles (require CPC subclass look-up beyond the released fields), post-2020 ratio and CN-share statistics (require jurisdiction and earliest-priority-date fields not included in this release). These are documented in the manuscript but depend on the original Lens.org export.

**Data-quality note:** The released dataset may still contain residual edge-case false positives; manuscript Appendix A.6 describes the precision audit protocol and sensitivity analysis.

## Scope and Limitations of This Package

This package provides codebooks, aggregated matrices, and plotting scripts sufficient to reproduce the code-generated figures and verify the analytical constants reported in the manuscript. It constitutes a **figure replication package** and a **reusable parameterized pipeline template**, but does not yet constitute a full raw-to-result reproduction package: the verbatim Boolean query string, family-consolidation log, and per-record LLM adjudication scores are documented in the manuscript Appendix but are not included as machine-readable files in this release. The WBS-based ITC codebook and its CPC/keyword mapping constitute the core reproducibility instrument.

## Requirements

```bash
pip install matplotlib seaborn numpy pandas openpyxl
```

Python 3.9+

## Quick Start

### Reproduce Figures

```bash
cd scripts
python generate_all_figures.py
```

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
| `FILING_YEAR_WBS` | Year × WBS-layer tag-count matrix (for Figure 3) |
| `JACCARD_MATRIX` | 15×15 Jaccard similarity (phase-two) |
| `CPC_TOP25` | Top 25 CPC codes by frequency |
| `CPC_COOCCURRENCE` | 25×25 co-occurrence matrix |
| `CPC_BRIDGING` | Degree centrality for top CPC codes |
| `TOP_JACCARD_PAIRS` | Ranked inter-domain Jaccard pairs |

## Domain-External Families

80 of the 453 families (17.7%) received no ITC domain tag and are classified as domain-external. These families are **included** in Figure 3 only to the extent that they carry at least one ITC tag (they do not, by definition). They are included in the JSON for completeness and for any researcher who wishes to reclassify them under a refined taxonomy. They contribute to CPC-level analyses (Fig. 4, Table 8) where the analysis unit is CPC codes, not ITC tags.

## Citation

> Lee, Y. S. (2026). Exploring Work Breakdown Structures of in-situ resource utilization construction: technology convergence, cross-domain coupling, and private-sector entry opportunities based on the patent landscape. *Acta Astronautica* (under review).

## License

CC BY 4.0 — provided for academic and research purposes.
