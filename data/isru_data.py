"""
ISRU Construction Patent Analysis — Core Data Module (Phase-Two v2)
===================================================================
Dataset: 453 unique simple patent families (phase-two synchronized dataset)
Source:   Lens.org
Search date: 2026-03-28
Tagging: CPC-primary hybrid ITC method (see ITC_RULES)

This module provides all constants, matrices, and labels needed to
reproduce the figures and tables in the manuscript.
"""

import numpy as np

# ============================================================
# Lens.org Retrieval Query (verbatim Boolean string)
# ============================================================
# Executed on Lens.org Patent Search on 2026-03-28.
# Returns 1,093 patent records before relevance screening.
# Eight keyword blocks (K1-K8) OR-unioned with five CPC-anchor blocks (C1-C5).

LENS_QUERY = (
    # --- K1: Direct ISRU construction terminology ---
    '(("in-situ resource utilization" OR "in situ resource utilization" OR "ISRU") '
    'AND (habitat OR shelter OR regolith OR sintering OR geopolymer '
    'OR "landing pad" OR "3D printing" OR "additive manufacturing" OR construction)) '
    # --- K2: Regolith processing / beneficiation ---
    'OR ("regolith" AND (processing OR beneficiation OR "particle size" '
    'OR "mineral separation" OR excavat* OR refin* OR "oxygen extraction")) '
    # --- K3: Materials — binder, ceramic, composite ---
    'OR ((geopolymer OR binder OR cement OR "sulfur concrete" OR ceramic '
    'OR "sintered body" OR vitrif* OR "composite material" OR "fiber reinforc*") '
    'AND (lunar OR martian OR space OR extraterrestrial OR regolith)) '
    # --- K4: Additive manufacturing ---
    'OR (("3D print*" OR "additive manufactur*" OR "contour crafting" '
    'OR "layer-by-layer" OR "fused deposition" OR "selective laser sinter*" '
    'OR "powder bed" OR "electron beam melt*" OR "solar sinter*") '
    'AND (lunar OR martian OR space OR regolith OR "in-situ")) '
    # --- K5: Robotics ---
    'OR (("autonomous robot*" OR "mobile robot*" OR "lunar rover" OR "robotic vehicle" '
    'OR "tele-operat*" OR teleoperat* OR "remote operat*" OR "autonomous construct*" '
    'OR "swarm construct*" OR "multi-robot" OR "robotic construct*") '
    'AND (lunar OR martian OR space OR construction)) '
    # --- K6: Structures ---
    'OR ((habitat OR shelter OR "pressurized module" OR shielding '
    'OR "radiation protect*" OR "landing pad" OR "launch pad" '
    'OR inflatable OR deployable OR expandable) '
    'AND (lunar OR martian OR space OR extraterrestrial)) '
    # --- K7: ECLSS ---
    'OR (("life support" OR ECLSS OR "environmental control" OR "air revitalization" '
    'OR "water recycl*") AND (lunar OR space OR habitat)) '
    # --- K8: Additional space construction ---
    'OR (("space construction" OR "extraterrestrial construction" '
    'OR "planetary construction" OR "lunar base" OR "Mars base") '
    'AND (build* OR construct* OR manufactur* OR fabricat*)) '
    # --- C1-C5: CPC-anchor blocks (classification-only capture) ---
    'OR classification:(B33Y OR C04B28 OR C04B12 OR C04B35 '
    'OR E04H15 OR B22F10 OR B22F12 OR E01C OR B64G1/48 '
    'OR G21F1 OR E04G21)'
)

# ============================================================
# ITC Domain Definitions
# ============================================================
ITC_DOMAINS = ['1-1', '1-2', '1-3', '2-1', '2-2', '2-3', '2-4', '3-1', '3-2', '3-3', '4-1', '4-2', '4-3', '4-4', '4-5']

