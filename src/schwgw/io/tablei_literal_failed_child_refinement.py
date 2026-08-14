from __future__ import annotations

import hashlib
from io import BytesIO
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.scattering.partial_wave import (
    compute_flat_no_lens_polarization,
    compute_polarization,
)


LITERAL_FAILED_CHILD_FREQUENCIES = (
    0.3125, 0.3375, 0.3625, 0.3875,
    0.8625, 0.9125, 0.9375, 0.9625, 0.9875,
    1.5125, 1.5375, 1.5625, 1.5875, 1.6125, 1.6375, 1.6625,
    1.6875, 1.70625, 1.71875,
    2.78125, 2.79375, 2.8125, 2.8375, 2.8625, 2.8875, 2.9125,
    2.9375, 2.9625, 2.9875,
    3.75625, 3.76875, 3.78125, 3.79375, 3.8125, 3.8375, 3.8625,
    3.8875, 3.9125, 3.9375, 3.9625, 3.9875,
)
FREQUENCY_TOKENS = {
    0.3125: "0p3125", 0.3375: "0p3375", 0.3625: "0p3625", 0.3875: "0p3875",
    0.8625: "0p8625", 0.9125: "0p9125", 0.9375: "0p9375", 0.9625: "0p9625", 0.9875: "0p9875",
    1.5125: "1p5125", 1.5375: "1p5375", 1.5625: "1p5625", 1.5875: "1p5875",
    1.6125: "1p6125", 1.6375: "1p6375", 1.6625: "1p6625", 1.6875: "1p6875",
    1.70625: "1p70625", 1.71875: "1p71875",
    2.78125: "2p78125", 2.79375: "2p79375", 2.8125: "2p8125", 2.8375: "2p8375",
    2.8625: "2p8625", 2.8875: "2p8875", 2.9125: "2p9125", 2.9375: "2p9375",
    2.9625: "2p9625", 2.9875: "2p9875",
    3.75625: "3p75625", 3.76875: "3p76875", 3.78125: "3p78125", 3.79375: "3p79375",
    3.8125: "3p8125", 3.8375: "3p8375", 3.8625: "3p8625", 3.8875: "3p8875",
    3.9125: "3p9125", 3.9375: "3p9375", 3.9625: "3p9625", 3.9875: "3p9875",
}
LITERAL_FAILED_CHILD_LMAX_VALUES: dict[float, tuple[int, ...]] = {
    0.3125: (24, 36, 60, 84), 0.3375: (24, 36, 60, 84),
    0.3625: (24, 36, 60, 84), 0.3875: (24, 36, 60, 84),
    0.8625: (24, 36, 60, 84), 0.9125: (24, 36, 60, 84),
    0.9375: (24, 48, 72, 96), 0.9625: (24, 48, 72, 96), 0.9875: (24, 48, 72, 96),
    1.5125: (72, 96, 120, 144), 1.5375: (72, 96, 120, 144),
    1.5625: (72, 96, 120, 144), 1.5875: (72, 96, 120, 144),
    1.6125: (84, 108, 132, 156), 1.6375: (84, 108, 132, 156),
    1.6625: (84, 108, 132, 156), 1.6875: (84, 108, 132, 156),
    1.70625: (84, 108, 132, 156), 1.71875: (84, 108, 132, 156),
    2.78125: (180, 204, 228, 252), 2.79375: (180, 204, 228, 252),
    2.8125: (192, 216, 240, 264), 2.8375: (192, 216, 240, 264),
    2.8625: (192, 216, 240, 264), 2.8875: (192, 216, 240, 264),
    2.9125: (192, 216, 240, 264), 2.9375: (204, 228, 252, 276),
    2.9625: (204, 228, 252, 276), 2.9875: (204, 228, 252, 276),
    3.75625: (276, 300, 324, 348), 3.76875: (276, 300, 324, 348),
    3.78125: (276, 300, 324, 348), 3.79375: (276, 300, 324, 348),
    3.8125: (276, 300, 324, 348), 3.8375: (276, 300, 324, 348),
    3.8625: (276, 300, 324, 348), 3.8875: (288, 312, 336, 360),
    3.9125: (288, 312, 336, 360), 3.9375: (288, 312, 336, 360),
    3.9625: (288, 312, 336, 360), 3.9875: (288, 312, 336, 360),
}
_FROZEN_FREQUENCIES = LITERAL_FAILED_CHILD_FREQUENCIES
_FROZEN_LMAX_VALUES = dict(LITERAL_FAILED_CHILD_LMAX_VALUES)
PARENT_REFINEMENTS = (
    {"midpoint": 0.3125, "parent": [0.3, 0.325], "children": [[0.3, 0.3125], [0.3125, 0.325]], "parent_width": 0.025},
    {"midpoint": 0.3375, "parent": [0.325, 0.35], "children": [[0.325, 0.3375], [0.3375, 0.35]], "parent_width": 0.025},
    {"midpoint": 0.3625, "parent": [0.35, 0.375], "children": [[0.35, 0.3625], [0.3625, 0.375]], "parent_width": 0.025},
    {"midpoint": 0.3875, "parent": [0.375, 0.4], "children": [[0.375, 0.3875], [0.3875, 0.4]], "parent_width": 0.025},
    {"midpoint": 0.8625, "parent": [0.85, 0.875], "children": [[0.85, 0.8625], [0.8625, 0.875]], "parent_width": 0.025},
    {"midpoint": 0.9125, "parent": [0.9, 0.925], "children": [[0.9, 0.9125], [0.9125, 0.925]], "parent_width": 0.025},
    {"midpoint": 0.9375, "parent": [0.925, 0.95], "children": [[0.925, 0.9375], [0.9375, 0.95]], "parent_width": 0.025},
    {"midpoint": 0.9625, "parent": [0.95, 0.975], "children": [[0.95, 0.9625], [0.9625, 0.975]], "parent_width": 0.025},
    {"midpoint": 0.9875, "parent": [0.975, 1.0], "children": [[0.975, 0.9875], [0.9875, 1.0]], "parent_width": 0.025},
    {"midpoint": 1.5125, "parent": [1.5, 1.525], "children": [[1.5, 1.5125], [1.5125, 1.525]], "parent_width": 0.025},
    {"midpoint": 1.5375, "parent": [1.525, 1.55], "children": [[1.525, 1.5375], [1.5375, 1.55]], "parent_width": 0.025},
    {"midpoint": 1.5625, "parent": [1.55, 1.575], "children": [[1.55, 1.5625], [1.5625, 1.575]], "parent_width": 0.025},
    {"midpoint": 1.5875, "parent": [1.575, 1.6], "children": [[1.575, 1.5875], [1.5875, 1.6]], "parent_width": 0.025},
    {"midpoint": 1.6125, "parent": [1.6, 1.625], "children": [[1.6, 1.6125], [1.6125, 1.625]], "parent_width": 0.025},
    {"midpoint": 1.6375, "parent": [1.625, 1.65], "children": [[1.625, 1.6375], [1.6375, 1.65]], "parent_width": 0.025},
    {"midpoint": 1.6625, "parent": [1.65, 1.675], "children": [[1.65, 1.6625], [1.6625, 1.675]], "parent_width": 0.025},
    {"midpoint": 1.6875, "parent": [1.675, 1.7], "children": [[1.675, 1.6875], [1.6875, 1.7]], "parent_width": 0.025},
    {"midpoint": 1.70625, "parent": [1.7, 1.7125], "children": [[1.7, 1.70625], [1.70625, 1.7125]], "parent_width": 0.0125},
    {"midpoint": 1.71875, "parent": [1.7125, 1.725], "children": [[1.7125, 1.71875], [1.71875, 1.725]], "parent_width": 0.0125},
    {"midpoint": 2.78125, "parent": [2.775, 2.7875], "children": [[2.775, 2.78125], [2.78125, 2.7875]], "parent_width": 0.0125},
    {"midpoint": 2.79375, "parent": [2.7875, 2.8], "children": [[2.7875, 2.79375], [2.79375, 2.8]], "parent_width": 0.0125},
    {"midpoint": 2.8125, "parent": [2.8, 2.825], "children": [[2.8, 2.8125], [2.8125, 2.825]], "parent_width": 0.025},
    {"midpoint": 2.8375, "parent": [2.825, 2.85], "children": [[2.825, 2.8375], [2.8375, 2.85]], "parent_width": 0.025},
    {"midpoint": 2.8625, "parent": [2.85, 2.875], "children": [[2.85, 2.8625], [2.8625, 2.875]], "parent_width": 0.025},
    {"midpoint": 2.8875, "parent": [2.875, 2.9], "children": [[2.875, 2.8875], [2.8875, 2.9]], "parent_width": 0.025},
    {"midpoint": 2.9125, "parent": [2.9, 2.925], "children": [[2.9, 2.9125], [2.9125, 2.925]], "parent_width": 0.025},
    {"midpoint": 2.9375, "parent": [2.925, 2.95], "children": [[2.925, 2.9375], [2.9375, 2.95]], "parent_width": 0.025},
    {"midpoint": 2.9625, "parent": [2.95, 2.975], "children": [[2.95, 2.9625], [2.9625, 2.975]], "parent_width": 0.025},
    {"midpoint": 2.9875, "parent": [2.975, 3.0], "children": [[2.975, 2.9875], [2.9875, 3.0]], "parent_width": 0.025},
    {"midpoint": 3.75625, "parent": [3.75, 3.7625], "children": [[3.75, 3.75625], [3.75625, 3.7625]], "parent_width": 0.0125},
    {"midpoint": 3.76875, "parent": [3.7625, 3.775], "children": [[3.7625, 3.76875], [3.76875, 3.775]], "parent_width": 0.0125},
    {"midpoint": 3.78125, "parent": [3.775, 3.7875], "children": [[3.775, 3.78125], [3.78125, 3.7875]], "parent_width": 0.0125},
    {"midpoint": 3.79375, "parent": [3.7875, 3.8], "children": [[3.7875, 3.79375], [3.79375, 3.8]], "parent_width": 0.0125},
    {"midpoint": 3.8125, "parent": [3.8, 3.825], "children": [[3.8, 3.8125], [3.8125, 3.825]], "parent_width": 0.025},
    {"midpoint": 3.8375, "parent": [3.825, 3.85], "children": [[3.825, 3.8375], [3.8375, 3.85]], "parent_width": 0.025},
    {"midpoint": 3.8625, "parent": [3.85, 3.875], "children": [[3.85, 3.8625], [3.8625, 3.875]], "parent_width": 0.025},
    {"midpoint": 3.8875, "parent": [3.875, 3.9], "children": [[3.875, 3.8875], [3.8875, 3.9]], "parent_width": 0.025},
    {"midpoint": 3.9125, "parent": [3.9, 3.925], "children": [[3.9, 3.9125], [3.9125, 3.925]], "parent_width": 0.025},
    {"midpoint": 3.9375, "parent": [3.925, 3.95], "children": [[3.925, 3.9375], [3.9375, 3.95]], "parent_width": 0.025},
    {"midpoint": 3.9625, "parent": [3.95, 3.975], "children": [[3.95, 3.9625], [3.9625, 3.975]], "parent_width": 0.025},
    {"midpoint": 3.9875, "parent": [3.975, 4.0], "children": [[3.975, 3.9875], [3.9875, 4.0]], "parent_width": 0.025},
)
SEQUENCES = (
    (0.3, 0.3125, 0.325, 0.3375, 0.35, 0.3625, 0.375, 0.3875, 0.4, 0.45, 0.5),
    (0.75, 0.8, 0.825, 0.85, 0.8625, 0.875, 0.9, 0.9125, 0.925, 0.9375, 0.95, 0.9625, 0.975, 0.9875, 1.0),
    (1.5, 1.5125, 1.525, 1.5375, 1.55, 1.5625, 1.575, 1.5875, 1.6, 1.6125, 1.625, 1.6375, 1.65, 1.6625, 1.675, 1.6875, 1.7, 1.70625, 1.7125, 1.71875, 1.725, 1.7375, 1.75),
    (2.75, 2.7625, 2.775, 2.78125, 2.7875, 2.79375, 2.8, 2.8125, 2.825, 2.8375, 2.85, 2.8625, 2.875, 2.8875, 2.9, 2.9125, 2.925, 2.9375, 2.95, 2.9625, 2.975, 2.9875, 3.0),
    (3.75, 3.75625, 3.7625, 3.76875, 3.775, 3.78125, 3.7875, 3.79375, 3.8, 3.8125, 3.825, 3.8375, 3.85, 3.8625, 3.875, 3.8875, 3.9, 3.9125, 3.925, 3.9375, 3.95, 3.9625, 3.975, 3.9875, 4.0),
)

