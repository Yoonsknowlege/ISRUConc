#!/usr/bin/env python3
"""
ISRU Construction Patent Analysis — Figure Generation Script (Phase-Two)
========================================================================
Generates publication-quality figures for the manuscript.
All data drawn from the phase-two 453-family synchronized dataset.

Figures (matching manuscript numbering):
  Fig. 2 — ITC Portfolio bar (horizontal) by domain
  Fig. 3 — Filing-year WBS-layer tag counts (stacked bar + cumulative line)
  Fig. 4 — CPC co-classification heatmap (phase-two top 25)
  Fig. 5 — Jaccard similarity heatmap (phase-two 15x15)
  Fig. S1 — ITC domain tag-share by WBS layer (stacked bar, supplementary)

Note: Fig. 1 (overall research framework) is a conceptual diagram created
outside this script.
"""
import sys, os
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
    """Figure 3: Filing-year WBS-layer tag counts (stacked bar + cumulative).

    Each family contributes one tag per matched WBS layer per year.
    A family tagged in multiple WBS layers is counted once per layer,
    so annual column sums may exceed the number of unique families.
    The cumulative line tracks total tag counts, not unique families.
    """
    data = np.array(FILING_YEAR_WBS)
    years = data[:, 0].astype(int)
    wbs1, wbs2, wbs3, wbs4 = data[:, 1], data[:, 2], data[:, 3], data[:, 4]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(years))
    width = 0.7

    ax1.bar(x, wbs1, width, label='WBS-1 Materials', color='#5B9BD5')
    ax1.bar(x, wbs2, width, bottom=wbs1, label='WBS-2 Manufacturing', color='#ED7D31')
    ax1.bar(x, wbs3, width, bottom=wbs1+wbs2, label='WBS-3 Robotics', color='#70AD47')
    ax1.bar(x, wbs4, width, bottom=wbs1+wbs2+wbs3, label='WBS-4 Structures & Systems', color='#C0504D')

    ax1.set_xticks(x)
    ax1.set_xticklabels(years, rotation=45, ha='right', fontsize=9)
    ax1.set_xlabel("Publication Year")
    ax1.set_ylabel("Annual WBS-layer tag count")
    ax1.set_title("Filing-Year WBS-Layer Tag Distribution (453 families)")
    ax1.spines['top'].set_visible(False)

    # Cumulative line on secondary axis
    cumulative = np.cumsum(wbs1 + wbs2 + wbs3 + wbs4)
    ax2 = ax1.twinx()
    ax2.plot(x, cumulative, 'k-o', markersize=4, linewidth=1.5, label='Cumulative tags')
    ax2.set_ylabel("Cumulative tag count")
    ax2.spines['top'].set_visible(False)

    # Combined legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=9, framealpha=0.9)

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
