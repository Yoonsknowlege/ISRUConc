#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ISRU Construction Patent Analysis — Reproducibility Pipeline              ║
║  Version: 1.0                                                              ║
║  License: CC BY 4.0                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

PURPOSE
-------
This script implements a **reusable, parameterized** patent landscape analysis
pipeline for ISRU (In-Situ Resource Utilization) Construction technologies.

DESIGN CONCEPT
--------------
This script is the REUSABLE PIPELINE component of the repository. It is designed
for portability: subsequent researchers can define their own keyword lists, CPC/IPC
code prefixes, and domain taxonomy, supply their own patent dataset, and follow the
same analytical procedure (tagging → portfolio → network → Jaccard → leadership)
to produce comparable results for related technology domains.

For EXACT REPLICATION of the manuscript's figures and tables, use the companion
script `generate_all_figures.py`, which reads directly from the pre-computed data
in `isru_data.py` and the tagged dataset in `phase2_453_families.json`.

HOW TO USE (FOR SUBSEQUENT RESEARCHERS)
---------------------------------------
Step 1 — Prepare your data
    Export patents from Lens.org (or equivalent) as CSV.
    Required columns: Title, Abstract, CPC Classifications, IPCR Classifications,
    Publication Year, Jurisdiction, Applicants, Cited by Patent Count.
    Delimiter for multiple codes: ';;'

Step 2 — Define your technology classification
    Edit the `ITC_RULES` dictionary below. Each domain needs:
      - 'cpc': list of CPC code prefixes (e.g., ['C04B28', 'C04B12'])
      - 'ipc': list of IPC code prefixes
      - 'keywords': list of keyword stems to match in title+abstract (lowercase)

Step 3 — Configure paths
    Set DATA_FILE, OUTPUT_DIR, and OUTPUT_XLSX to your local paths.

Step 4 — Run
    $ pip install pandas numpy matplotlib seaborn openpyxl
    $ python ISRU_Reproducibility_Pipeline.py

Step 5 — Outputs
    - Excel workbook (6 sheets): Portfolio_Metrics, Network_Centrality,
      Jaccard_Matrix, CPC_Communities, Leadership, Jaccard_Pairs
    - 5 PNG figures (300 DPI)
    - Console summary report

ANALYSIS PIPELINE (5 STAGES)
-----------------------------
  Stage 1: ITC Multi-tagging     → Assign patents to technology domains
  Stage 2: Portfolio Metrics     → GM_i, recent share, maturity classification
  Stage 3: CPC Co-classification → Adjacency matrix, centrality, community detection
  Stage 4: Jaccard Similarity    → Inter-domain technology overlap
  Stage 5: Technology Leadership → Country, institution, actor-type analysis

DEPENDENCIES
------------
  pandas >= 1.5, numpy >= 1.23, matplotlib >= 3.6, seaborn >= 0.12, openpyxl >= 3.0
  (No networkx required — graph algorithms implemented from scratch)

REFERENCE
---------
  [Your citation here, e.g.:]
  Lee, Y. S. (2026). Patent-based technology landscape analysis of ISRU
  construction: An integrated classification and convergence approach.
  Acta Astronautica, xx(x), xxx–xxx.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from itertools import combinations
import os
import sys
import warnings
warnings.filterwarnings('ignore')


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION A: USER CONFIGURATION (EDIT THIS SECTION)                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# --- A1. File Paths ---
DATA_FILE   = './isru-construction-final-union-kuc.csv'   # Input CSV from Lens.org
OUTPUT_DIR  = './outputs/'                                 # Output directory
OUTPUT_XLSX = OUTPUT_DIR + 'Patent_Analysis_Results.xlsx'

# --- A2. Column Name Mapping ---
# Map YOUR CSV column names to the standard names used in this pipeline.
# If your CSV uses different headers, change the RIGHT side of each mapping.
COLUMN_MAP = {
    'title':         'Title',
    'abstract':      'Abstract',
    'cpc':           'CPC Classifications',
    'ipc':           'IPCR Classifications',
    'pub_year':      'Publication Year',
    'jurisdiction':  'Jurisdiction',
    'applicants':    'Applicants',
    'citations':     'Cited by Patent Count',
    'family_size':   'Simple Family Size',
    'legal_status':  'Legal Status',
}

# --- A3. Multi-code Delimiter ---
# Lens.org uses ';;' to separate multiple CPC/IPC codes in a single cell.
# Adjust if your data source uses a different delimiter (e.g., '|', ';', ',').
CODE_DELIMITER = ';;'

# --- A4. Time Windows for Growth Multiplier ---
RECENT_WINDOW = (2021, 2026)   # Numerator period
OLDER_WINDOW  = (2015, 2020)   # Denominator period