ADAPTER_NAME = "q018_tablei_literal_failed_child_transition"
SCHEMA_VERSION = "phase5_t8ar_literal_failed_child_refinement_v1_units_dtype_ordering"
CONVERGENCE_TOLERANCE = 1.0e-4
EXPECTED_ACTIVE_FILES = 87
EXPECTED_MANIFEST_RECORDS = 86
T7CC_GREEN = "ACCEPT GREEN / LITERAL FAILED-CHILD RADIAL GATE ACCEPTED"
ACCEPTED_RISK_SCHEMA = "phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering"
ACCEPTED_RISK_GENERATION_HASH = (
    "92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9"
)
ACCEPTED_RISK_METADATA_HASH = (
    "1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161"
)
CLASSIFICATION_SNAPSHOT_HASH = (
    "e675b751fd4beae2446597034b99f847e0cc3528551bfc30f8efd3460ad944fe"
)
FINAL_ADAPTER_SNAPSHOT_HASH = (
    "8188b306fea0190654f752190f0ab6e96ef6970b16fea704b9cdb99ca96c7ccc"
)
ACCEPTED_ADAPTIVE_SCHEMA = (
    "phase5_t8ap_targeted_adaptive_refinement_v1_units_dtype_ordering"
)
ACCEPTED_ADAPTIVE_GENERATION_HASH = (
    "74cb3aafa63e12609d7f6b7f1efef10b539ebec1f1a91f2990356d9e56a51c94"
)
ACCEPTED_ADAPTIVE_METADATA_HASH = (
    "5bf94f5bd0ac5ad8678fe9e561012c53ff4e9c1cff14bd401f3feadba6fd2865"
)
ACCEPTED_FURTHER_LOCAL_SCHEMA = (
    "phase5_t8aq_further_local_refinement_v1_units_dtype_ordering"
)
ACCEPTED_FURTHER_LOCAL_GENERATION_HASH = (
    "a43ab0769a73768723505b2bee0715646e215624cc5b5efd880d97bcfff778f1"
)
ACCEPTED_FURTHER_LOCAL_METADATA_HASH = (
    "ff4210c449dfedb5b37228f76e9d91d71488935c7c5064c40b1ddefb961e8d96"
)

IMPLEMENTATION_PATHS = (
    "src/schwgw/io/tablei_literal_failed_child_refinement.py",
    "src/schwgw/io/__init__.py",
    "scripts/phase5_run_literal_failed_child_refinement.py",
    "tests/unit/test_tablei_literal_failed_child_refinement.py",
    "tests/regression/test_literal_failed_child_refinement_script.py",
)
_FROZEN_PACKAGE_HASHES = {
    "docs/superpowers/specs/2026-07-18-t4ac-t8ar-literal-failed-child-refinement-design.md": "0052af7360e06f5218360839a50e21b6d154cfc98dffd526328c43d962f58b58",
    "docs/superpowers/plans/2026-07-18-t4ac-literal-failed-child-radial-gate.md": "824594ad257f39d7e56d738837b16ceb8cde081bf12acba5e294fcaad594a75d",
    "docs/superpowers/plans/2026-07-18-t8ar-literal-failed-child-refinement.md": "972c74186364a3506001616b4f8fe8deb1563a1a1f44548b89bd96f08bd6ef7c",
    "docs/prompts/phase5_t4ac_literal_failed_child_radial_gate.md": "9189e68169774cfdf9abe6afee31c81ef95c30cc15269c7d9a8ede76d77ee655",
    "docs/prompts/phase5_t7cc_literal_failed_child_radial_review.md": "4a8097a3b8728b290139596e4611440a3de34a1a26c4503c3c38c074c462a3b7",
    "docs/prompts/phase5_t8ar_literal_failed_child_refinement.md": "dcdb2849111475cd2dbe45371607bc96181ca4abcadcf27d28f2cf20dc9fb242",
    "docs/prompts/phase5_t7cd_literal_failed_child_refinement_review.md": "0e9fcb766e722aa15f59544e5997eb81f861f2c2375f861389604a944b9395ed",
}

_FROZEN_SOURCE_HASHES = {
    "review_npz": "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb",
    "review_json": "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537",
    "review_manifest": "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf",
    "risk_ledger": "8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e",
    "risk_npz": "69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7",
    "risk_json": "b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566",
    "risk_audit": "7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b",
    "risk_manifest": "27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78",
    "adaptive_ledger": "2dfcaa7802ed8c7e3b3225429bb8b312d651441f378719331d023a5adb1e1caf",
    "adaptive_npz": "ec6328ad5b9acfdd341a00877a7aaf355d49a0d39db1569f3e488b34b9980f17",
    "adaptive_json": "9d9c821ab8c7f5af1ceb5136451e859a41bccd5456fe3beee834b876ffdc38cc",
    "adaptive_audit": "4606960110b658b74894c1b82a604c333481290ca0c451f3013574906eea5d67",
    "adaptive_manifest": "b728b1f5b4d45e622d5bebc32e710ac2be786556ab1ee7b7d9f26ca545223e5c",
    "t7bz_evidence": "8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e",
    "t4aa_classification": "aa3af55cd8454d610ebcd31fd8bbda5d37522a9a4e2279c8622decf3459a1b83",
    "t4aa_oracle": "002889f81ebce0574b948912217bf1231add3411253855db71adf2769b441d02",
    "t4aa_preflight": "a39bacfea6f2728129fde71b791c6f4f18eba05b34e9fa7dcf49b8b64d9824d4",
    "t4aa_manifest": "a796e4c34af8a80f800ec1f9ebc04089e4b3af9d79a190bc5a733b7c9f4c85d8",
    "further_local_ledger": "7b63e0689a01e32e27397007a3e458c800e2802bdd72c3f582a6e8a6bec4ae72",
    "further_local_npz": "27c263e8cb4b3270fe3103a9d79617a345a383a636da0ab3af4f954432fdf50b",
    "further_local_json": "df30e1f3cb3d17f87bc8f62470a87d5bca2e6819543fe9430b5c48a1d9552a8e",
    "further_local_audit": "a5f5e9d91d1b932fbec307244d35ebee688cfecaf2b11a54672b7eb2d33a2395",
    "further_local_manifest": "f84d6a1fb2cee35d2a00e81756110d2b75b99edca2946e79e2f70362f7350f3c",
    "t7cb_evidence": "57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01",
    "t7cc_record": "acfd4e53a8fc63a2e33eb7c5051508e5a1f918e6dcbe3768b1256452a5ff7298",
}
_FROZEN_GATE_HASHES = {
    "classification_manifest.json": "e5c934568ff1a9f80838df3fc674fea153e4c638777e6d7c9c2c2d32d0024e5b",
    "oracle_validation.json": "b4954a152aa81853fe53931bcb9ee9820b6d6da6d923019288f276d0519c52c6",
    "resume_preflight.json": "08b5542a26c0b95f6bf10005aeb21681f75735f53b924f894f1c133081ee2873",
    "manifest.md": "6b55500aae750f7b2400627825220f18e2ca9f608a4c977707e4f2ec363e78c8",
}
_T7CC_RECORD_PATH = Path("docs/handoffs/T7_current.md")
_DEFAULT_OUTPUT_DIR = Path("runs/phase5/fig5_fig6_literal_failed_child_refinement")
_DEFAULT_REVIEW_NPZ = Path(
    "runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"
)
_DEFAULT_RISK_DIR = Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot")
_DEFAULT_ADAPTIVE_DIR = Path(
    "runs/phase5/fig5_fig6_targeted_adaptive_refinement"
)
_DEFAULT_T7BZ_EVIDENCE = Path(
    "docs/handoffs/archive/T7_2026-07-16_pre_t7ca_further_local_radial_review.md"
)
_DEFAULT_T4AA_GATE_DIR = Path(
    "runs/phase5/fig5_fig6_targeted_adaptive_radial_gate"
)
_DEFAULT_FURTHER_LOCAL_DIR = Path(
    "runs/phase5/fig5_fig6_further_local_refinement"
)
_DEFAULT_T7CB_EVIDENCE = Path(
    "docs/handoffs/archive/T7_2026-07-18_pre_t7cc_literal_failed_child_radial_review.md"
)
_DEFAULT_GATE_DIR = Path(
    "runs/phase5/fig5_fig6_literal_failed_child_radial_gate"
)

