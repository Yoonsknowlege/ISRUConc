#!/usr/bin/env python3
"""
ISRU Construction Patent Analysis — Figure Generation Script (Phase-Two)
========================================================================
Generates publication-quality figures for the manuscript.
All data drawn from the phase-two 453-family synchronized dataset.

Figures (matching manuscript numbering):
  Fig. 2 — ITC Portfolio bar (horizontal) by domain
  Fig. 3 — Filing-year distribution by WBS layer (from phase2_453_families.json)
  Fig. 4 — CPC co-classification heatmap (phase-two top 25)
  Fig. 5 — Jaccard similarity heatmap (phase-two 15x15)
  Fig. S1 — ITC domain tag-share by WBS layer (stacked bar, supplementary)

Note: Fig. 1 (overall research framework) is a conceptual diagram created
outside this script.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from isru_data import *

FIGDIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGDIR, exist_ok=True)

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})


def fig2_portfolio_bar():
    """Figure 2: ITC domain portfolio (horizontal bar chart)."""
    fig, ax = plt.subplots(figsize=(10, 7))
    domains = ITC_DOMAINS[::-1]
    vals = [PORTFOLIO[d] for d in domains]
    colors = [WBS_COLORS[get_wbs(d)] for d in domains]
    labels = [f"{d} {ITC_LABELS[d]}" for d in domains]

    bars = ax.barh(range(len(domains)), vals, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(domains)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Number of ITC tags (N = 795)")
    ax.set_title("Phase-Two ITC Domain Portfolio (453 families)")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=9)

    fig.savefig(os.path.join(FIGDIR, 'fig2_portfolio_bar.png'))
    plt.close(fig)
    print("  fig2_portfolio_bar.png")


def fig3_filing_year():
    """Figure 3: Filing-year distribution by WBS layer (N=453 families)."""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'phase2_453_families.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        families = json.load(f)

    wbs_year = {}  # {wbs_label: {year: count}}
    wbs_labels_ordered = ['WBS-1 Materials', 'WBS-2 Manufacturing',
                          'WBS-3 Robotics', 'WBS-4 Structures & Systems']

    for fam in families:
        year = fam.get('earliest_priority_year') or fam.get('publication_year')
        if not year or int(year) < 1990:
            continue
        year = int(year)
        itc_tags = fam.get('itc_domains', [])
        wbs_seen = set()
        for tag in itc_tags:
            layer = tag.split('-')[0]
            wbs_label = {
                '1': 'WBS-1 Materials', '2': 'WBS-2 Manufacturing',
                '3': 'WBS-3 Robotics', '4': 'WBS-4 Structures & Systems'
            }.get(layer)
            if wbs_label and wbs_label not in wbs_seen:
                wbs_seen.add(wbs_label)
                wbs_year.setdefault(wbs_label, {})
                wbs_year[wbs_label][year] = wbs_year[wbs_label].get(year, 0) + 1

    if not wbs_year:
        print("  fig3_filing_year.png — SKIPPED (no year data in JSON)")
        return

    all_years = sorted({y for d in wbs_year.values() for y in d})
    fig, ax1 = plt.subplots(figsize=(12, 6))

    wbs_colors_list = ['#5B9BD5', '#ED7D31', '#70AD47', '#C0504D']
    bottoms = np.zeros(len(all_years))
    total_per_year = np.zeros(len(all_years))

    for wbs_label, color in zip(wbs_labels_ordered, wbs_colors_list):
        counts = np.array([wbs_year.get(wbs_label, {}).get(y, 0) for y in all_years])
        ax1.bar(all_years, counts, bottom=bottoms, color=color,
                label=wbs_label, edgecolor='white', linewidth=0.3, width=0.8)
        bottoms += counts
        total_per_year += counts

    # Cumulative growth line
    ax2 = ax1.twinx()
    cumulative = np.cumsum(total_per_year)
    ax2.plot(all_years, cumulative, color='black', linewidth=1.5,
             marker='o', markersize=3, label='Cumulative')
    ax2.set_ylabel('Cumulative families')

    ax1.set_xlabel('Earliest priority year')
    ax1.set_ylabel('Number of families')
    ax1.set_title('Filing-Year Distribution by WBS Layer (N = 453 families)')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.spines['top'].set_visible(False)
    ax1.grid(axis='y', alpha=0.3)

    fig.savefig(os.path.join(FIGDIR, 'fig3_filing_year.png'))
    plt.close(fig)
    print("  fig3_filing_year.png")


def fig4_cpc_heatmap():
    """Figure 4: CPC co-classification heatmap (top 25)."""
    fig, ax = plt.subplots(figsize=(13, 11))
    mask = np.zeros_like(CPC_COOCCURRENCE, dtype=bool)
    np.fill_diagonal(mask, True)
    sns.heatmap(CPC_COOCCURRENCE, mask=mask,
                xticklabels=CPC_TOP25, yticklabels=CPC_TOP25,
                cmap='YlOrRd', annot=True, fmt='d', annot_kws={'size': 7},
                linewidths=0.5, linecolor='white', ax=ax)
    ax.set_title("CPC Co-classification Network (Phase-Two, Top 25 codes)")
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    fig.savefig(os.path.join(FIGDIR, 'fig4_cpc_coclass.png'))
    plt.close(fig)
    print("  fig4_cpc_coclass.png")


def fig5_jaccard_heatmap():
    """Figure 5: Jaccard similarity heatmap (15x15 ITC domains)."""
    fig, ax = plt.subplots(figsize=(12, 10))
    labels = [f"{d}\n{ITC_LABELS[d]}" for d in ITC_DOMAINS]
    mask = np.eye(15, dtype=bool)
    sns.heatmap(JACCARD_MATRIX, mask=mask,
                xticklabels=ITC_DOMAINS, yticklabels=labels,
                cmap='RdYlBu_r', vmin=0, vmax=0.4,
                annot=True, fmt='.2f', annot_kws={'size': 8},
                linewidths=0.3, linecolor='white', ax=ax,
                cbar_kws={'label': 'Jaccard Similarity Index'})
    ax.set_title("Phase-Two Jaccard Convergence Matrix (N = 453 families)")
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    fig.savefig(os.path.join(FIGDIR, 'fig5_jaccard_heatmap.png'))
    plt.close(fig)
    print("  fig5_jaccard_heatmap.png")


def figS1_wbs_stacked():
    """Figure S1: WBS-layer tag-share stacked bar (supplementary)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    wbs_groups = {
        'WBS-1\nMaterials': ['1-1', '1-2', '1-3'],
        'WBS-2\nManufacturing': ['2-1', '2-2', '2-3', '2-4'],
        'WBS-3\nRobotics': ['3-1', '3-2', '3-3'],
        'WBS-4\nStructures & Systems': ['4-1', '4-2', '4-3', '4-4', '4-5'],
    }
    wbs_colors = ['#5B9BD5', '#ED7D31', '#70AD47', '#C0504D']
    wbs_labels = list(wbs_groups.keys())
    totals = [sum(PORTFOLIO[d] for d in domains) for domains in wbs_groups.values()]
    pcts = [t / TOTAL_ITC_TAGS * 100 for t in totals]

    bars = ax.bar(range(4), pcts, color=wbs_colors, edgecolor='white', linewidth=0.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(wbs_labels, fontsize=11)
    ax.set_ylabel("Share of ITC tags (%)")
    ax.set_title("WBS-Layer Distribution (N = 795 tags)")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, pct, total in zip(bars, pcts, totals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{pct:.1f}%\n({total})", ha='center', fontsize=10)

    fig.savefig(os.path.join(FIGDIR, 'figS1_wbs_stacked.png'))
    plt.close(fig)
    print("  figS1_wbs_stacked.png")


if __name__ == '__main__':
    print("Generating figures...")
    fig2_portfolio_bar()
    fig3_filing_year()
    fig4_cpc_heatmap()
    fig5_jaccard_heatmap()
    figS1_wbs_stacked()
    print("Done. All figures saved to:", FIGDIR)
