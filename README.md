# ISRU Construction Patent Analysis — Reproducibility Package (v2)

**Paper:** Lee, Y. S. (2026). "WBS-based patent landscape of ISRU construction: technology convergence and private-sector entry opportunities." *Acta Astronautica*, xx(x), xxx--xxx.

**Dataset:** 453 unique simple patent families (phase-two synchronized dataset)

## Directory Structure

```
ISRUConc/
├── README.md
├── LICENSE                                ← CC BY 4.0
├── requirements.txt                       ← Python dependencies
├── data/
│   ├── isru_data.py                       ← Core data module (constants, matrices, ITC_RULES, LENS_QUERY)
│   ├── crosswalk_codebook.csv             ← ITC-to-WBS crosswalk with CPC/keyword/source mapping
│   ├── phase2_453_families.json           ← 453-family tagged dataset (Lens IDs, CPC, ITC tags)
│   └── adjudication_log.csv               ← Screening & consolidation audit trail (R1–R6)
├── scripts/
│   ├── generate_all_figures.py            ← Figure generation (Figs. 2, 3, 4, 5, S1)
│   └── ISRU_Reproducibility_Pipeline.py   ← Full parameterized analysis pipeline
└── figures/                               ← Pre-generated publication-quality PNGs
```

## Quick Start

### Requirements

```bash
pip install -r requirements.txt
```

Python 3.9+

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

## Manuscript Figure Mapping

| Manuscript Figure | Content | Source |
|---|---|---|
| Fig. 1 | Overall research framework | Conceptual diagram (not code-generated) |
| Fig. 2 | ITC domain portfolio bar chart | `fig2_portfolio_bar.png` |
| Fig. 3 | Filing-year distribution by WBS layer | `fig3_filing_year.png` |
| Fig. 4 | CPC co-classification heatmap | `fig4_cpc_coclass.png` |
| Fig. 5 | Jaccard similarity matrix | `fig5_jaccard_heatmap.png` |
| Fig. S1 | WBS-layer tag-share distribution | `figS1_wbs_stacked.png` (supplementary) |

## Reproducibility Protocol (Appendix A Summary)

The full procedural details are documented in the manuscript appendix. Key stages:

### A.1. Lens.org Retrieval Query

The initial corpus of 1,093 patent records was retrieved from Lens.org using a multi-block Boolean query combining eight keyword blocks (K1--K8) with five CPC-anchor blocks (C1--C5) via OR logic. The verbatim query string is provided in `data/isru_data.py` (`LENS_QUERY`).

### A.2. Relevance Scoring