ITC_LABELS = {
    "1-1": "Regolith Processing",
    "1-2": "Binder/Geopolymer",
    "1-3": "Composite/Ceramic",
    "2-1": "Extrusion AM",
    "2-2": "Powder Bed",
    "2-3": "Solar/Thermal Sintering",
    "2-4": "Process Monitoring",
    "3-1": "Autonomous Robots",
    "3-2": "Tele-operation",
    "3-3": "Autonomous Construction",
    "4-1": "Habitat Structures",
    "4-2": "Shielding",
    "4-3": "Landing Pads",
    "4-4": "Deployable Structures",
    "4-5": "Life Support/ECLSS"
}

WBS_COLORS = {
    "1": "#5B9BD5",   # Materials - blue
    "2": "#ED7D31",   # Manufacturing - orange
    "3": "#70AD47",   # Robotics - green
    "4": "#C0504D",   # Structures - red
}

def get_wbs(code):
    return code.split("-")[0]

# ============================================================
# ITC Rules — PRIMARY REPRODUCIBILITY INSTRUMENT
# ============================================================
# Tagging logic (OR-based, evaluated in order):
#   1. If ANY CPC code starts with any prefix in 'cpc' → tagged
#   2. Else if ANY keyword found in title+abstract → tagged
#   3. If no domain matches → 'domain-external'
# Multi-tagging is permitted.

ITC_RULES = {
    '1-1': {
        'name': 'Regolith Processing / Refining',
        'wbs':  'WBS-1 Materials',
        'cpc':  ['C22B', 'B07B', 'B02C', 'B03'],
        'keywords': ['regolith processing', 'beneficiation', 'particle size',
                     'mineral separation', 'excavat', 'regolith refin', 'oxygen extraction']
    },
    '1-2': {
        'name': 'Binder / Geopolymer',
        'wbs':  'WBS-1 Materials',
        'cpc':  ['C04B28', 'C04B12', 'C04B7'],
        'keywords': ['geopolymer', 'binder', 'cement', 'concrete',
                     'sulfur concrete', 'calcium carbonate']
    },
    '1-3': {
        'name': 'Composite / Ceramic / Sintered Bodies',
        'wbs':  'WBS-1 Materials',
        'cpc':  ['C04B35', 'B22F3', 'C04B33'],
        'keywords': ['ceramic', 'sintered body', 'vitrif', 'composite material', 'fiber reinforc']
    },
    '2-1': {
        'name': 'Extrusion-based Additive Manufacturing',
        'wbs':  'WBS-2 Manufacturing',
        'cpc':  ['B33Y10', 'B29C48', 'B28B1', 'B33Y30'],
        'keywords': ['3d print', 'additive manufactur', 'extrusion',
                     'contour crafting', 'layer-by-layer', 'fused deposition']
    },
    '2-2': {
        'name': 'Powder Bed Melting / Sintering',
        'wbs':  'WBS-2 Manufacturing',
        'cpc':  ['B22F10', 'B22F12', 'H05B6'],
        'keywords': ['selective laser sinter', 'SLS', 'SLM',
                     'electron beam melt', 'powder bed', 'microwave sinter']
    },
    '2-3': {
        'name': 'Solar / Laser Sintering',
        'wbs':  'WBS-2 Manufacturing',
        'cpc':  ['B23K26', 'F24S'],
        'keywords': ['solar sinter', 'laser sinter', 'concentrated solar', 'solar furnace']
    },
    '2-4': {
        'name': 'Process Monitoring / NDI',
        'wbs':  'WBS-2 Manufacturing',
        'cpc':  ['G01N', 'G01B', 'B33Y50'],
        'keywords': ['non-destructive', 'NDI', 'quality control',
                     'in-situ monitor', 'process monitor', 'inspect', 'ultrasonic test']
    },
    '3-1': {
        'name': 'Autonomous Mobile Robots',
        'wbs':  'WBS-3 Robotics',
        'cpc':  ['B25J9', 'B62D', 'G05D1'],
        'keywords': ['autonomous robot', 'mobile robot', 'lunar rover',
                     'mars rover', 'robotic vehicle', 'autonomous vehicle', 'navigation']
    },
    '3-2': {
        'name': 'Tele-operation',
        'wbs':  'WBS-3 Robotics',
        'cpc':  ['G06F3', 'H04L'],
        'keywords': ['tele-operat', 'teleoperat', 'remote operat',
                     'remote control', 'telerobot', 'telepresence']
    },
    '3-3': {
        'name': 'Autonomous Construction Systems',
        'wbs':  'WBS-3 Robotics',
        'cpc':  ['G05D1/02', 'E04G21'],
        'keywords': ['autonomous construct', 'swarm construct', 'multi-robot',
                     'automated construct', 'robotic construct', 'automated assembl']
    },
    '4-1': {
        'name': 'Habitat Structures',
        'wbs':  'WBS-4 Structures & Systems',
        'cpc':  ['E04H15', 'B64G1/48', 'E04B1', 'E04H1'],
        'keywords': ['habitat', 'shelter', 'living quarter', 'habitation',
                     'pressurized module', 'base structure', 'dwelling']
    },
    '4-2': {
        'name': 'Shielding Structures',
        'wbs':  'WBS-4 Structures & Systems',
        'cpc':  ['G21F1', 'E04B1/92'],
        'keywords': ['shielding', 'radiation protect', 'micrometeorite',
                     'regolith shield', 'protection structure', 'cosmic ray']
    },
    '4-3': {
        'name': 'Landing Pad / Infrastructure',
        'wbs':  'WBS-4 Structures & Systems',
        'cpc':  ['E01C', 'B64G1/62'],
        'keywords': ['landing pad', 'launch pad', 'runway', 'road',
                     'surface stabiliz', 'plume', 'infrastructure']
    },
    '4-4': {
        'name': 'Deployable Structures',
        'wbs':  'WBS-4 Structures & Systems',
        'cpc':  ['E04H15', 'B64G1/22'],
        'keywords': ['inflatable', 'deployable', 'expandable', 'foldable',
                     'membrane structure', 'tensile structure', 'pneumatic']
    },
    '4-5': {
        'name': 'Life Support / ECLSS',
        'wbs':  'WBS-4 Structures & Systems',
        'cpc':  ['B64G1/46', 'A01G'],
        'keywords': ['life support', 'ECLSS', 'oxygen generat',
                     'water recycl', 'air revitaliz', 'waste process', 'environmental control']
    },
}

