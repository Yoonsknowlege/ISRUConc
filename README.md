# ISRU Construction Patent Analysis — Reproduction and Reuse Package

**Paper:** "WBS-based patent landscape of ISRU construction: technology convergence and private-sector entry opportunities"

**Dataset:** 453 unique simple patent families (final analytical dataset derived from validated core)

## Purpose

This repository serves two distinct purposes at two levels of reproducibility:

1. **Figure replication** (`data/` + `scripts/generate_all_figures.py`):
   Regenerates all code-produced manuscript figures (Figs. 2–5, S1) from the released
   final dataset and pre-computed analytical constants. This allows third-party verification
   that the published figures faithfully represent the underlying data.

2. **Reusable analysis pipeline** (`scripts/ISRU_Reproducibility_Pipeline.py`):
   A parameterized template that subsequent researchers can apply to their own patent
   datasets and technology classification schemes. Researchers may modify the WBS structure,
   add CPC anchors or keyword stems, and run the same analytical workflow on new data.
   This is *not* a tool for replicating the present study's exact numbers from raw retrieval;
   it is a generalizable analytical framework.

**What this repository does NOT provide:** A full raw-to-result rerun from the original
1,093-record Lens.org retrieval. The screening, adjudication, and family-consolidation
steps described in the manuscript (§3.1, Appendix A) were performed using LLM-assisted
protocols with human expert oversight; the intermediate working files are not released.
To independently construct a comparable dataset, a researcher would need to execute the
verbatim Lens.org query (`LENS_QUERY` in `isru_data.py`) and apply the ITC codebook
with their own screening methodology.

## Directory Structure

```
ISRUConc/
├── README.md
├── LICENSE                                ← CC BY 4.0
├── requirements.txt                       ← Python dependencies (pinned versions)
├── data/
│   ├── isru_data.py                      ← Core data module (constants, matrices, ITC_RULES, LENS_QUERY)
│   ├── crosswalk_codebook.csv            ← ITC-to-WBS crosswalk with CPC/keyword/source mapping
│   └── phase2_453_families.json          ← Final 453-family tagged dataset
├── scripts/
│   ├── generate_all_figures.py           ← Figure generation (Figs. 2, 3, 4, 5, S1)
│   └── ISRU_Reproducibility_Pipeline.py  ← Reusable parameterized pipeline for new data
└── figures/                              ← Output directory for generated PNGs
```

## Manuscript Figure Mapping

| Manuscript Figure | Content | Source |
|---|---|---|
| Fig. 1 | Overall research framework | Conceptual diagram (not code-generated) |
| Fig. 2 | ITC domain portfolio bar chart | `fig2_portfolio_bar.png` |
| Fig. 3 | Filing-year growth trajectory | `fig3_filing_year.png` |
| Fig. 4 | CPC co-classification heatmap | `fig4_cpc_coclass.png` |
| Fig. 5 | Jaccard similarity matrix | `fig5_jaccard_heatmap.png` |
| Fig. S1 | WBS-layer tag-share distribution | `figS1_wbs_stacked.png` (supplementary) |

## Verifiable Scope

**What can be independently verified from this package:**

- Figures 2–5 and S1 (regenerated from `generate_all_figures.py`)
- Tag-share counts (Table 4) and WBS-layer distributions
- Jaccard similarity matrix (Table 6, Figure 5)
- CPC co-occurrence and centrality values (Tables 4–5)
- Top Jaccard pairs and intersection sizes (Table 7)
- Jurisdiction and temporal distributions (Table 7 post-2020 ratio, CN share)

**What cannot be verified from this package alone:**

- The screening pipeline from 1,093 records to 453 families (requires LLM adjudication infrastructure)
- Table 8 (mission-function vs. method priority) — qualitative author judgment
- Tables 9–10 (entry-window hypothesis map) — discussion-derived, qualitative scoring

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

The ITC codebook was synthesized from publicly available WBS documents (ISECG, NASA, KICT).
As additional national or commercial WBS frameworks become available, researchers can extend
the codebook by adding CPC anchors, keyword stems, or entire domains while preserving the
analytical architecture.

## Method Notes

**Jaccard definition:** The manuscript uses a **patent-family-based** Jaccard index: J(A,B) = |F_A ∩ F_B| / |F_A ∪ F_B|, where F is the set of families tagged to each domain. The reusable pipeline supports both this definition (`method='family'`, default) and an alternative CPC-code-set-based definition (`method='cpc'`).

**Centrality:** Degree centrality in Table 5 is weighted (sum of co-occurrence edge weights / (N−1)). Betweenness centrality uses BFS normalized by (N−1)(N−2)/2.

**Precision audit:** A stratified sample of 60 classified families (15 per WBS layer) was independently reviewed (Appendix A.6). Overall precision was 88.3%; excluding flagged false positives changed no WBS-layer share by more than 1.2 percentage points.

## Data Source

| Item | Value |
|------|-------|
| Database | Lens.org Scholarly & Patent Search |
| Search date | 2026-03-28 |
| Initial retrieval | 1,093 patent records |
| Validated core | 511 records / 443 families |
| Final analytical dataset | 453 unique simple patent families |
| Classified (≥1 ITC tag) | 373 (82.3%) |
| Domain-external | 80 (17.7%) |
| Total ITC tags | 795 |

## JSON Schema (`phase2_453_families.json`)

Each record contains:

| Field | Type | Description |
|-------|------|-------------|
| `lens_id` | string | Hashed Lens.org identifier |
| `title` | string | Patent title |
| `abstract` | string | Patent abstract |
| `cpc` | array[string] | CPC codes assigned to the patent |
| `itc_codes` | array[string] | ITC domain codes (e.g., ["2-1", "2-4"]) |
| `itc_names` | array[string] | ITC domain names |
| `source` | string | "r2_keep" (core) or "rescue" (ITC-rescued) |
| `earliest_priority_year` | int | Earliest priority filing year |
| `jurisdiction` | string | Patent jurisdiction (e.g., CN, US, WO, EP) |
| `applicant_type` | string | Applicant category (corporate, academic, government, individual) |
| `publication_year` | int | Publication year |
| `is_classified` | bool | `true` if ≥1 ITC tag assigned (373 families); `false` if domain-external (80 families) |

Of the 453 families, 373 (`is_classified=true`) matched at least one ITC domain and are used for
tag-share and Jaccard analyses (Figs. 2, 5; Tables 4, 6–7). The remaining 80 (`is_classified=false`)
are domain-external families retained for CPC co-classification and filing-year analyses (Figs. 3–4; Table 5).

## Requirements

```bash
pip install -r requirements.txt
```

Python 3.9+ | Dependencies pinned to exact versions used for figure generation.

## Quick Start

### Reproduce Figures

```bash
cd scripts
python generate_all_figures.py
```

### Apply Pipeline to Your Own Data

```bash
# 1. Edit ISRU_Reproducibility_Pipeline.py — set DATA_FILE to your CSV
# 2. Modify ITC_RULES to add/refine CPC anchors or keywords for your domain
# 3. Run:
python ISRU_Reproducibility_Pipeline.py
```

## Citation

```bibtex
@article{Lee2026ISRUConc,
  author  = {Lee, Y.},
  title   = {WBS-based patent landscape of ISRU construction: technology convergence and private-sector entry opportunities},
  journal = {Acta Astronautica},
  year    = {2026},
  note    = {Under review}
}
```

## License

CC BY 4.0 — https://github.com/Yoonsknowlege/ISRUConc — provided for academic and research purposes.