# --- A5. Integrated Technology Classification (ITC) Rules ---
# ┌─────────────────────────────────────────────────────────────────────┐
# │  THIS IS THE CORE CONFIGURATION FOR REPRODUCIBILITY.               │
# │                                                                     │
# │  Each domain entry requires:                                        │
# │    'name': Human-readable domain name                               │
# │    'wbs' : WBS group label                                          │
# │    'cpc' : List of CPC code PREFIXES to match                       │
# │    'ipc' : List of IPC code PREFIXES to match                       │
# │    'keywords': List of keyword STEMS (lowercase) to search in       │
# │               title + abstract. Use partial stems for broader       │
# │               matching (e.g., 'sinter' matches 'sintered',         │
# │               'sintering').                                         │
# │                                                                     │
# │  Matching logic (OR-based, evaluated in order):                     │
# │    1. If ANY CPC code starts with any prefix in 'cpc' → tagged     │
# │    2. Else if ANY IPC code starts with any prefix in 'ipc' → tagged│
# │    3. Else if ANY keyword found in title+abstract → tagged          │
# │    4. If no domain matches → 'domain-external'                        │
# │                                                                     │
# │  Multi-tagging: A patent CAN be tagged to multiple domains.        │
# └─────────────────────────────────────────────────────────────────────┘

ITC_RULES = {
    # ── WBS 1: Materials ──────────────────────────────────────────────
    '1-1': {
        'name': 'Regolith Processing / Refining',
        'wbs':  'WBS 1: Materials',
        'cpc':  ['C22B', 'B07B', 'B02C', 'B03'],
        'ipc':  ['C22B', 'B07B', 'B02C'],
        'keywords': [
            'regolith processing', 'beneficiation', 'particle size',
            'mineral separation', 'excavat', 'regolith refin',
            'oxygen extraction'
        ]
    },
    '1-2': {
        'name': 'Binder / Geopolymer',
        'wbs':  'WBS 1: Materials',
        'cpc':  ['C04B28', 'C04B12', 'C04B7'],
        'ipc':  ['C04B28', 'C04B12', 'C04B7'],
        'keywords': [
            'geopolymer', 'binder', 'cement', 'concrete',
            'sulfur concrete', 'calcium carbonate', 'bioite'
        ]
    },
    '1-3': {
        'name': 'Composite / Ceramic / Sintered Bodies',
        'wbs':  'WBS 1: Materials',
        'cpc':  ['C04B35', 'B22F3', 'C04B33'],
        'ipc':  ['C04B35', 'B22F3', 'C04B33'],
        'keywords': [
            'ceramic', 'sintered body', 'vitrif',
            'composite material', 'fiber reinforc'
        ]
    },

    # ── WBS 2: Manufacturing ──────────────────────────────────────────
    '2-1': {
        'name': 'Extrusion-based Additive Manufacturing',
        'wbs':  'WBS 2: Manufacturing',
        'cpc':  ['B33Y10', 'B29C48', 'B28B1', 'B33Y30'],
        'ipc':  ['B29C48', 'B28B1', 'B29C64'],
        'keywords': [
            '3d print', 'additive manufactur', 'extrusion',
            'contour crafting', 'layer-by-layer', 'fused deposition'
        ]
    },
    '2-2': {
        'name': 'Powder Bed Melting / Sintering',
        'wbs':  'WBS 2: Manufacturing',
        'cpc':  ['B22F10', 'B22F12', 'H05B6'],
        'ipc':  ['B22F3', 'B23K26', 'H05B6'],
        'keywords': [
            'selective laser sinter', 'SLS', 'SLM',
            'electron beam melt', 'powder bed',
            'microwave sinter', 'DMLS'
        ]
    },
    '2-3': {
        'name': 'Solar / Laser Sintering',
        'wbs':  'WBS 2: Manufacturing',
        'cpc':  ['B23K26', 'F24S'],
        'ipc':  ['B23K26', 'F24S'],
        'keywords': [
            'solar sinter', 'laser sinter', 'concentrated solar',
            'solar furnace', 'solar energy sinter'
        ]
    },
    '2-4': {
        'name': 'Process Monitoring / NDI',
        'wbs':  'WBS 2: Manufacturing',
        'cpc':  ['G01N', 'G01B', 'B33Y50'],
        'ipc':  ['G01N', 'G01B'],
        'keywords': [
            'non-destructive', 'NDI', 'quality control',
            'in-situ monitor', 'process monitor', 'inspect',
            'ultrasonic test'
        ]
    },

    # ── WBS 3: Robotics ──────────────────────────────────────────────
    '3-1': {
        'name': 'Autonomous Mobile Robots',
        'wbs':  'WBS 3: Robotics',
        'cpc':  ['B25J9', 'B62D', 'G05D1'],
        'ipc':  ['B25J9', 'B62D', 'G05D1'],
        'keywords': [
            'autonomous robot', 'mobile robot', 'lunar rover',
            'mars rover', 'robotic vehicle', 'autonomous vehicle',
            'navigation', 'CADRE'
        ]
    },
    '3-2': {
        'name': 'Tele-operation',
        'wbs':  'WBS 3: Robotics',
        'cpc':  ['G06F3', 'H04L'],
        'ipc':  ['G06F3', 'H04L'],
        'keywords': [
            'tele-operat', 'teleoperat', 'remote operat',
            'remote control', 'telerobot', 'telepresence',
            'time delay compensat'
        ]
    },
    '3-3': {
        'name': 'Autonomous Construction Systems',
        'wbs':  'WBS 3: Robotics',
        'cpc':  ['G05D1/02', 'E04G21'],
        'ipc':  ['G05D1', 'E04G21'],
        'keywords': [
            'autonomous construct', 'swarm construct', 'multi-robot',
            'automated construct', 'robotic construct', 'A4CSEL',
            'automated assembl'
        ]
    },

    # ── WBS 4: Structures & Systems ─────────────────────────────────────────────
    '4-1': {
        'name': 'Habitat Structures',
        'wbs':  'WBS 4: Structures & Systems',
        'cpc':  ['E04H15', 'B64G1/48', 'E04B1', 'E04H1'],
        'ipc':  ['E04H15', 'B64G1', 'E04B1', 'E04H1'],
        'keywords': [
            'habitat', 'shelter', 'living quarter', 'habitation',
            'pressurized module', 'base structure', 'dwelling',
            'residential'
        ]
    },
    '4-2': {
        'name': 'Shielding Structures',
        'wbs':  'WBS 4: Structures & Systems',
        'cpc':  ['G21F1', 'E04B1/92'],
        'ipc':  ['G21F1', 'E04B1/92'],
        'keywords': [
            'shielding', 'radiation protect', 'micrometeorite',
            'regolith shield', 'protection structure', 'cosmic ray'
        ]
    },
    '4-3': {
        'name': 'Landing Pad / Infrastructure',
        'wbs':  'WBS 4: Structures & Systems',
        'cpc':  ['E01C', 'B64G1/62'],
        'ipc':  ['E01C', 'B64G1/62'],
        'keywords': [
            'landing pad', 'launch pad', 'runway', 'road',
            'surface stabiliz', 'plume', 'infrastructure',
            'lunar road'
        ]
    },
    '4-4': {
        'name': 'Deployable Structures',
        'wbs':  'WBS 4: Structures & Systems',
        'cpc':  ['E04H15', 'B64G1/22'],
        'ipc':  ['E04H15', 'B64G1/22'],
        'keywords': [
            'inflatable', 'deployable', 'expandable', 'foldable',
            'membrane structure', 'tensile structure', 'pneumatic'
        ]
    },
    '4-5': {
        'name': 'Life Support / ECLSS',
        'wbs':  'WBS 4: Structures & Systems',
        'cpc':  ['B64G1/46', 'A01G'],
        'ipc':  ['B64G1/46', 'A01G'],
        'keywords': [
            'life support', 'ECLSS', 'oxygen generat',
            'water recycl', 'air revitaliz', 'waste process',
            'environmental control'
        ]
    },
}

