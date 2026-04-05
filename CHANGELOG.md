# Changelog

## v1.5-title-sync

This revision synchronizes the repository metadata with the final manuscript title and authorship.

### Main changes
- Updated `README.md` paper title from the earlier working title to the current manuscript title: "WBS-based patent landscape of ISRU construction: technology convergence and subsystem-level industrial participation pathways".
- Updated `CITATION.cff` with: (a) both authors (Tai Sik Lee, Yoon-Sun Lee), (b) the current manuscript title, (c) the public repository URL.
- Updated the README Citation section to reflect both authors and the current title.
- Added `sensitivity_checks.py` to the Directory Structure listing and Quick Start section in `README.md`.
- Corrected table number references throughout `README.md` to match the current manuscript numbering (Tables 3–6, not 4–8). Affected sections: Verifiable Scope, Scope of This Package, Quick Start, Data Module.

## v1.4-public-release

This public-release revision aligns the repository with the GitHub version cited in the manuscript.

### Main changes
- Updated package metadata from `v1.3-final-sync` to `v1.4-public-release`.
- Added the public repository URL (`https://github.com/Yoonsknowlege/ISRUConc`) to package metadata and synchronized the manuscript/package wording around the public release.
- Replaced review-copy language with public-repository language throughout the package.
- Reframed the classification workflow as a scalable option for large corpora, while clarifying that smaller datasets can be handled through CPC-guided manual review.
- Simplified data-availability language so the package is explicitly centered on the finalized family-level dataset released with the article.

## v1.3-final-sync

This final review-copy sync aligns the package with the integrated-workflow manuscript version.

### Main changes
- Updated package metadata from `v1.2-review` to `v1.3-final-sync`.
- Synchronized manuscript table references so package text and scripts now map quantitative outputs to **Tables 3–6**.
- Updated the Figure 1 description to **Integrated research and dataset-construction workflow**.
- Harmonized the package label set to the manuscript's canonical ITC domain names (`Binder / Geopolymer`, `Composite / Ceramic`, `Powder Bed`, `Solar / Laser Sintering`, `Shielding`, `Life Support / ECLSS`).
- Rebuilt `phase2_453_families.json` `itc_names` from `itc_codes` to remove the single name-array mismatch and ensure code-name consistency throughout the dataset.

## v1.2-review

This review-copy revision synchronizes the supplementary material and package wording with the final revised manuscript.

### Main changes
- Updated review-copy metadata from `v1.1-review` to `v1.2-review`.
- Revised README and `lens_query.txt` language to describe **retrieval-logic documentation** rather than an exact executable Lens query artifact.
- Added the explicit distinction between **12 rescued records before deduplication** and **10 rescue families in the released dataset**.
- Updated supplementary Table S1 headings/captions to the current manuscript title and Appendix B wording.
- Refreshed header strings in package scripts/data modules to match the current manuscript title.
- Preserved the analytical-layer replication scope and review-copy sensitivity notes introduced in `v1.1-review`.

## v1.1-review

This review-copy revision focuses on internal consistency between the manuscript and the released analytical-layer package.

### Main changes
- Updated package metadata to the current manuscript title.
- Replaced stale references to a public repository with review-copy language.
- Corrected the ITC keyword-stem count from 102 to 94.
- Clarified that Figure 3 visualizes annual **ITC tag counts aggregated to WBS layers**, not unique-family counts.
- Corrected `scripts/recompute_tables.py` to use the current ITC domain labels from `data/isru_data.py`.
- Added `scripts/sensitivity_checks.py` and `supplementary/Package_Sensitivity_Notes.md`.
- Added explicit review-copy notes on:
  - rescue leave-out sensitivity (10 rescue families in the released dataset)
  - classified-only CPC bridging sensitivity
  - analytical-layer replication scope versus full raw-to-result reproduction