# ============================================================
# Phase-Two Portfolio (N = 453 families, 795 ITC tags)
# ============================================================
TOTAL_FAMILIES = 453
TAGGED_FAMILIES = 373
DOMAIN_EXTERNAL = 80
TOTAL_ITC_TAGS = 795

PORTFOLIO = {
    "1-1": 60,
    "1-2": 53,
    "1-3": 110,
    "2-1": 94,
    "2-2": 43,
    "2-3": 29,
    "2-4": 87,
    "3-1": 22,
    "3-2": 3,
    "3-3": 12,
    "4-1": 146,
    "4-2": 27,
    "4-3": 21,
    "4-4": 65,
    "4-5": 23
}

# ============================================================
# Phase-Two Jaccard Similarity Matrix (15 x 15)
# ============================================================
JACCARD_MATRIX = np.array([
    [1.000,0.076,0.056,0.069,0.030,0.060,0.167,0.065,0.000,0.059,0.108,0.012,0.066,0.033,0.037],
    [0.076,1.000,0.148,0.148,0.011,0.012,0.045,0.014,0.000,0.032,0.137,0.067,0.028,0.063,0.013],
    [0.056,0.148,1.000,0.172,0.077,0.168,0.101,0.015,0.000,0.034,0.164,0.046,0.023,0.101,0.015],
    [0.069,0.148,0.172,1.000,0.202,0.070,0.341,0.027,0.000,0.019,0.101,0.008,0.009,0.026,0.017],
    [0.030,0.011,0.077,0.202,1.000,0.043,0.102,0.016,0.000,0.000,0.044,0.000,0.000,0.009,0.015],
    [0.060,0.012,0.168,0.070,0.043,1.000,0.064,0.062,0.000,0.108,0.061,0.000,0.042,0.011,0.106],
    [0.167,0.045,0.101,0.341,0.102,0.064,1.000,0.028,0.000,0.021,0.084,0.000,0.000,0.013,0.000],
    [0.065,0.014,0.015,0.027,0.016,0.062,0.028,1.000,0.042,0.097,0.050,0.065,0.049,0.048,0.098],
    [0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.042,1.000,0.000,0.000,0.000,0.000,0.000,0.000],
    [0.059,0.032,0.034,0.019,0.000,0.108,0.021,0.097,0.000,1.000,0.039,0.026,0.000,0.000,0.129],
    [0.108,0.137,0.164,0.101,0.044,0.061,0.084,0.050,0.000,0.039,1.000,0.161,0.025,0.294,0.083],
    [0.012,0.067,0.046,0.008,0.000,0.000,0.000,0.065,0.000,0.026,0.161,1.000,0.021,0.260,0.163],
    [0.066,0.028,0.023,0.009,0.000,0.042,0.000,0.049,0.000,0.000,0.025,0.021,1.000,0.062,0.023],
    [0.033,0.063,0.101,0.026,0.009,0.011,0.013,0.048,0.000,0.000,0.294,0.260,0.062,1.000,0.114],
    [0.037,0.013,0.015,0.017,0.015,0.106,0.000,0.098,0.000,0.129,0.083,0.163,0.023,0.114,1.000]
])