# --- A6. Organization Classification ---
GOVERNMENT_ORGS = {
    'NASA', 'JAXA', 'ESA', 'CNSA', 'DLR', 'KARI', 'CAS', 'CNES', 'ISRO',
    'CSA', 'ROSCOSMOS', 'INSA', 'AEM', 'NSSTC'
}

UNIVERSITY_KEYWORDS = {
    'UNIV', 'UNIVERSITY', 'COLLEGE', 'INSTITUTE OF TECHNOLOGY',
    'POLYTECHNIC', 'ACADEMY', 'SCHOOL OF', 'TECHNICAL UNIVERSITY',
    'STATE UNIVERSITY', 'ETH', 'CALTECH'
}

# --- A7. Visualization Settings ---
VIZ_DPI = 300
COLORS_WBS = {
    'WBS 1: Materials':      '#1f77b4',
    'WBS 2: Manufacturing':  '#ff7f0e',
    'WBS 3: Robotics':       '#2ca02c',
    'WBS 4: Structures & Systems':     '#d62728',
}


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION B: ANALYSIS FUNCTIONS (DO NOT EDIT UNLESS EXTENDING)          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def load_and_prepare(filepath, col_map, delimiter):
    """Stage 0: Load CSV and clean columns."""
    print("=" * 80)
    print("ISRU CONSTRUCTION PATENT ANALYSIS — REPRODUCIBILITY PIPELINE")
    print("=" * 80)
    print(f"\n[0/5] Loading data from: {filepath}")

    df = pd.read_csv(filepath)
    print(f"  Loaded {len(df)} patents, {len(df.columns)} columns")

    # Standardize column names (use col_map values as-is since they match CSV headers)
    for std_name, csv_name in col_map.items():
        if csv_name not in df.columns:
            print(f"  WARNING: Column '{csv_name}' not found. Creating empty column.")
            df[csv_name] = ''

    # Clean text fields
    for col in [col_map['title'], col_map['abstract'], col_map['cpc'],
                col_map['ipc'], col_map['applicants']]:
        df[col] = df[col].fillna('')

    df[col_map['pub_year']] = pd.to_numeric(
        df[col_map['pub_year']], errors='coerce'
    ).fillna(0).astype(int)
    df[col_map['jurisdiction']] = df[col_map['jurisdiction']].fillna('UN')

    yr_col = col_map['pub_year']
    print(f"  Year range: {df[yr_col].min()} – {df[yr_col].max()}")
    return df