PER_FREQUENCY_DTYPES = {
    "kM": "float64",
    "point_ids": "<U16",
    "point_group": "<U9",
    "point_x": "float64",
    "point_y": "float64",
    "point_z": "float64",
    "point_r": "float64",
    "point_theta": "float64",
    "point_phi": "float64",
    "lmax_values": "int64",
    "F_plus_history": "complex128",
    "F_cross_history": "complex128",
    "F_plus_complex": "complex128",
    "F_cross_complex": "complex128",
    "abs_F_plus": "float64",
    "abs_F_cross": "float64",
    "arg_F_plus_principal": "float64",
    "arg_F_cross_principal": "float64",
    "valid_ratio_plus_mask": "bool",
    "valid_ratio_cross_mask": "bool",
    "final_pair_delta_plus": "float64",
    "final_pair_delta_cross": "float64",
}
AGGREGATE_DTYPES = {
    name: dtype
    for name, dtype in PER_FREQUENCY_DTYPES.items()
    if name not in {"kM", "lmax_values", "F_plus_history", "F_cross_history"}
}
AGGREGATE_DTYPES = {"kM_values": "float64", **AGGREGATE_DTYPES}

PER_FREQUENCY_UNITS = {
    "kM": "dimensionless (M k)",
    "point_ids": "identifier",
    "point_group": "category label",
    "point_x": "M",
    "point_y": "M",
    "point_z": "M",
    "point_r": "M",
    "point_theta": "radian",
    "point_phi": "radian",
    "lmax_values": "dimensionless integer",
    "F_plus_history": "dimensionless complex amplification",
    "F_cross_history": "dimensionless complex amplification",
    "F_plus_complex": "dimensionless complex amplification",
    "F_cross_complex": "dimensionless complex amplification",
    "abs_F_plus": "dimensionless",
    "abs_F_cross": "dimensionless",
    "arg_F_plus_principal": "radian",
    "arg_F_cross_principal": "radian",
    "valid_ratio_plus_mask": "boolean",
    "valid_ratio_cross_mask": "boolean",
    "final_pair_delta_plus": "dimensionless",
    "final_pair_delta_cross": "dimensionless",
}
AGGREGATE_UNITS = {
    name: unit
    for name, unit in PER_FREQUENCY_UNITS.items()
    if name not in {"kM", "lmax_values", "F_plus_history", "F_cross_history"}
}
AGGREGATE_UNITS = {
    "kM_values": "dimensionless (M k)",
    **AGGREGATE_UNITS,
    "arg_F_plus_unwrapped": "radian",
    "arg_F_cross_unwrapped": "radian",
}
AGGREGATE_DTYPES.update(
    {"arg_F_plus_unwrapped": "float64", "arg_F_cross_unwrapped": "float64"}
)
UNITS_CONTRACT = {
    "per_frequency_arrays": PER_FREQUENCY_UNITS,
    "aggregate_arrays": AGGREGATE_UNITS,
    "numeric_metadata": {
        "frequencies": "dimensionless (M k)",
        "lmax_values": "dimensionless integer",
        "runtime_seconds": "second",
        "radial_solve_count": "count",
        "radial_reuse_count": "count",
        "radial_warning_count": "count",
        "adapter_use_count": "count",
        "phase": "radian",
        "phase_step": "radian",
        "magnitude": "dimensionless",
        "relative_magnitude_step": "dimensionless",
        "parent_width": "dimensionless (M k)",
        "child_spacing": "dimensionless (M k)",
    },
}
DTYPE_CONTRACT = {
    "per_frequency_arrays": PER_FREQUENCY_DTYPES,
    "aggregate_arrays": AGGREGATE_DTYPES,
}
ORDERING_CONTRACT = {
    "frequency_order": list(LITERAL_FAILED_CHILD_FREQUENCIES),
    "frequency_tokens": {str(k): FREQUENCY_TOKENS[k] for k in LITERAL_FAILED_CHILD_FREQUENCIES},
    "point_order": [point.point_id for point in TABLEI_POINTS],
    "lmax_values": {str(k): list(LITERAL_FAILED_CHILD_LMAX_VALUES[k]) for k in LITERAL_FAILED_CHILD_FREQUENCIES},
    "per_frequency_history_axes": ["lmax", "point"],
    "per_frequency_final_axes": ["point"],
    "aggregate_field_axes": ["frequency", "point"],
    "sampling_sequences": [list(sequence) for sequence in SEQUENCES],
    "parent_refinements": list(PARENT_REFINEMENTS),
}
NON_CLAIM_FLAGS = {
    "point_only": True,
    "literal_failed_child_refinement": True,
    "not_full_or_uniform_grid": True,
    "not_40_or_79_frequency_production": True,
    "not_uniform_0p025_scan": True,
    "not_uniform_0p0125_scan": True,
    "no_next_midpoint": True,
    "no_lmax_extension": True,
    "no_interpolation": True,
    "no_smoothing": True,
    "no_fill": True,
    "no_kirchhoff": True,
    "not_fixture": True,
    "not_paper_style": True,
}
_ROOT_FILES = {
    "checkpoint_ledger.json",
    "literal_failed_child_values.npz",
    "literal_failed_child_values.npz.json",
    "literal_failed_child_sampling_audit.json",
    "manifest.md",
}