# Top 10 Jaccard pairs
TOP_JACCARD_PAIRS = [
    [
        "2-1",
        "2-4",
        0.341
    ],
    [
        "4-1",
        "4-4",
        0.294
    ],
    [
        "4-2",
        "4-4",
        0.26
    ],
    [
        "2-1",
        "2-2",
        0.202
    ],
    [
        "1-3",
        "2-1",
        0.172
    ],
    [
        "1-3",
        "2-3",
        0.168
    ],
    [
        "1-1",
        "2-4",
        0.167
    ],
    [
        "1-3",
        "4-1",
        0.164
    ],
    [
        "4-2",
        "4-5",
        0.163
    ],
    [
        "4-1",
        "4-2",
        0.161
    ]
]

# ============================================================
# CPC Co-classification Network (Top 25 codes)
# ============================================================
CPC_TOP25 = [
    "B64G",
    "B33Y",
    "C04B",
    "G01N",
    "E04B",
    "E02D",
    "E04H",
    "B28B",
    "B22F",
    "B29C",
    "Y02P",
    "E04G",
    "C22C",
    "E21B",
    "E21C",
    "Y02A",
    "Y02W",
    "E04C",
    "E01C",
    "Y02E",
    "B25J",
    "H02J",
    "B02C",
    "F24S",
    "B28C"
]