def tag_patents(df, itc_rules, col_map, delimiter):
    """Stage 1: Assign each patent to one or more ITC domains."""
    print(f"\n[1/5] ITC Multi-tagging ({len(itc_rules)} domains)...")

    title_col = col_map['title']
    abstract_col = col_map['abstract']
    cpc_col = col_map['cpc']
    ipc_col = col_map['ipc']

    def _tag_one(row):
        tags = []
        text_lower = (str(row[title_col]) + ' ' + str(row[abstract_col])).lower()
        cpc_codes = [c.strip() for c in str(row[cpc_col]).split(delimiter) if c.strip()]
        ipc_codes = [c.strip() for c in str(row[ipc_col]).split(delimiter) if c.strip()]

        for domain_id, rules in itc_rules.items():
            matched = False
            # Priority 1: CPC prefix match
            for prefix in rules['cpc']:
                if any(c.startswith(prefix) for c in cpc_codes):
                    matched = True
                    break
            # Priority 2: IPC prefix match
            if not matched:
                for prefix in rules['ipc']:
                    if any(c.startswith(prefix) for c in ipc_codes):
                        matched = True
                        break
            # Priority 3: Keyword match in title + abstract
            if not matched:
                for kw in rules['keywords']:
                    if kw.lower() in text_lower:
                        matched = True
                        break
            if matched:
                tags.append(domain_id)

        return tags if tags else ['domain-external']

    df['ITC_Domains'] = df.apply(_tag_one, axis=1)
    df['Domain_Count'] = df['ITC_Domains'].apply(len)

    # Flatten for downstream analysis
    domain_rows = []
    for idx, domains in enumerate(df['ITC_Domains']):
        for d in domains:
            domain_rows.append({'Patent_ID': idx, 'Domain': d})
    df_domains = pd.DataFrame(domain_rows)

    n_unclass = len(df[df['ITC_Domains'].apply(lambda x: x == ['domain-external'])])
    n_multi   = len(df[df['Domain_Count'] > 1])
    print(f"  Tagged → {df_domains['Domain'].nunique()} categories")
    print(f"  Domain-external: {n_unclass} ({n_unclass/len(df)*100:.1f}%)")
    print(f"  Multi-tagged: {n_multi} ({n_multi/len(df)*100:.1f}%)")

    return df, df_domains


def compute_portfolio(df, itc_rules, col_map, recent_window, older_window):
    """Stage 2: Portfolio metrics — GM_i, maturity classification."""
    print(f"\n[2/5] Portfolio Metrics (windows: {older_window} vs {recent_window})...")

    yr_col = col_map['pub_year']
    jur_col = col_map['jurisdiction']
    rows = []

    for domain_id in sorted(itc_rules.keys()):
        mask = df['ITC_Domains'].apply(lambda x: domain_id in x)
        dp = df[mask]
        n = len(dp)

        n_recent = len(dp[dp[yr_col].between(*recent_window)])
        n_older  = len(dp[dp[yr_col].between(*older_window)])

        recent_share = n_recent / n if n > 0 else 0
        gm_i = n_recent / n_older if n_older > 0 else (2.0 if n_recent > 0 else 0)

        if gm_i > 2.0 and recent_share > 0.5:
            maturity = 'High-growth emerging'
        elif gm_i > 1.0:
            maturity = 'Growth stage'
        else:
            maturity = 'Mature/Stable'

        top_jur = dp[jur_col].value_counts().head(3)
        top_jur_str = '; '.join(f"{k}({v})" for k, v in top_jur.items())

        rows.append({
            'Domain': domain_id,
            'Domain_Name': itc_rules[domain_id]['name'],
            'WBS_Group': itc_rules[domain_id]['wbs'],
            'Patent_Count': n,
            f'{older_window[0]}-{older_window[1]}_Count': n_older,
            f'{recent_window[0]}-{recent_window[1]}_Count': n_recent,
            'Recent_Share': recent_share,
            'Growth_Multiplier_GM_i': gm_i,
            'Maturity_Class': maturity,
            'Top_3_Jurisdictions': top_jur_str,
        })

    df_port = pd.DataFrame(rows)
    print(df_port[['Domain', 'Domain_Name', 'Patent_Count',
                    'Growth_Multiplier_GM_i', 'Maturity_Class']].to_string(index=False))
    return df_port