Each record was scored through an LLM-assisted expert screening protocol:
- **Models:** GPT-4 (`gpt-4-0613`) and Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`), temperature = 0
- **Rubric (0--5):** 5 = directly addresses ISRU construction; 0 = not relevant
- **Inter-model agreement:** Cohen's kappa = 0.74 (substantial agreement)
- **Threshold:** Mean R2 >= 2.5 retained; disagreements > 2 points underwent mandatory human review
- **Result:** 511 validated records (corpus mean R2 = 3.59, median 3.50)

### A.3. ITC Domain Tagging

Deterministic, OR-based CPC Hybrid v2 protocol assigning each family to one or more of 15 ITC domains across four WBS layers. The complete `ITC_RULES` dictionary and `crosswalk_codebook.csv` are provided in the `data/` directory.

### A.4. ITC-Rescue Rule

12 records rescued from the 582 excluded candidates where 1.5 <= R2 < 2.5 **and** at least one CPC/IPC code matched an ITC domain anchor prefix, producing 523 pre-deduplication records.

### A.5. Family Consolidation

Union-find grouping by Lens Simple Family ID: 523 records consolidated to 453 unique families (416 singletons, 37 multi-member groups).

## Core Reproducibility Instrument

The **ITC codebook** (`ITC_RULES` in `isru_data.py`) maps 15 technology domains across four WBS layers to:

- **41 CPC anchor prefixes** (e.g., 1-1: C22B, B07B, B02C, B03)
- **102 keyword stems** (e.g., 2-1: "3d print", "additive manufactur", "extrusion" ...)

**WBS Layer Structure:**
| Layer | Scope | Domains |
|-------|-------|---------|
| WBS-1 | Materials | 1-1 through 1-3 |
| WBS-2 | Manufacturing | 2-1 through 2-4 |
| WBS-3 | Robotics | 3-1 through 3-3 |
| WBS-4 | Structures & Systems | 4-1 through 4-5 |

**Tagging logic** (OR-based):
1. If any CPC code on a patent starts with an anchor prefix -> domain tag assigned
2. Else if any keyword stem matches in title+abstract -> domain tag assigned
3. Multi-tagging permitted (mean 1.76 tags per family)
4. If no domain matches -> classified as domain-external (80 families, 17.7%)

## Data Module (`isru_data.py`)

| Object | Description |
|--------|-------------|
| `LENS_QUERY` | Verbatim Boolean query string used on Lens.org (2026-03-28) |
| `ITC_RULES` | CPC anchors + keyword stems per domain (reproducibility instrument) |
| `ITC_DOMAINS` | List of 15 domain codes (1-1 through 4-5) |
| `ITC_LABELS` | Human-readable labels |
| `PORTFOLIO` | Tag counts per domain (N = 795) |
| `JACCARD_MATRIX` | 15x15 Jaccard similarity (phase-two) |
| `CPC_TOP25` | Top 25 CPC codes by frequency |
| `CPC_COOCCURRENCE` | 25x25 co-occurrence matrix |
| `CPC_CENTRALITY` | Weighted degree + BFS betweenness for top CPC codes (Table 5) |
| `TOP_JACCARD_PAIRS` | Ranked inter-domain Jaccard pairs |

## Data Source

| Item | Value |
|------|-------|
| Database | Lens.org Scholarly & Patent Search |
| Search date | 2026-03-28 |
| Initial retrieval | 1,093 patent records |
| Validated core | 511 records / 443 families |
| ITC-rescued | +12 records (CPC-anchored false negatives) |
| Phase-two dataset | 453 unique simple patent families |
| Tagged families | 373 (82.3%) |
| Domain-external | 80 (17.7%) |
| Total ITC tags | 795 |
| Deduplication | Lens Simple Family ID, union-find grouping |

## v2 Changelog (2026-04-02)

- **CPC_CENTRALITY** replaces `CPC_BRIDGING`: now includes both weighted degree centrality and BFS betweenness centrality, matching manuscript Table 5. Betweenness normalization by (N-1)(N-2)/2 is documented in code.
- **Dual Jaccard method** in `ISRU_Reproducibility_Pipeline.py`: `method='family'` (default, matching manuscript) and `method='cpc'` (CPC-set overlap).
- **ITC 4-5 CPC anchors** unified to `B64G1/46; A01G` across `isru_data.py`, `crosswalk_codebook.csv`, and manuscript Table 2.
- **Figure 3** generation added: filing-year distribution by WBS layer with cumulative growth line.
- **`adjudication_log.csv`** created: machine-readable audit trail of the R1--R6 screening and consolidation pipeline.
- **`requirements.txt`** added.

## Scope and Limitations

This package provides the verbatim Lens.org Boolean query string, the ITC-to-WBS crosswalk codebook, aggregated matrices, the adjudication audit trail, and plotting scripts sufficient to reproduce the code-generated figures and verify the analytical constants reported in the manuscript. The per-record LLM adjudication scores are documented in the manuscript Appendix but are not included as machine-readable files in this release.

## Citation

```bibtex
@article{Lee2026ISRUConc,
  author  = {Lee, Yoon Seok},
  title   = {WBS-based patent landscape of ISRU construction: technology convergence and private-sector entry opportunities},
  journal = {Acta Astronautica},
  year    = {2026}
}
```

## License

[CC BY 4.0](LICENSE) -- provided for academic and research purposes.