CPC_COOCCURRENCE = np.array([
    [ 94,  5,  4,  4,  3,  2,  7,  1,  4,  2,  2,  2,  1,  5,  9,  6,  0,  0,  0,  3,  1,  1,  0,  3,  0],
    [  5, 75, 13,  1,  2,  3,  2, 23, 15, 27, 19,  6,  8,  0,  0,  0,  2,  0,  0,  1,  0,  0,  0,  3,  0],
    [  4, 13, 75,  2,  1,  2,  0, 15,  2,  2, 10,  1,  0,  0,  1,  0,  9,  0,  2,  0,  0,  0,  1,  1,  6],
    [  4,  1,  2, 53,  0,  1,  1,  1,  0,  0,  3,  0,  0,  2,  2,  2,  0,  0,  0,  0,  1,  1,  0,  0,  0],
    [  3,  2,  1,  0, 52,  2, 22,  0,  0,  0,  1, 13,  0,  0,  1,  4,  0, 13,  0,  2,  0,  4,  0,  0,  0],
    [  2,  3,  2,  1,  2, 47,  2,  0,  0,  0,  0,  3,  0,  7,  0,  2,  2,  1,  2,  3,  0,  0,  0,  0,  1],
    [  7,  2,  0,  1, 22,  2, 40,  0,  0,  0,  0,  9,  0,  1,  1,  4,  0,  9,  0,  0,  0,  5,  0,  0,  0],
    [  1, 23, 15,  1,  0,  0,  0, 40,  0,  0,  5,  0,  0,  0,  0,  0,  2,  0,  0,  1,  0,  0,  0,  1,  4],
    [  4, 15,  2,  0,  0,  0,  0,  0, 34,  2, 10,  0, 21,  1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0],
    [  2, 27,  2,  0,  0,  0,  0,  0,  2, 33,  3,  1,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  2,  0],
    [  2, 19, 10,  3,  1,  0,  0,  5, 10,  3, 32,  2,  6,  0,  0,  1,  2,  1,  1,  0,  1,  0,  0,  0,  3],
    [  2,  6,  1,  0, 13,  3,  9,  0,  0,  1,  2, 28,  0,  0,  0,  0,  0,  5,  0,  1,  0,  0,  0,  1,  1],
    [  1,  8,  0,  0,  0,  0,  0,  0, 21,  0,  6,  0, 21,  1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0],
    [  5,  0,  0,  2,  0,  7,  1,  0,  1,  0,  0,  0,  1, 15,  6,  1,  0,  0,  0,  1,  1,  2,  0,  0,  0],
    [  9,  0,  1,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  6, 14,  0,  0,  0,  1,  0,  0,  2,  0,  1,  0],
    [  6,  0,  0,  2,  4,  2,  4,  0,  0,  0,  1,  0,  0,  1,  0, 14,  0,  0,  1,  1,  1,  2,  0,  0,  0],
    [  0,  2,  9,  0,  0,  2,  0,  2,  0,  2,  2,  0,  0,  0,  0,  0, 14,  0,  1,  0,  0,  0,  2,  0,  2],
    [  0,  0,  0,  0, 13,  1,  9,  0,  0,  0,  1,  5,  0,  0,  0,  0,  0, 14,  0,  0,  0,  1,  0,  0,  0],
    [  0,  0,  2,  0,  0,  2,  0,  0,  0,  0,  1,  0,  0,  0,  1,  1,  1,  0, 13,  0,  0,  0,  0,  0,  1],
    [  3,  1,  0,  0,  2,  3,  0,  1,  1,  0,  0,  1,  1,  1,  0,  1,  0,  0,  0, 12,  0,  2,  0,  3,  0],
    [  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  1,  0,  0,  0,  0, 12,  0,  0,  0,  0],
    [  1,  0,  0,  1,  4,  0,  5,  0,  0,  0,  0,  0,  0,  2,  2,  2,  0,  1,  0,  2,  0, 11,  0,  2,  0],
    [  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0, 11,  0,  1],
    [  3,  3,  1,  0,  0,  0,  0,  1,  1,  2,  0,  1,  0,  0,  1,  0,  0,  0,  0,  3,  0,  2,  0, 10,  0],
    [  0,  0,  6,  0,  0,  1,  0,  4,  0,  0,  3,  1,  0,  0,  0,  0,  2,  0,  1,  0,  0,  0,  1,  0, 10]
])

# ============================================================
# CPC Centrality (Table 5 — weighted degree + BFS betweenness)
# ============================================================
# Degree centrality: weighted by co-occurrence count, normalized
#   by (N-1) where N = number of unique CPC 4-char subclasses.
# Betweenness centrality: BFS shortest-path approximation on the
#   binary co-occurrence graph, normalized by (N-1)(N-2)/2.
CPC_CENTRALITY = [
    {"cpc": "B64G", "degree": 0.422, "betweenness": 0.107},
    {"cpc": "E04H", "degree": 0.301, "betweenness": 0.088},
    {"cpc": "E21C", "degree": 0.289, "betweenness": 0.056},
    {"cpc": "C04B", "degree": 0.265, "betweenness": 0.088},
    {"cpc": "B33Y", "degree": 0.253, "betweenness": 0.129},
    {"cpc": "E04B", "degree": 0.217, "betweenness": 0.075},
    {"cpc": "B22F", "degree": 0.199, "betweenness": 0.050},
    {"cpc": "B29C", "degree": 0.169, "betweenness": 0.052},
    {"cpc": "E02D", "degree": 0.163, "betweenness": 0.063},
    {"cpc": "G01N", "degree": 0.151, "betweenness": 0.031},
]