def compute_cpc_network(df, col_map, delimiter):
    """Stage 3: CPC co-classification network — centrality + community detection."""
    print(f"\n[3/5] CPC Co-classification Network...")

    cpc_col = col_map['cpc']
    patent_cpcs = defaultdict(set)

    for idx, row in df.iterrows():
        codes = [c.strip()[:4] for c in str(row[cpc_col]).split(delimiter) if c.strip()]
        patent_cpcs[idx].update(codes)

    cpc_list = sorted({c for s in patent_cpcs.values() for c in s})
    print(f"  Unique CPC subclasses (4-char): {len(cpc_list)}")

    # Co-occurrence adjacency
    adj = defaultdict(lambda: defaultdict(int))
    for idx, cpcs in patent_cpcs.items():
        cpcs_l = list(cpcs)
        for i in range(len(cpcs_l)):
            for j in range(i + 1, len(cpcs_l)):
                adj[cpcs_l[i]][cpcs_l[j]] += 1
                adj[cpcs_l[j]][cpcs_l[i]] += 1

    # Degree centrality (weighted)
    max_edges = len(cpc_list) - 1
    degree = {c: sum(adj[c].values()) / max_edges if max_edges > 0 else 0
              for c in cpc_list}

    # Betweenness centrality (BFS shortest-path approximation)
    # Implementation note: This uses an unweighted BFS to find shortest
    # paths between all pairs, counting how often each node appears as an
    # intermediary. The result is normalized by (N-1)(N-2)/2 where N is the
    # number of nodes. This is a simplified version of the Brandes (2001)
    # algorithm suitable for small networks (N ≤ 50). For larger networks,
    # consider using networkx.betweenness_centrality() instead.
    between = {c: 0 for c in cpc_list}
    for start in cpc_list:
        visited = {start}
        queue = [(start, [start])]
        while queue:
            node, path = queue.pop(0)
            for nbr in adj.get(node, {}):
                if nbr not in visited:
                    visited.add(nbr)
                    new_path = path + [nbr]
                    queue.append((nbr, new_path))
                    for mid in new_path[1:-1]:
                        between[mid] += 1
    # Normalize by the number of node pairs
    n_nodes = len(cpc_list)
    norm = (n_nodes - 1) * (n_nodes - 2) / 2
    if norm > 0:
        between = {c: v / norm for c, v in between.items()}

    # Greedy modularity community detection
    print("  Running greedy modularity community detection...")

    def _modularity(comms, adj_d, nodes):
        m = sum(sum(adj_d[n].values()) for n in nodes) / 2
        if m == 0:
            return 0
        Q = 0
        for comm in comms:
            a_c = sum(sum(adj_d[n].values()) for n in comm) / (2 * m)
            e_c = sum(adj_d[i].get(j, 0) for i in comm for j in comm if i != j) / (2 * m)
            Q += e_c - a_c ** 2
        return Q

    comms = [[c] for c in cpc_list]
    best_Q = _modularity(comms, adj, cpc_list)

    for _ in range(50):
        if len(comms) <= 5:
            break
        best_merge = None
        best_mQ = best_Q
        for i in range(len(comms)):
            for j in range(i + 1, min(i + 5, len(comms))):
                merged = comms[:i] + [comms[i] + comms[j]] + comms[j+1:]
                mQ = _modularity(merged, adj, cpc_list)
                if mQ > best_mQ:
                    best_mQ = mQ
                    best_merge = merged
        if best_merge:
            comms = best_merge
            best_Q = best_mQ
        else:
            break

    print(f"  Communities detected: {len(comms)} (Q = {best_Q:.4f})")

    comm_data = [{'Community_ID': i + 1, 'CPC_Codes': '; '.join(sorted(c)), 'Size': len(c)}
                 for i, c in enumerate(comms)]

    return cpc_list, adj, degree, between, comm_data, best_Q