class LiteralFailedChildRefinementContractError(ValueError):
    """Raised when the frozen T8ar contract cannot be preserved."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"))


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, Path):
        return str(value)
    return value


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(_json_safe(dict(value)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _atomic_npz(path: Path, arrays: Mapping[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        np.savez(stream, **arrays)
    os.replace(temporary, path)


def _canonical_array_fingerprint(value: np.ndarray) -> str:
    stream = BytesIO()
    np.save(stream, np.asarray(value), allow_pickle=False)
    return hashlib.sha256(stream.getvalue()).hexdigest()


def _array_fingerprints(arrays: Mapping[str, np.ndarray]) -> dict[str, str]:
    return {
        name: _canonical_array_fingerprint(np.asarray(value))
        for name, value in arrays.items()
        if name != "metadata_json"
    }


def _covers(solution: Any, required_radius: float) -> bool:
    lower = float(solution.r_grid[0])
    upper = solution.r_grid[-1] if solution.valid_until_r is None else solution.valid_until_r
    return lower <= float(required_radius) <= float(upper)


def _radial_cache_key(
    sector: Any,
    ell: int,
    k: float,
    background: Any,
    config: BoundaryConfig,
) -> tuple[Any, ...]:
    return (
        str(getattr(sector, "value", sector)),
        int(ell),
        float(k),
        type(background).__qualname__,
        float(getattr(background, "M", np.nan)),
        config.r_out,
        config.r_in_eps,
        config.rtol,
        config.atol,
        config.method,
        config.max_step,
        config.dense_output,
        config.experimental_required_radius_oracle,
    )


class _FrequencyRadialCache:
    def __init__(self, solver: Callable[..., Any]) -> None:
        self._solver = solver
        self._entries: dict[tuple[Any, ...], list[Any]] = {}
        self.solve_count = 0
        self.reuse_count = 0
        self.solutions: list[Any] = []

    def __call__(
        self,
        sector: Any,
        ell: int,
        k: float,
        background: Any,
        boundary_config: BoundaryConfig | None = None,
    ) -> Any:
        config = boundary_config or BoundaryConfig()
        required = config.required_eval_radius
        if required is None:
            raise LiteralFailedChildRefinementContractError(
                "literal failed-child radial cache requires an exact radius"
            )
        key = _radial_cache_key(sector, ell, k, background, config)
        entries = self._entries.setdefault(key, [])
        for existing in entries:
            if _covers(existing, float(required)):
                self.reuse_count += 1
                return existing
        solution = self._solver(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            boundary_config=config,
        )
        self.solve_count += 1
        self.solutions.append(solution)
        if not _covers(solution, float(required)):
            raise LiteralFailedChildRefinementContractError(
                "radial solver returned a solution outside its certified interval"
            )
        entries.append(solution)
        return solution


def _implementation_identity() -> dict[str, Any]:
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", *IMPLEMENTATION_PATHS],
            text=True,
        ).splitlines()
        commit_paths = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            text=True,
        ).splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LiteralFailedChildRefinementContractError(
            f"cannot establish implementation identity: {exc}"
        ) from exc
    if changed:
        raise LiteralFailedChildRefinementContractError(
            f"uncommitted implementation path(s): {sorted(changed)}"
        )
    if set(commit_paths) != set(IMPLEMENTATION_PATHS) or len(commit_paths) != len(
        IMPLEMENTATION_PATHS
    ):
        raise LiteralFailedChildRefinementContractError(
            "HEAD is not the frozen five-path T8ar implementation commit"
        )
    blobs: dict[str, dict[str, str]] = {}
    for path_text in IMPLEMENTATION_PATHS:
        path = Path(path_text)
        if not path.is_file():
            raise LiteralFailedChildRefinementContractError(f"missing implementation path: {path}")
        try:
            git_blob = subprocess.check_output(
                ["git", "rev-parse", f"HEAD:{path_text}"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise LiteralFailedChildRefinementContractError(
                f"cannot resolve implementation blob for {path_text}: {exc}"
            ) from exc
        blobs[path_text] = {"git_blob": git_blob, "sha256": _sha256(path)}
    return {"commit": head, "paths": list(IMPLEMENTATION_PATHS), "blobs": blobs}


def _selected_code_hashes() -> dict[str, str]:
    paths = (
        Path(__file__),
        Path("src/schwgw/io/tablei.py"),
        Path("src/schwgw/scattering/partial_wave.py"),
        Path("src/schwgw/numerics/radial_solver.py"),
        Path("src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py"),
    )
    return {str(path): _sha256(path) for path in paths}


def _validate_start_gate() -> None:
    try:
        text = _T7CC_RECORD_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise LiteralFailedChildRefinementContractError(f"cannot read T7cc record: {exc}") from exc
    if T7CC_GREEN not in text:
        raise LiteralFailedChildRefinementContractError("T7cc exact GREEN is absent")


def _validate_frozen_scope() -> None:
    if LITERAL_FAILED_CHILD_FREQUENCIES != _FROZEN_FREQUENCIES:
        raise LiteralFailedChildRefinementContractError("frozen frequency scope changed")
    if LITERAL_FAILED_CHILD_LMAX_VALUES != _FROZEN_LMAX_VALUES:
        raise LiteralFailedChildRefinementContractError("lmax extension or window change is forbidden")


def _validate_frozen_package() -> None:
    try:
        actual = {path: _sha256(Path(path)) for path in _FROZEN_PACKAGE_HASHES}
    except OSError as exc:
        raise LiteralFailedChildRefinementContractError(
            f"cannot verify frozen seven-file package: {exc}"
        ) from exc
    if actual != _FROZEN_PACKAGE_HASHES:
        raise LiteralFailedChildRefinementContractError("frozen seven-file package hash mismatch")


def _input_records(
    review_npz: Path,
    risk_dir: Path,
    adaptive_dir: Path,
    t7bz_evidence: Path,
    t4aa_gate_dir: Path,
    further_local_dir: Path,
    t7cb_evidence: Path,
    gate_dir: Path,
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    def active_files(path: Path) -> list[Path]:
        return [
            item
            for item in path.rglob("*")
            if item.is_file() and "quarantine" not in item.parts
        ]

    def require_package(path: Path, *, active: int, records: int, label: str) -> None:
        files = active_files(path)
        if len(files) != active or any(item.name.endswith(".tmp") for item in files):
            raise LiteralFailedChildRefinementContractError(
                f"accepted {label} cardinality/temp mismatch: active={len(files)}"
            )
        try:
            count = sum(
                line.startswith("- `") and "SHA256" in line
                for line in (path / "manifest.md").read_text(encoding="utf-8").splitlines()
            )
        except OSError as exc:
            raise LiteralFailedChildRefinementContractError(
                f"cannot read accepted {label} manifest: {exc}"
            ) from exc
        if count != records:
            raise LiteralFailedChildRefinementContractError(
                f"accepted {label} manifest cardinality={count}, expected {records}"
            )

    require_package(risk_dir, active=23, records=22, label="T8ao")
    require_package(adaptive_dir, active=31, records=30, label="T8ap")
    require_package(further_local_dir, active=53, records=52, label="T8aq")
    t4aa_files = active_files(t4aa_gate_dir)
    if len(t4aa_files) != 17 or any(item.name.endswith(".tmp") for item in t4aa_files):
        raise LiteralFailedChildRefinementContractError(
            f"accepted T4aa cardinality/temp mismatch: files={len(t4aa_files)}"
        )
    gate_files = active_files(gate_dir)
    if len(gate_files) != 45 or any(item.name.endswith(".tmp") for item in gate_files):
        raise LiteralFailedChildRefinementContractError(
            f"accepted T4ac cardinality/temp mismatch: files={len(gate_files)}"
        )
    source_paths = {
        "review_npz": review_npz,
        "review_json": review_npz.with_suffix(review_npz.suffix + ".json"),
        "review_manifest": review_npz.parent / "manifest.md",
        "risk_ledger": risk_dir / "checkpoint_ledger.json",
        "risk_npz": risk_dir / "risk_pilot_values.npz",
        "risk_json": risk_dir / "risk_pilot_values.npz.json",
        "risk_audit": risk_dir / "risk_pilot_sampling_audit.json",
        "risk_manifest": risk_dir / "manifest.md",
        "adaptive_ledger": adaptive_dir / "checkpoint_ledger.json",
        "adaptive_npz": adaptive_dir / "adaptive_refinement_values.npz",
        "adaptive_json": adaptive_dir / "adaptive_refinement_values.npz.json",
        "adaptive_audit": adaptive_dir / "adaptive_sampling_audit.json",
        "adaptive_manifest": adaptive_dir / "manifest.md",
        "t7bz_evidence": t7bz_evidence,
        "t4aa_classification": t4aa_gate_dir / "classification_manifest.json",
        "t4aa_oracle": t4aa_gate_dir / "oracle_validation.json",
        "t4aa_preflight": t4aa_gate_dir / "resume_preflight.json",
        "t4aa_manifest": t4aa_gate_dir / "manifest.md",
        "further_local_ledger": further_local_dir / "checkpoint_ledger.json",
        "further_local_npz": further_local_dir / "further_local_values.npz",
        "further_local_json": further_local_dir / "further_local_values.npz.json",
        "further_local_audit": further_local_dir / "further_local_sampling_audit.json",
        "further_local_manifest": further_local_dir / "manifest.md",
        "t7cb_evidence": t7cb_evidence,
        "t7cc_record": _T7CC_RECORD_PATH,
    }
    gate_paths = {name: gate_dir / name for name in _FROZEN_GATE_HASHES}
    missing = [str(path) for path in (*source_paths.values(), *gate_paths.values()) if not path.is_file()]
    if missing:
        raise LiteralFailedChildRefinementContractError(f"missing frozen input(s): {missing}")
    source_hashes = {name: _sha256(path) for name, path in source_paths.items()}
    gate_hashes = {name: _sha256(path) for name, path in gate_paths.items()}
    if source_hashes != _FROZEN_SOURCE_HASHES:
        raise LiteralFailedChildRefinementContractError("accepted source hash mismatch")
    if gate_hashes != _FROZEN_GATE_HASHES:
        raise LiteralFailedChildRefinementContractError("accepted T4ac/T7cc gate hash mismatch")
    try:
        risk = json.loads(source_paths["risk_json"].read_text(encoding="utf-8"))
        adaptive = json.loads(
            source_paths["adaptive_json"].read_text(encoding="utf-8")
        )
        further = json.loads(
            source_paths["further_local_json"].read_text(encoding="utf-8")
        )
        preflight = json.loads(gate_paths["resume_preflight.json"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LiteralFailedChildRefinementContractError(f"invalid frozen metadata: {exc}") from exc
    if (
        risk.get("schema_version") != ACCEPTED_RISK_SCHEMA
        or risk.get("generation_contract_hash") != ACCEPTED_RISK_GENERATION_HASH
        or risk.get("metadata_contract_hash") != ACCEPTED_RISK_METADATA_HASH
        or "units" not in risk
        or "ordering" not in risk
    ):
        raise LiteralFailedChildRefinementContractError("accepted T8ao metadata contract mismatch")
    if (
        adaptive.get("schema_version") != ACCEPTED_ADAPTIVE_SCHEMA
        or adaptive.get("generation_contract_hash")
        != ACCEPTED_ADAPTIVE_GENERATION_HASH
        or adaptive.get("metadata_contract_hash")
        != ACCEPTED_ADAPTIVE_METADATA_HASH
        or adaptive.get("shape") != [13, 8]
        or len(adaptive.get("frequency_metadata", [])) != 13
        or "units" not in adaptive
        or "dtypes" not in adaptive
        or "ordering" not in adaptive
    ):
        raise LiteralFailedChildRefinementContractError(
            "accepted T8ap metadata contract mismatch"
        )
    if (
        further.get("schema_version") != ACCEPTED_FURTHER_LOCAL_SCHEMA
        or further.get("generation_contract_hash")
        != ACCEPTED_FURTHER_LOCAL_GENERATION_HASH
        or further.get("metadata_contract_hash")
        != ACCEPTED_FURTHER_LOCAL_METADATA_HASH
        or further.get("shape") != [24, 8]
        or len(further.get("frequency_metadata", [])) != 24
        or "units" not in further
        or "dtypes" not in further
        or "ordering" not in further
    ):
        raise LiteralFailedChildRefinementContractError(
            "accepted T8aq metadata contract mismatch"
        )
    if (
        preflight.get("adapter_name") != ADAPTER_NAME
        or preflight.get("classification_snapshot_sha256")
        != CLASSIFICATION_SNAPSHOT_HASH
        or preflight.get("final_adapter_snapshot_sha256")
        != FINAL_ADAPTER_SNAPSHOT_HASH
    ):
        raise LiteralFailedChildRefinementContractError("accepted literal failed-child adapter mismatch")
    checkpoint_dir = gate_dir / "checkpoint"
    checkpoints = list(checkpoint_dir.glob("*.json"))
    if len(checkpoints) != 41:
        raise LiteralFailedChildRefinementContractError(
            "accepted literal failed-child checkpoint cardinality mismatch"
        )
    for path in checkpoints:
        checkpoint = json.loads(path.read_text(encoding="utf-8"))
        if checkpoint.get("complete") is not True or checkpoint.get("decision") != "PASS":
            raise LiteralFailedChildRefinementContractError(
                f"accepted literal failed-child checkpoint is not PASS: {path}"
            )
    return (
        {name: str(path) for name, path in source_paths.items()},
        source_hashes,
        {name: str(path) for name, path in gate_paths.items()},
        gate_hashes,
    )


def _contracts(
    *,
    source_paths: Mapping[str, str],
    source_hashes: Mapping[str, str],
    gate_paths: Mapping[str, str],
    gate_hashes: Mapping[str, str],
    implementation: Mapping[str, Any],
) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    generation = {
        "schema_version": SCHEMA_VERSION,
        "frequencies": list(LITERAL_FAILED_CHILD_FREQUENCIES),
        "frequency_tokens": {str(k): FREQUENCY_TOKENS[k] for k in LITERAL_FAILED_CHILD_FREQUENCIES},
        "lmax_values": {str(k): list(LITERAL_FAILED_CHILD_LMAX_VALUES[k]) for k in LITERAL_FAILED_CHILD_FREQUENCIES},
        "points": [point.metadata() for point in TABLEI_POINTS],
        "M": 1.0,
        "A_plus": 0.9 + 1.1j,
        "A_cross": 0.4 + 0.6j,
        "incident_direction": "+z",
        "r_out": 300.0,
        "r_in_eps": 1.0e-6,
        "rtol": 1.0e-10,
        "atol": 1.0e-12,
        "convergence_tolerance": CONVERGENCE_TOLERANCE,
        "adapter": ADAPTER_NAME,
        "classification_snapshot_sha256": CLASSIFICATION_SNAPSHOT_HASH,
        "final_adapter_snapshot_sha256": FINAL_ADAPTER_SNAPSHOT_HASH,
        "source_paths": dict(source_paths),
        "source_hashes": dict(source_hashes),
        "gate_paths": dict(gate_paths),
        "gate_hashes": dict(gate_hashes),
        "selected_code_hashes": _selected_code_hashes(),
        "implementation": dict(implementation),
        "frozen_package_hashes": _FROZEN_PACKAGE_HASHES,
        "cache_policy": "frequency-local certified-domain only; preserve disjoint local solutions",
        "resume_policy": "exact pair+ledger+contract+source+gate+implementation identity",
        "final_pair_policy": "no extension; fail if any relative complex delta exceeds 1e-4",
        "git_state": {"head": implementation["commit"], "unrelated_changes_excluded": True},
    }
    generation_hash = hashlib.sha256(_canonical_json(generation).encode()).hexdigest()
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "generation_contract_hash": generation_hash,
        "units": UNITS_CONTRACT,
        "dtypes": DTYPE_CONTRACT,
        "ordering": ORDERING_CONTRACT,
        "flags": NON_CLAIM_FLAGS,
        "source_paths": dict(source_paths),
        "source_hashes": dict(source_hashes),
        "gate_paths": dict(gate_paths),
        "gate_hashes": dict(gate_hashes),
    }
    metadata_hash = hashlib.sha256(_canonical_json(metadata).encode()).hexdigest()
    return generation, generation_hash, metadata, metadata_hash


def _verify_runtime_identity(
    *,
    source_paths: Mapping[str, str],
    source_hashes: Mapping[str, str],
    gate_paths: Mapping[str, str],
    gate_hashes: Mapping[str, str],
    implementation: Mapping[str, Any],
    selected_code_hashes: Mapping[str, str],
) -> None:
    _validate_frozen_package()
    try:
        current_sources = {
            name: _sha256(Path(path)) for name, path in source_paths.items()
        }
        current_gate = {
            name: _sha256(Path(path)) for name, path in gate_paths.items()
        }
    except OSError as exc:
        raise LiteralFailedChildRefinementContractError(
            f"frozen input changed during execution: {exc}"
        ) from exc
    if current_sources != dict(source_hashes) or current_gate != dict(gate_hashes):
        raise LiteralFailedChildRefinementContractError(
            "frozen input changed during execution"
        )
    if _implementation_identity() != dict(implementation):
        raise LiteralFailedChildRefinementContractError(
            "implementation identity changed during execution"
        )
    if _selected_code_hashes() != dict(selected_code_hashes):
        raise LiteralFailedChildRefinementContractError(
            "selected scientific code changed during execution"
        )


def _validate_output_tree(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    for path in output_dir.iterdir():
        if path.is_dir() and path.name in {"frequencies", "quarantine"}:
            continue
        if path.is_file() and path.name in _ROOT_FILES:
            continue
        raise LiteralFailedChildRefinementContractError(f"unexpected output path: {path}")
    frequencies = output_dir / "frequencies"
    if frequencies.exists():
        allowed = {
            f"kM_{FREQUENCY_TOKENS[k]}.npz" for k in LITERAL_FAILED_CHILD_FREQUENCIES
        } | {
            f"kM_{FREQUENCY_TOKENS[k]}.npz.json" for k in LITERAL_FAILED_CHILD_FREQUENCIES
        }
        for path in frequencies.iterdir():
            if not path.is_file() or path.name not in allowed:
                raise LiteralFailedChildRefinementContractError(
                    f"unexpected frequency artifact: {path}"
                )


def _new_ledger(
    *,
    generation_hash: str,
    metadata_hash: str,
    source_paths: Mapping[str, str],
    source_hashes: Mapping[str, str],
    gate_paths: Mapping[str, str],
    gate_hashes: Mapping[str, str],
    implementation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generation_contract_hash": generation_hash,
        "metadata_contract_hash": metadata_hash,
        "source_paths": dict(source_paths),
        "source_hashes": dict(source_hashes),
        "gate_paths": dict(gate_paths),
        "gate_hashes": dict(gate_hashes),
        "implementation": dict(implementation),
        "units": UNITS_CONTRACT,
        "dtypes": DTYPE_CONTRACT,
        "ordering": ORDERING_CONTRACT,
        "flags": NON_CLAIM_FLAGS,
        "completed": {},
    }


def _load_ledger(path: Path, expected: Mapping[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(expected)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LiteralFailedChildRefinementContractError(f"invalid checkpoint ledger: {exc}") from exc
    for key in (
        "schema_version",
        "generation_contract_hash",
        "metadata_contract_hash",
        "source_paths",
        "source_hashes",
        "gate_paths",
        "gate_hashes",
        "implementation",
        "units",
        "dtypes",
        "ordering",
        "flags",
    ):
        if value.get(key) != expected.get(key):
            raise LiteralFailedChildRefinementContractError(f"checkpoint ledger {key} mismatch")
    if not isinstance(value.get("completed"), dict):
        raise LiteralFailedChildRefinementContractError("checkpoint ledger completed mapping is invalid")
    return value


def _transaction_paths(output_dir: Path, kM: float) -> tuple[Path, Path]:
    npz = output_dir / "frequencies" / f"kM_{FREQUENCY_TOKENS[kM]}.npz"
    return npz, npz.with_suffix(npz.suffix + ".json")


def _validate_loaded_arrays(
    arrays: Mapping[str, np.ndarray], *, per_frequency: bool
) -> bool:
    expected = PER_FREQUENCY_DTYPES if per_frequency else AGGREGATE_DTYPES
    if set(arrays) != set(expected):
        return False
    return all(str(np.asarray(arrays[name]).dtype) == dtype for name, dtype in expected.items())


def _valid_transaction(
    npz: Path,
    sidecar: Path,
    entry: Mapping[str, Any] | None,
    *,
    kM: float,
    generation_hash: str,
    metadata_hash: str,
    source_hashes: Mapping[str, str],
    gate_hashes: Mapping[str, str],
    implementation: Mapping[str, Any],
) -> bool:
    if entry is None or not npz.is_file() or not sidecar.is_file():
        return False
    if entry.get("npz_sha256") != _sha256(npz) or entry.get("json_sha256") != _sha256(sidecar):
        return False
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        with np.load(npz, allow_pickle=False) as data:
            arrays = {name: np.asarray(data[name]) for name in data.files if name != "metadata_json"}
            embedded = json.loads(str(data["metadata_json"].item()))
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False
    return bool(
        _validate_loaded_arrays(arrays, per_frequency=True)
        and float(arrays["kM"].item()) == float(kM)
        and np.array_equal(
            arrays["point_ids"].astype(str),
            np.asarray([point.point_id for point in TABLEI_POINTS]),
        )
        and arrays["F_plus_complex"].shape == (8,)
        and arrays["F_cross_complex"].shape == (8,)
        and np.isfinite(arrays["F_plus_complex"]).all()
        and np.isfinite(arrays["F_cross_complex"]).all()
        and arrays["valid_ratio_plus_mask"].all()
        and arrays["valid_ratio_cross_mask"].all()
        and {key: value for key, value in metadata.items() if key != "npz_sha256"}
        == embedded
        and metadata.get("complete") is True
        and metadata.get("generation_contract_hash") == generation_hash
        and metadata.get("metadata_contract_hash") == metadata_hash
        and metadata.get("source_hashes") == dict(source_hashes)
        and metadata.get("gate_hashes") == dict(gate_hashes)
        and metadata.get("implementation") == dict(implementation)
        and metadata.get("adapter") == ADAPTER_NAME
        and metadata.get("lmax_values") == list(LITERAL_FAILED_CHILD_LMAX_VALUES[kM])
        and metadata.get("units") == UNITS_CONTRACT
        and metadata.get("dtypes") == DTYPE_CONTRACT
        and metadata.get("ordering") == ORDERING_CONTRACT
        and metadata.get("flags") == NON_CLAIM_FLAGS
        and metadata.get("array_fingerprints") == _array_fingerprints(arrays)
        and metadata.get("npz_sha256") == _sha256(npz)
    )


def _quarantine_pair(output_dir: Path, npz: Path, sidecar: Path) -> None:
    quarantine = output_dir / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for path in (npz, sidecar):
        if path.exists():
            os.replace(path, quarantine / f"{path.name}.{stamp}")


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


def _relative_delta(final: np.ndarray, previous: np.ndarray) -> np.ndarray:
    scale = np.maximum(1.0, np.maximum(np.abs(final), np.abs(previous)))
    return np.abs(final - previous) / scale


def _warning_summary(cache: _FrequencyRadialCache) -> tuple[list[str], int, int]:
    codes: list[str] = []
    adapter_count = 0
    warning_count = 0
    for solution in cache.solutions:
        diagnostics = getattr(solution, "diagnostics", None)
        for warning in getattr(diagnostics, "warnings", ()):
            warning_count += 1
            code = str(getattr(warning, "code", "unknown"))
            codes.append(code)
            if code == "q018_tablei_literal_failed_child_transition_oracle_used":
                adapter_count += 1
    return sorted(set(codes)), adapter_count, warning_count


def _compute_frequency(
    kM: float,
    *,
    generation_hash: str,
    metadata_hash: str,
    source_paths: Mapping[str, str],
    source_hashes: Mapping[str, str],
    gate_paths: Mapping[str, str],
    gate_hashes: Mapping[str, str],
    implementation: Mapping[str, Any],
    selected_code_hashes: Mapping[str, str],
    polarization_solver: Callable[..., Any],
    flat_solver: Callable[..., Any],
    radial_solver: Callable[..., Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    started = time.monotonic()
    background = SchwarzschildBackground(M=1.0)
    lmax_values = LITERAL_FAILED_CHILD_LMAX_VALUES[kM]
    plus_history = np.empty((len(lmax_values), 8), dtype=np.complex128)
    cross_history = np.empty_like(plus_history)
    plus_mask = np.empty((len(lmax_values), 8), dtype=bool)
    cross_mask = np.empty_like(plus_mask)
    cache = _FrequencyRadialCache(radial_solver)
    point_order = sorted(
        range(8), key=lambda index: TABLEI_POINTS[index].r, reverse=True
    )
    for row, lmax in enumerate(lmax_values):
        for point_index in point_order:
            point = TABLEI_POINTS[point_index]
            boundary = BoundaryConfig(
                r_out=300.0,
                r_in_eps=1.0e-6,
                rtol=1.0e-10,
                atol=1.0e-12,
                required_eval_radius=point.r,
                experimental_required_radius_oracle=ADAPTER_NAME,
            )
            lensed = polarization_solver(
                background=background,
                k=kM,
                r=point.r,
                theta=point.theta,
                phi=point.phi,
                A_plus=0.9 + 1.1j,
                A_cross=0.4 + 0.6j,
                lmax=lmax,
                boundary_config=boundary,
                radial_solver=cache,
            )
            flat = flat_solver(
                k=kM,
                r=point.r,
                theta=point.theta,
                phi=point.phi,
                A_plus=0.9 + 1.1j,
                A_cross=0.4 + 0.6j,
                lmax=lmax,
            )
            valid_plus = (
                _finite_complex(lensed.h_plus)
                and _finite_complex(flat.h_plus)
                and abs(flat.h_plus) > 0.0
            )
            valid_cross = (
                _finite_complex(lensed.h_cross)
                and _finite_complex(flat.h_cross)
                and abs(flat.h_cross) > 0.0
            )
            plus_mask[row, point_index] = valid_plus
            cross_mask[row, point_index] = valid_cross
            plus_history[row, point_index] = (
                lensed.h_plus / flat.h_plus if valid_plus else np.nan + 1j * np.nan
            )
            cross_history[row, point_index] = (
                lensed.h_cross / flat.h_cross
                if valid_cross
                else np.nan + 1j * np.nan
            )
    if not plus_mask.all() or not cross_mask.all():
        raise LiteralFailedChildRefinementContractError(f"nonfinite or invalid ratio at kM={kM}")
    delta_plus = _relative_delta(plus_history[-1], plus_history[-2])
    delta_cross = _relative_delta(cross_history[-1], cross_history[-2])
    if not np.all(delta_plus <= CONVERGENCE_TOLERANCE) or not np.all(
        delta_cross <= CONVERGENCE_TOLERANCE
    ):
        raise LiteralFailedChildRefinementContractError(
            f"final adjacent lmax pair failed at kM={kM}; "
            f"max_plus={delta_plus.max():.17g}, max_cross={delta_cross.max():.17g}"
        )
    final_plus = plus_history[-1]
    final_cross = cross_history[-1]
    warning_codes, adapter_count, warning_count = _warning_summary(cache)
    arrays = {
        "kM": np.asarray(kM, dtype=np.float64),
        "point_ids": np.asarray([point.point_id for point in TABLEI_POINTS], dtype="<U16"),
        "point_group": np.asarray([point.group for point in TABLEI_POINTS], dtype="<U9"),
        "point_x": np.asarray([point.x for point in TABLEI_POINTS], dtype=np.float64),
        "point_y": np.asarray([point.y for point in TABLEI_POINTS], dtype=np.float64),
        "point_z": np.asarray([point.z for point in TABLEI_POINTS], dtype=np.float64),
        "point_r": np.asarray([point.r for point in TABLEI_POINTS], dtype=np.float64),
        "point_theta": np.asarray([point.theta for point in TABLEI_POINTS], dtype=np.float64),
        "point_phi": np.asarray([point.phi for point in TABLEI_POINTS], dtype=np.float64),
        "lmax_values": np.asarray(lmax_values, dtype=np.int64),
        "F_plus_history": plus_history,
        "F_cross_history": cross_history,
        "F_plus_complex": final_plus,
        "F_cross_complex": final_cross,
        "abs_F_plus": np.abs(final_plus),
        "abs_F_cross": np.abs(final_cross),
        "arg_F_plus_principal": np.angle(final_plus),
        "arg_F_cross_principal": np.angle(final_cross),
        "valid_ratio_plus_mask": plus_mask[-1],
        "valid_ratio_cross_mask": cross_mask[-1],
        "final_pair_delta_plus": delta_plus,
        "final_pair_delta_cross": delta_cross,
    }
    if not _validate_loaded_arrays(arrays, per_frequency=True):
        raise LiteralFailedChildRefinementContractError("per-frequency dtype contract mismatch")
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "frequency_token": FREQUENCY_TOKENS[kM],
        "point_ids": [point.point_id for point in TABLEI_POINTS],
        "lmax_values": list(lmax_values),
        "final_lmax_pair": list(lmax_values[-2:]),
        "max_final_pair_delta_plus": float(delta_plus.max()),
        "max_final_pair_delta_cross": float(delta_cross.max()),
        "runtime_seconds": time.monotonic() - started,
        "radial_solve_count": cache.solve_count,
        "radial_reuse_count": cache.reuse_count,
        "radial_warning_codes": warning_codes,
        "radial_warning_count": warning_count,
        "adapter_use_count": adapter_count,
        "adapter": ADAPTER_NAME,
        "generation_contract_hash": generation_hash,
        "metadata_contract_hash": metadata_hash,
        "source_paths": dict(source_paths),
        "source_hashes": dict(source_hashes),
        "gate_paths": dict(gate_paths),
        "gate_hashes": dict(gate_hashes),
        "implementation": dict(implementation),
        "selected_code_hashes": dict(selected_code_hashes),
        "units": UNITS_CONTRACT,
        "dtypes": DTYPE_CONTRACT,
        "ordering": ORDERING_CONTRACT,
        "flags": NON_CLAIM_FLAGS,
        "array_fingerprints": _array_fingerprints(arrays),
    }
    arrays["metadata_json"] = np.asarray(
        json.dumps(_json_safe(metadata), sort_keys=True)
    )
    return arrays, metadata


def _write_transaction(
    output_dir: Path,
    kM: float,
    arrays: Mapping[str, np.ndarray],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    npz, sidecar = _transaction_paths(output_dir, kM)
    _atomic_npz(npz, arrays)
    metadata_value = dict(metadata)
    metadata_value["npz_sha256"] = _sha256(npz)
    _atomic_json(sidecar, metadata_value)
    return {
        "complete": True,
        "kM": kM,
        "frequency_token": FREQUENCY_TOKENS[kM],
        "npz_path": str(npz),
        "json_path": str(sidecar),
        "npz_sha256": _sha256(npz),
        "json_sha256": _sha256(sidecar),
    }


def _load_frequency(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        return {name: np.asarray(data[name]) for name in data.files if name != "metadata_json"}


def _common_metadata(
    *,
    generation_hash: str,
    metadata_hash: str,
    source_paths: Mapping[str, str],
    source_hashes: Mapping[str, str],
    gate_paths: Mapping[str, str],
    gate_hashes: Mapping[str, str],
    implementation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generation_contract_hash": generation_hash,
        "metadata_contract_hash": metadata_hash,
        "source_paths": dict(source_paths),
        "source_hashes": dict(source_hashes),
        "gate_paths": dict(gate_paths),
        "gate_hashes": dict(gate_hashes),
        "implementation": dict(implementation),
        "units": UNITS_CONTRACT,
        "dtypes": DTYPE_CONTRACT,
        "ordering": ORDERING_CONTRACT,
        "flags": NON_CLAIM_FLAGS,
    }


def _aggregate(
    output_dir: Path,
    ledger: Mapping[str, Any],
    common: Mapping[str, Any],
) -> Path:
    rows: list[dict[str, np.ndarray]] = []
    sidecars: list[dict[str, Any]] = []
    for kM in LITERAL_FAILED_CHILD_FREQUENCIES:
        npz, sidecar = _transaction_paths(output_dir, kM)
        entry = ledger["completed"].get(FREQUENCY_TOKENS[kM])
        if not _valid_transaction(
            npz,
            sidecar,
            entry,
            kM=kM,
            generation_hash=common["generation_contract_hash"],
            metadata_hash=common["metadata_contract_hash"],
            source_hashes=common["source_hashes"],
            gate_hashes=common["gate_hashes"],
            implementation=common["implementation"],
        ):
            raise LiteralFailedChildRefinementContractError(
                f"cannot aggregate invalid kM={kM} transaction"
            )
        rows.append(_load_frequency(npz))
        sidecars.append(json.loads(sidecar.read_text(encoding="utf-8")))
    arrays: dict[str, np.ndarray] = {
        "kM_values": np.asarray(LITERAL_FAILED_CHILD_FREQUENCIES, dtype=np.float64),
        **{
            name: rows[0][name]
            for name in (
                "point_ids",
                "point_group",
                "point_x",
                "point_y",
                "point_z",
                "point_r",
                "point_theta",
                "point_phi",
            )
        },
    }
    stack_names = (
        "F_plus_complex",
        "F_cross_complex",
        "abs_F_plus",
        "abs_F_cross",
        "arg_F_plus_principal",
        "arg_F_cross_principal",
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "final_pair_delta_plus",
        "final_pair_delta_cross",
    )
    for name in stack_names:
        arrays[name] = np.stack([row[name] for row in rows])
    arrays["arg_F_plus_unwrapped"] = np.unwrap(
        arrays["arg_F_plus_principal"], axis=0
    )
    arrays["arg_F_cross_unwrapped"] = np.unwrap(
        arrays["arg_F_cross_principal"], axis=0
    )
    if not _validate_loaded_arrays(arrays, per_frequency=False):
        raise LiteralFailedChildRefinementContractError("aggregate dtype contract mismatch")
    metadata = {
        **dict(common),
        "shape": [41, 8],
        "frequency_metadata": sidecars,
        "array_fingerprints": _array_fingerprints(arrays),
    }
    arrays["metadata_json"] = np.asarray(
        json.dumps(_json_safe(metadata), sort_keys=True)
    )
    path = output_dir / "literal_failed_child_values.npz"
    _atomic_npz(path, arrays)
    metadata["npz_sha256"] = _sha256(path)
    _atomic_json(path.with_suffix(".npz.json"), metadata)
    return path


def _load_values(path: Path) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    with np.load(path, allow_pickle=False) as data:
        return np.asarray(data["kM_values"]), {
            "plus": np.asarray(data["F_plus_complex"]),
            "cross": np.asarray(data["F_cross_complex"]),
        }


def _row_at(kM: float, sources: tuple[tuple[np.ndarray, dict[str, np.ndarray]], ...], component: str) -> np.ndarray:
    matches: list[np.ndarray] = []
    for frequencies, values in sources:
        index = np.flatnonzero(frequencies == kM)
        if index.size == 1:
            matches.append(values[component][index[0]])
    if len(matches) != 1:
        raise LiteralFailedChildRefinementContractError(
            f"frequency {kM} has {len(matches)} exact source rows"
        )
    return matches[0]


def _relative_magnitude_step(a: float, b: float) -> float:
    return float(abs(a - b) / max(1.0, a, b))


def _strict_extrema(magnitude: np.ndarray) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in range(1, magnitude.shape[0] - 1):
        for column in range(magnitude.shape[1]):
            center = magnitude[row, column]
            if (
                center > magnitude[row - 1, column]
                and center > magnitude[row + 1, column]
            ) or (
                center < magnitude[row - 1, column]
                and center < magnitude[row + 1, column]
            ):
                result.append(
                    {"sequence_index": row, "point_index": column, "magnitude": float(center)}
                )
    return result


def _sampling_audit(
    output_dir: Path,
    review_npz: Path,
    risk_npz: Path,
    adaptive_npz: Path,
    further_local_npz: Path,
    common: Mapping[str, Any],
) -> None:
    sources = (
        _load_values(review_npz),
        _load_values(risk_npz),
        _load_values(adaptive_npz),
        _load_values(further_local_npz),
        _load_values(output_dir / "literal_failed_child_values.npz"),
    )
    phase_records: list[dict[str, Any]] = []
    sequence_summaries: list[dict[str, Any]] = []
    for sequence_index, sequence in enumerate(SEQUENCES):
        for component in ("plus", "cross"):
            values = np.stack([_row_at(kM, sources, component) for kM in sequence])
            magnitude = np.abs(values)
            phase = np.unwrap(np.angle(values), axis=0)
            for interval_index in range(len(sequence) - 1):
                for point_index, point in enumerate(TABLEI_POINTS):
                    phase_records.append(
                        {
                            "sequence_index": sequence_index,
                            "component": component,
                            "point_id": point.point_id,
                            "point_index": point_index,
                            "interval": [sequence[interval_index], sequence[interval_index + 1]],
                            "phase_values": [
                                float(phase[interval_index, point_index]),
                                float(phase[interval_index + 1, point_index]),
                            ],
                            "absolute_phase_step": float(
                                abs(phase[interval_index + 1, point_index] - phase[interval_index, point_index])
                            ),
                        }
                    )
            for point_index, point in enumerate(TABLEI_POINTS):
                steps = np.abs(np.diff(magnitude[:, point_index]))
                largest = int(np.argmax(steps))
                endpoint_step = float(abs(magnitude[-1, point_index] - magnitude[0, point_index]))
                total_variation = float(np.sum(steps))
                sequence_summaries.append(
                    {
                        "sequence_index": sequence_index,
                        "sequence": list(sequence),
                        "component": component,
                        "point_id": point.point_id,
                        "magnitude_total_variation": total_variation,
                        "endpoint_magnitude_step": endpoint_step,
                        "cancellation": total_variation - endpoint_step,
                        "largest_step_interval": [sequence[largest], sequence[largest + 1]],
                        "largest_step": float(steps[largest]),
                    }
                )
            extrema = _strict_extrema(magnitude)
            for record in sequence_summaries[-8:]:
                point_index = [point.point_id for point in TABLEI_POINTS].index(record["point_id"])
                record["strict_interior_extrema"] = [
                    item for item in extrema if item["point_index"] == point_index
                ]
    hierarchical: list[dict[str, Any]] = []
    for mapping_index, mapping in enumerate(PARENT_REFINEMENTS):
        parent = mapping["parent"]
        midpoint = float(mapping["midpoint"])
        for component in ("plus", "cross"):
            left_values = _row_at(float(parent[0]), sources, component)
            mid_values = _row_at(midpoint, sources, component)
            right_values = _row_at(float(parent[1]), sources, component)
            for point_index, point in enumerate(TABLEI_POINTS):
                magnitudes = [
                    float(abs(left_values[point_index])),
                    float(abs(mid_values[point_index])),
                    float(abs(right_values[point_index])),
                ]
                parent_step = _relative_magnitude_step(magnitudes[0], magnitudes[2])
                for child_index, child in enumerate(mapping["children"]):
                    a = magnitudes[child_index]
                    b = magnitudes[child_index + 1]
                    hierarchical.append(
                        {
                            "mapping_index": mapping_index,
                            "midpoint": midpoint,
                            "parent": list(parent),
                            "parent_width": float(mapping["parent_width"]),
                            "child_index": child_index,
                            "child": list(child),
                            "child_spacing": float(child[1] - child[0]),
                            "component": component,
                            "point_id": point.point_id,
                            "point_index": point_index,
                            "parent_magnitudes": [magnitudes[0], magnitudes[2]],
                            "child_magnitudes": [a, b],
                            "parent_relative_step": parent_step,
                            "child_relative_step": _relative_magnitude_step(a, b),
                        }
                    )
    if (
        len(phase_records) != 1472
        or len(hierarchical) != 1312
        or len(sequence_summaries) != 80
    ):
        raise LiteralFailedChildRefinementContractError("sampling audit cardinality mismatch")
    _atomic_json(
        output_dir / "literal_failed_child_sampling_audit.json",
        {
            **dict(common),
            "diagnostic_only": True,
            "acceptance_decision_emitted": False,
            "phase_record_count": len(phase_records),
            "hierarchical_magnitude_record_count": len(hierarchical),
            "phase_records": phase_records,
            "hierarchical_magnitude_records": hierarchical,
            "sequence_summaries": sequence_summaries,
        },
    )


def _manifest(output_dir: Path, common: Mapping[str, Any]) -> None:
    files = sorted(
        path
        for path in output_dir.rglob("*")
        if path.is_file()
        and path.name != "manifest.md"
        and "quarantine" not in path.parts
    )
    if len(files) != EXPECTED_MANIFEST_RECORDS:
        raise LiteralFailedChildRefinementContractError(
            f"manifest input cardinality is {len(files)}, expected {EXPECTED_MANIFEST_RECORDS}"
        )
    lines = [
        "# Literal Failed-Child Forty-One-Frequency Point-Only Evidence",
        "",
        f"schema_version: `{SCHEMA_VERSION}`",
        f"generation_contract_hash: `{common['generation_contract_hash']}`",
        f"metadata_contract_hash: `{common['metadata_contract_hash']}`",
        f"source_paths: `{_canonical_json(common['source_paths'])}`",
        f"source_hashes: `{_canonical_json(common['source_hashes'])}`",
        f"gate_paths: `{_canonical_json(common['gate_paths'])}`",
        f"gate_hashes: `{_canonical_json(common['gate_hashes'])}`",
        f"implementation: `{_canonical_json(common['implementation'])}`",
        f"units: `{_canonical_json(UNITS_CONTRACT)}`",
        f"dtypes: `{_canonical_json(DTYPE_CONTRACT)}`",
        f"ordering: `{_canonical_json(ORDERING_CONTRACT)}`",
        f"flags: `{_canonical_json(NON_CLAIM_FLAGS)}`",
        "",
        "This package is point-only evidence, not production or scientific acceptance.",
        "No interpolation, smoothing, fill, lmax extension, next midpoint,",
        "Kirchhoff, fixture, plot, or paper-style artifact is included.",
        "",
        "## Files",
        "",
    ]
    for path in files:
        lines.append(
            f"- `{path.relative_to(output_dir)}` — {path.stat().st_size} bytes — "
            f"SHA256 `{_sha256(path)}`"
        )
    temporary = output_dir / "manifest.md.tmp"
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temporary, output_dir / "manifest.md")


def run_literal_failed_child_refinement(
    *,
    output_dir: str | Path = _DEFAULT_OUTPUT_DIR,
    accepted_review_npz: str | Path = _DEFAULT_REVIEW_NPZ,
    accepted_risk_pilot_dir: str | Path = _DEFAULT_RISK_DIR,
    accepted_adaptive_dir: str | Path = _DEFAULT_ADAPTIVE_DIR,
    accepted_t7bz_evidence: str | Path = _DEFAULT_T7BZ_EVIDENCE,
    accepted_t4aa_gate_dir: str | Path = _DEFAULT_T4AA_GATE_DIR,
    accepted_further_local_dir: str | Path = _DEFAULT_FURTHER_LOCAL_DIR,
    accepted_t7cb_evidence: str | Path = _DEFAULT_T7CB_EVIDENCE,
    radial_gate_dir: str | Path = _DEFAULT_GATE_DIR,
    resume: bool = False,
    polarization_solver: Callable[..., Any] | None = None,
    flat_solver: Callable[..., Any] | None = None,
    radial_solver: Callable[..., Any] | None = None,
) -> Path:
    """Run or safely resume the frozen forty-one-frequency T8ar evidence."""

    _validate_frozen_scope()
    _validate_start_gate()
    _validate_frozen_package()
    output = Path(output_dir)
    review = Path(accepted_review_npz)
    risk = Path(accepted_risk_pilot_dir)
    adaptive = Path(accepted_adaptive_dir)
    t7bz = Path(accepted_t7bz_evidence)
    t4aa_gate = Path(accepted_t4aa_gate_dir)
    further_local = Path(accepted_further_local_dir)
    t7cb = Path(accepted_t7cb_evidence)
    gate = Path(radial_gate_dir)
    _validate_output_tree(output)
    source_paths, source_hashes, gate_paths, gate_hashes = _input_records(
        review, risk, adaptive, t7bz, t4aa_gate, further_local, t7cb, gate
    )
    implementation = _implementation_identity()
    generation, generation_hash, _, metadata_hash = _contracts(
        source_paths=source_paths,
        source_hashes=source_hashes,
        gate_paths=gate_paths,
        gate_hashes=gate_hashes,
        implementation=implementation,
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "frequencies").mkdir(exist_ok=True)
    ledger_path = output / "checkpoint_ledger.json"
    expected_ledger = _new_ledger(
        generation_hash=generation_hash,
        metadata_hash=metadata_hash,
        source_paths=source_paths,
        source_hashes=source_hashes,
        gate_paths=gate_paths,
        gate_hashes=gate_hashes,
        implementation=implementation,
    )
    ledger = _load_ledger(ledger_path, expected_ledger)
    compute = compute_polarization if polarization_solver is None else polarization_solver
    flat = compute_flat_no_lens_polarization if flat_solver is None else flat_solver
    radial = solve_radial_mode if radial_solver is None else radial_solver
    for kM in LITERAL_FAILED_CHILD_FREQUENCIES:
        _verify_runtime_identity(
            source_paths=source_paths,
            source_hashes=source_hashes,
            gate_paths=gate_paths,
            gate_hashes=gate_hashes,
            implementation=implementation,
            selected_code_hashes=generation["selected_code_hashes"],
        )
        npz, sidecar = _transaction_paths(output, kM)
        token = FREQUENCY_TOKENS[kM]
        entry = ledger["completed"].get(token)
        if resume and _valid_transaction(
            npz,
            sidecar,
            entry,
            kM=kM,
            generation_hash=generation_hash,
            metadata_hash=metadata_hash,
            source_hashes=source_hashes,
            gate_hashes=gate_hashes,
            implementation=implementation,
        ):
            continue
        if npz.exists() or sidecar.exists():
            _quarantine_pair(output, npz, sidecar)
        ledger["completed"].pop(token, None)
        _atomic_json(ledger_path, ledger)
        arrays, metadata = _compute_frequency(
            kM,
            generation_hash=generation_hash,
            metadata_hash=metadata_hash,
            source_paths=source_paths,
            source_hashes=source_hashes,
            gate_paths=gate_paths,
            gate_hashes=gate_hashes,
            implementation=implementation,
            selected_code_hashes=generation["selected_code_hashes"],
            polarization_solver=compute,
            flat_solver=flat,
            radial_solver=radial,
        )
        entry = _write_transaction(output, kM, arrays, metadata)
        ledger["completed"][token] = entry
        ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
        _atomic_json(ledger_path, ledger)
        ledger = _load_ledger(ledger_path, expected_ledger)
        entry = ledger["completed"].get(token)
        if not _valid_transaction(
            npz,
            sidecar,
            entry,
            kM=kM,
            generation_hash=generation_hash,
            metadata_hash=metadata_hash,
            source_hashes=source_hashes,
            gate_hashes=gate_hashes,
            implementation=implementation,
        ):
            raise LiteralFailedChildRefinementContractError(
                f"fresh transaction validation failed at kM={kM}"
            )
    _verify_runtime_identity(
        source_paths=source_paths,
        source_hashes=source_hashes,
        gate_paths=gate_paths,
        gate_hashes=gate_hashes,
        implementation=implementation,
        selected_code_hashes=generation["selected_code_hashes"],
    )
    common = _common_metadata(
        generation_hash=generation_hash,
        metadata_hash=metadata_hash,
        source_paths=source_paths,
        source_hashes=source_hashes,
        gate_paths=gate_paths,
        gate_hashes=gate_hashes,
        implementation=implementation,
    )
    aggregate = _aggregate(output, ledger, common)
    _sampling_audit(
        output,
        review,
        risk / "risk_pilot_values.npz",
        adaptive / "adaptive_refinement_values.npz",
        further_local / "further_local_values.npz",
        common,
    )
    _manifest(output, common)
    _verify_runtime_identity(
        source_paths=source_paths,
        source_hashes=source_hashes,
        gate_paths=gate_paths,
        gate_hashes=gate_hashes,
        implementation=implementation,
        selected_code_hashes=generation["selected_code_hashes"],
    )
    active = [
        path
        for path in output.rglob("*")
        if path.is_file() and "quarantine" not in path.parts
    ]
    if len(active) != EXPECTED_ACTIVE_FILES:
        raise LiteralFailedChildRefinementContractError(
            f"active artifact cardinality is {len(active)}, expected {EXPECTED_ACTIVE_FILES}"
        )
    return aggregate


__all__ = [
    "ADAPTER_NAME",
    "LITERAL_FAILED_CHILD_FREQUENCIES",
    "LITERAL_FAILED_CHILD_LMAX_VALUES",
    "LiteralFailedChildRefinementContractError",
    "DTYPE_CONTRACT",
    "EXPECTED_ACTIVE_FILES",
    "EXPECTED_MANIFEST_RECORDS",
    "FREQUENCY_TOKENS",
    "ORDERING_CONTRACT",
    "PARENT_REFINEMENTS",
    "SCHEMA_VERSION",
    "UNITS_CONTRACT",
    "run_literal_failed_child_refinement",
]