def compute_jaccard(df, itc_rules, col_map, delimiter, method='family'):
    """Stage 4: Jaccard similarity between ITC domains.

    Parameters
    ----------
    method : str, default 'family'
        'family' — J(A,B) = |F_A ∩ F_B| / |F_A ∪ F_B|, where F is the
            set of patent-family indices tagged to each domain.
            This is the definition used in the manuscript (§3.3, Figure 5).
        'cpc' — J(A,B) = |C_A ∩ C_B| / |C_A ∪ C_B|, where C is the
            pooled set of CPC codes appearing on patents in each domain.
            This alternative measures shared classification breadth and
            may be useful for exploratory analysis on new datasets.
    """
    print(f"\n[4/5] Jaccard Similarity Analysis (method='{method}')...")

    domains = sorted(itc_rules.keys())
    n = len(domains)

    mat = np.zeros((n, n))

    if method == 'family':
        # Patent-family-based Jaccard (manuscript definition)
        domain_families = {}
        for domain_id in itc_rules:
            mask = df['ITC_Domains'].apply(lambda x: domain_id in x)
            domain_families[domain_id] = set(df[mask].index)

        for i in range(n):
            for j in range(n):
                if i == j:
                    mat[i, j] = 1.0
                else:
                    inter = len(domain_families[domains[i]] & domain_families[domains[j]])
                    union = len(domain_families[domains[i]] | domain_families[domains[j]])
                    mat[i, j] = inter / union if union > 0 else 0

    elif method == 'cpc':
        # CPC-code-set-based Jaccard (alternative definition)
        cpc_col = col_map['cpc']
        domain_cpcs = {}
        for domain_id in itc_rules:
            mask = df['ITC_Domains'].apply(lambda x: domain_id in x)
            dp = df[mask]
            cpcs = set()
            for _, row in dp.iterrows():
                codes = [c.strip() for c in str(row[cpc_col]).split(delimiter) if c.strip()]
                cpcs.update(codes)
            domain_cpcs[domain_id] = cpcs

        for i in range(n):
            for j in range(n):
                if i == j:
                    mat[i, j] = 1.0
                else:
                    inter = len(domain_cpcs[domains[i]] & domain_cpcs[domains[j]])
                    union = len(domain_cpcs[domains[i]] | domain_cpcs[domains[j]])
                    mat[i, j] = inter / union if union > 0 else 0

    else:
        raise ValueError(f"Unknown Jaccard method: '{method}'. Use 'family' or 'cpc'.")

    # Sorted pairs
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append({
                'Domain_1': domains[i], 'Domain_2': domains[j],
                'Jaccard_Similarity': mat[i, j]
            })
    pairs.sort(key=lambda x: x['Jaccard_Similarity'], reverse=True)

    print("  Top 10 similar domain pairs:")
    for k, p in enumerate(pairs[:10], 1):
        print(f"    {k}. {p['Domain_1']} ↔ {p['Domain_2']}: {p['Jaccard_Similarity']:.4f}")

    return domains, mat, pairs


def compute_leadership(df, itc_rules, col_map, delimiter, gov_orgs, univ_kws):
    """Stage 5: Technology leadership — countries, institutions, actor types."""
    print(f"\n[5/5] Technology Leadership Analysis...")

    jur_col = col_map['jurisdiction']
    app_col = col_map['applicants']
    rows = []

    def _classify(name):
        up = str(name).upper()
        if any(g in up for g in gov_orgs):
            return 'Gov'
        if any(u in up for u in univ_kws):
            return 'Univ'
        return 'Corp'

    for domain_id in sorted(itc_rules.keys()):
        mask = df['ITC_Domains'].apply(lambda x: domain_id in x)
        dp = df[mask]

        top_countries = dp[jur_col].value_counts().head(3)
        top_c_str = '; '.join(f"{k}({v})" for k, v in top_countries.items())

        all_apps = []
        for app_str in dp[app_col]:
            if pd.notna(app_str) and str(app_str).strip():
                all_apps.extend(a.strip() for a in str(app_str).split(delimiter) if a.strip())
        app_counts = Counter(all_apps)
        top5 = app_counts.most_common(5)

        actor_counts = Counter()
        for a, cnt in app_counts.items():
            actor_counts[_classify(a)] += cnt

        total = sum(app_counts.values())
        hhi = sum((c / total) ** 2 for c in app_counts.values()) if total > 0 else 0

        rows.append({
            'Domain': domain_id,
            'Domain_Name': itc_rules[domain_id]['name'],
            'Top_3_Countries': top_c_str,
            'Top_5_Applicants': '; '.join(f"{a}({c})" for a, c in top5),
            'Gov_Count': actor_counts.get('Gov', 0),
            'Corp_Count': actor_counts.get('Corp', 0),
            'Univ_Count': actor_counts.get('Univ', 0),
            'HHI_Index': hhi,
            'Total_Unique_Applicants': len(app_counts),
        })

    df_lead = pd.DataFrame(rows)
    return df_lead


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION C: OUTPUT GENERATION                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def save_excel(output_path, df_port, cpc_list, degree, between,
               domains, jaccard_mat, comm_data, df_lead, jaccard_pairs):
    """Save all results to a multi-sheet Excel workbook."""
    print(f"\nSaving Excel → {output_path}")

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Portfolio Metrics
        df_port.to_excel(writer, sheet_name='Portfolio_Metrics', index=False)

        # Sheet 2: Network Centrality
        net_rows = [{'CPC_Code': c, 'Degree_Centrality': degree[c],
                     'Betweenness_Centrality': between[c]} for c in cpc_list]
        pd.DataFrame(net_rows).sort_values(
            'Degree_Centrality', ascending=False
        ).to_excel(writer, sheet_name='Network_Centrality', index=False)

        # Sheet 3: Jaccard Matrix
        pd.DataFrame(jaccard_mat, index=domains, columns=domains).to_excel(
            writer, sheet_name='Jaccard_Matrix')

        # Sheet 4: CPC Communities
        pd.DataFrame(comm_data).to_excel(writer, sheet_name='CPC_Communities', index=False)

        # Sheet 5: Leadership
        df_lead.to_excel(writer, sheet_name='Leadership', index=False)

        # Sheet 6: Jaccard Pairs
        pd.DataFrame(jaccard_pairs).to_excel(writer, sheet_name='Jaccard_Pairs', index=False)


def generate_figures(output_dir, df_port, cpc_list, adj, degree,
                     domains, jaccard_mat, df_lead, colors_wbs, dpi=300):
    """Generate 5 publication-quality PNG figures."""
    print(f"\nGenerating figures (DPI={dpi})...")

    # ── Fig 1: Portfolio Bubble Map ──
    fig, ax = plt.subplots(figsize=(14, 10), dpi=dpi)
    dp = df_port[df_port['Patent_Count'] > 0].copy()
    for wbs in sorted(dp['WBS_Group'].unique()):
        sub = dp[dp['WBS_Group'] == wbs]
        ax.scatter(sub['Recent_Share'], sub['Growth_Multiplier_GM_i'],
                   s=sub['Patent_Count'] * 3, alpha=0.6,
                   label=wbs, color=colors_wbs.get(wbs, 'gray'))
        for _, r in sub.iterrows():
            ax.annotate(r['Domain'], (r['Recent_Share'], r['Growth_Multiplier_GM_i']),
                        fontsize=8, ha='center')
    ax.set_xlabel('Recent 5-Year Share', fontsize=12, fontweight='bold')
    ax.set_ylabel('Growth Multiplier (GM_i)', fontsize=12, fontweight='bold')
    ax.set_title('Patent Portfolio: Growth & Maturity Landscape',
                 fontsize=14, fontweight='bold', pad=20)
    ax.axhline(y=1.0, color='gray', ls='--', alpha=0.5)
    ax.axvline(x=0.5, color='gray', ls='--', alpha=0.5)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'Fig1_Portfolio_BubbleMap.png'),
                dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: Fig1_Portfolio_BubbleMap.png")

    # ── Fig 2: CPC Co-classification Heatmap (Top 25) ──
    fig, ax = plt.subplots(figsize=(14, 12), dpi=dpi)
    top25 = [c for c, _ in sorted(degree.items(), key=lambda x: x[1], reverse=True)[:25]]
    mat25 = np.zeros((25, 25))
    for i, ci in enumerate(top25):
        for j, cj in enumerate(top25):
            mat25[i, j] = adj.get(ci, {}).get(cj, 0)
    sns.heatmap(mat25, xticklabels=top25, yticklabels=top25,
                cmap='YlOrRd', cbar_kws={'label': 'Co-occurrence Count'},
                linewidths=0.5, ax=ax)
    ax.set_title('CPC Co-classification Network (Top 25)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'Fig2_CPC_Network_Heatmap.png'),
                dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: Fig2_CPC_Network_Heatmap.png")

    # ── Fig 3: Jaccard Similarity Heatmap ──
    fig, ax = plt.subplots(figsize=(14, 12), dpi=dpi)
    sns.heatmap(jaccard_mat, xticklabels=domains, yticklabels=domains,
                cmap='coolwarm', vmin=0, vmax=1, annot=True, fmt='.2f',
                cbar_kws={'label': 'Jaccard Similarity'}, linewidths=0.5, ax=ax)
    ax.set_title('ITC Domain Similarity (Jaccard Index)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'Fig3_Jaccard_Heatmap.png'),
                dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: Fig3_Jaccard_Heatmap.png")

    # ── Fig 4: Leadership Bar Chart ──
    fig, ax = plt.subplots(figsize=(16, 10), dpi=dpi)
    labels = df_lead['Domain'].values
    x = np.arange(len(labels))
    w = 0.25
    ax.bar(x - w, df_lead['Gov_Count'], w, label='Government', color='#1f77b4', alpha=0.8)
    ax.bar(x,     df_lead['Corp_Count'], w, label='Corporate',  color='#ff7f0e', alpha=0.8)
    ax.bar(x + w, df_lead['Univ_Count'], w, label='University', color='#2ca02c', alpha=0.8)
    ax.set_xlabel('ITC Domain', fontsize=12, fontweight='bold')
    ax.set_ylabel('Applicant Count', fontsize=12, fontweight='bold')
    ax.set_title('Technology Leadership by Organization Type',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'Fig4_Leadership_BarChart.png'),
                dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: Fig4_Leadership_BarChart.png")

    # ── Fig 5: Actor Type Pie ──
    fig, ax = plt.subplots(figsize=(12, 8), dpi=dpi)
    tg = int(df_lead['Gov_Count'].sum())
    tc = int(df_lead['Corp_Count'].sum())
    tu = int(df_lead['Univ_Count'].sum())
    ax.pie([tg, tc, tu],
           labels=[f'Government\n({tg})', f'Corporate\n({tc})', f'University\n({tu})'],
           colors=['#1f77b4', '#ff7f0e', '#2ca02c'],
           autopct='%1.1f%%', startangle=90, explode=(0.05, 0.05, 0.05),
           textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax.set_title('Actor Type Distribution', fontsize=14, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'Fig5_ActorType_Pie.png'),
                dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: Fig5_ActorType_Pie.png")


def print_summary(df, df_port, cpc_list, comm_data, best_Q,
                  jaccard_pairs, df_lead):
    """Print comprehensive console summary."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SUMMARY REPORT")
    print("=" * 80)

    n_unclass = len(df[df['ITC_Domains'].apply(lambda x: x == ['domain-external'])])
    n_multi   = len(df[df['Domain_Count'] > 1])

    print(f"\n  DATASET: {len(df)} patents")
    print(f"  ITC Multi-tagging: {n_unclass} domain-external, {n_multi} multi-tagged")
    print(f"  CPC Network: {len(cpc_list)} subclasses, "
          f"{len(comm_data)} communities (Q={best_Q:.4f})")
    print(f"  Jaccard: avg={np.mean([p['Jaccard_Similarity'] for p in jaccard_pairs]):.4f}, "
          f"max={jaccard_pairs[0]['Jaccard_Similarity']:.4f}")
    print(f"  Leadership: Gov={int(df_lead['Gov_Count'].sum())}, "
          f"Corp={int(df_lead['Corp_Count'].sum())}, "
          f"Univ={int(df_lead['Univ_Count'].sum())}")

    # Maturity summary
    for cls in ['High-growth emerging', 'Growth stage', 'Mature/Stable']:
        doms = df_port[df_port['Maturity_Class'] == cls]['Domain'].tolist()
        if doms:
            print(f"  {cls}: {', '.join(doms)}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION D: MAIN EXECUTION                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

if __name__ == '__main__':

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Stage 0: Load data
    df = load_and_prepare(DATA_FILE, COLUMN_MAP, CODE_DELIMITER)

    # Stage 1: ITC Multi-tagging
    df, df_domains = tag_patents(df, ITC_RULES, COLUMN_MAP, CODE_DELIMITER)

    # Stage 2: Portfolio Metrics
    df_portfolio = compute_portfolio(
        df, ITC_RULES, COLUMN_MAP, RECENT_WINDOW, OLDER_WINDOW)

    # Stage 3: CPC Co-classification Network
    cpc_list, adj, degree, between, comm_data, best_Q = \
        compute_cpc_network(df, COLUMN_MAP, CODE_DELIMITER)

    # Stage 4: Jaccard Similarity
    domains, jaccard_mat, jaccard_pairs = \
        compute_jaccard(df, ITC_RULES, COLUMN_MAP, CODE_DELIMITER)

    # Stage 5: Technology Leadership
    df_leadership = compute_leadership(
        df, ITC_RULES, COLUMN_MAP, CODE_DELIMITER,
        GOVERNMENT_ORGS, UNIVERSITY_KEYWORDS)

    # Save outputs
    save_excel(OUTPUT_XLSX, df_portfolio, cpc_list, degree, between,
               domains, jaccard_mat, comm_data, df_leadership, jaccard_pairs)

    generate_figures(OUTPUT_DIR, df_portfolio, cpc_list, adj, degree,
                     domains, jaccard_mat, df_leadership, COLORS_WBS, VIZ_DPI)

    # Summary
    print_summary(df, df_portfolio, cpc_list, comm_data, best_Q,
                  jaccard_pairs, df_leadership)
