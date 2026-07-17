"""Generated immutable T4ab further-local Q018 envelope."""

from __future__ import annotations

FREQUENCIES: tuple[float, ...] = (0.325, 0.375, 0.825, 0.875, 0.925, 0.975, 1.525, 1.575, 1.625, 1.675, 1.7125, 1.7375, 2.7625, 2.7875, 2.825, 2.875, 2.925, 2.975, 3.7625, 3.7875, 3.825, 3.875, 3.925, 3.975)
FREQUENCY_TOKENS: dict[float, str] = {0.325: '0p325', 0.375: '0p375', 0.825: '0p825', 0.875: '0p875', 0.925: '0p925', 0.975: '0p975', 1.525: '1p525', 1.575: '1p575', 1.625: '1p625', 1.675: '1p675', 1.7125: '1p7125', 1.7375: '1p7375', 2.7625: '2p7625', 2.7875: '2p7875', 2.825: '2p825', 2.875: '2p875', 2.925: '2p925', 2.975: '2p975', 3.7625: '3p7625', 3.7875: '3p7875', 3.825: '3p825', 3.875: '3p875', 3.925: '3p925', 3.975: '3p975'}
POINTS: tuple[tuple[str, float], ...] = (('near_axis_x0_z30', 30.0), ('near_axis_x1_z30', 30.01666203960727), ('near_axis_x2_z30', 30.066592756745816), ('near_axis_x3_z30', 30.14962686336267), ('far_axis_x10_z30', 31.622776601683793), ('far_axis_x15_z30', 33.54101966249684), ('far_axis_x20_z30', 36.05551275463989), ('far_axis_x25_z30', 39.05124837953327))
TRANSITION_SEGMENTS: dict[
    tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]
] = {
    (0.325, 'odd'): (),
    (0.325, 'even'): (),
    (0.375, 'odd'): (),
    (0.375, 'even'): (),
    (0.825, 'odd'): (),
    (0.825, 'even'): (),
    (0.875, 'odd'): (),
    (0.875, 'even'): (),
    (0.925, 'odd'): (),
    (0.925, 'even'): (),
    (0.975, 'odd'): (),
    (0.975, 'even'): (),
    (1.525, 'odd'): (),
    (1.525, 'even'): (),
    (1.575, 'odd'): (),
    (1.575, 'even'): (),
    (1.625, 'odd'): (),
    (1.625, 'even'): (),
    (1.675, 'odd'): (),
    (1.675, 'even'): (),
    (1.7125, 'odd'): (),
    (1.7125, 'even'): (),
    (1.7375, 'odd'): (),
    (1.7375, 'even'): (),
    (2.7625, 'odd'): ((163, 163, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (164, 171, ('far_axis_x20_z30', 'far_axis_x25_z30')), (172, 181, ('far_axis_x25_z30',))),
    (2.7625, 'even'): ((163, 163, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (164, 171, ('far_axis_x20_z30', 'far_axis_x25_z30')), (172, 181, ('far_axis_x25_z30',))),
    (2.7875, 'odd'): ((164, 164, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 172, ('far_axis_x20_z30', 'far_axis_x25_z30')), (173, 183, ('far_axis_x25_z30',))),
    (2.7875, 'even'): ((164, 164, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 172, ('far_axis_x20_z30', 'far_axis_x25_z30')), (173, 183, ('far_axis_x25_z30',))),
    (2.825, 'odd'): ((164, 164, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 165, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (166, 174, ('far_axis_x20_z30', 'far_axis_x25_z30')), (175, 184, ('far_axis_x25_z30',))),
    (2.825, 'even'): ((164, 164, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 165, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (166, 174, ('far_axis_x20_z30', 'far_axis_x25_z30')), (175, 184, ('far_axis_x25_z30',))),
    (2.875, 'odd'): ((165, 167, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (168, 176, ('far_axis_x20_z30', 'far_axis_x25_z30')), (177, 187, ('far_axis_x25_z30',))),
    (2.875, 'even'): ((165, 167, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (168, 176, ('far_axis_x20_z30', 'far_axis_x25_z30')), (177, 187, ('far_axis_x25_z30',))),
    (2.925, 'odd'): ((165, 165, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (166, 169, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (170, 178, ('far_axis_x20_z30', 'far_axis_x25_z30')), (179, 189, ('far_axis_x25_z30',))),
    (2.925, 'even'): ((165, 165, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (166, 169, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (170, 178, ('far_axis_x20_z30', 'far_axis_x25_z30')), (179, 189, ('far_axis_x25_z30',))),
    (2.975, 'odd'): ((166, 166, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (167, 171, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (172, 181, ('far_axis_x20_z30', 'far_axis_x25_z30')), (182, 192, ('far_axis_x25_z30',))),
    (2.975, 'even'): ((166, 166, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (167, 171, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (172, 181, ('far_axis_x20_z30', 'far_axis_x25_z30')), (182, 192, ('far_axis_x25_z30',))),
    (3.7625, 'odd'): ((175, 188, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (189, 189, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 195, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (196, 204, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (205, 215, ('far_axis_x20_z30', 'far_axis_x25_z30')), (216, 229, ('far_axis_x25_z30',))),
    (3.7625, 'even'): ((175, 188, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (189, 189, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 195, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (196, 204, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (205, 215, ('far_axis_x20_z30', 'far_axis_x25_z30')), (216, 229, ('far_axis_x25_z30',))),
    (3.7875, 'odd'): ((175, 189, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 190, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (191, 196, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 205, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (206, 217, ('far_axis_x20_z30', 'far_axis_x25_z30')), (218, 230, ('far_axis_x25_z30',))),
    (3.7875, 'even'): ((175, 189, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 190, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (191, 196, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 205, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (206, 217, ('far_axis_x20_z30', 'far_axis_x25_z30')), (218, 230, ('far_axis_x25_z30',))),
    (3.825, 'odd'): ((176, 190, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (191, 191, ('near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (192, 198, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (199, 207, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (208, 218, ('far_axis_x20_z30', 'far_axis_x25_z30')), (219, 232, ('far_axis_x25_z30',))),
    (3.825, 'even'): ((176, 190, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (191, 191, ('near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (192, 198, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (199, 207, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (208, 218, ('far_axis_x20_z30', 'far_axis_x25_z30')), (219, 232, ('far_axis_x25_z30',))),
    (3.875, 'odd'): ((176, 192, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (193, 193, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (194, 200, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (201, 209, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (210, 220, ('far_axis_x20_z30', 'far_axis_x25_z30')), (221, 234, ('far_axis_x25_z30',))),
    (3.875, 'even'): ((176, 192, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (193, 193, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (194, 200, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (201, 209, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (210, 220, ('far_axis_x20_z30', 'far_axis_x25_z30')), (221, 234, ('far_axis_x25_z30',))),
    (3.925, 'odd'): ((177, 194, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (195, 195, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (196, 202, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (203, 211, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (212, 223, ('far_axis_x20_z30', 'far_axis_x25_z30')), (224, 236, ('far_axis_x25_z30',))),
    (3.925, 'even'): ((177, 194, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (195, 195, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (196, 202, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (203, 211, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (212, 223, ('far_axis_x20_z30', 'far_axis_x25_z30')), (224, 236, ('far_axis_x25_z30',))),
    (3.975, 'odd'): ((177, 196, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 197, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (198, 204, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (205, 213, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (214, 225, ('far_axis_x20_z30', 'far_axis_x25_z30')), (226, 239, ('far_axis_x25_z30',))),
    (3.975, 'even'): ((177, 196, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 197, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (198, 204, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (205, 213, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (214, 225, ('far_axis_x20_z30', 'far_axis_x25_z30')), (226, 239, ('far_axis_x25_z30',))),
}
SOURCE_HASHES: dict[str, str] = {'docs/prompts/phase5_t4ab_further_local_radial_gate.md': '2e6dbb5508d800442b0cfec9e89c5de4daacfe34abbd475963fabeae24727e3e', 'docs/superpowers/plans/2026-07-16-t4ab-further-local-radial-gate.md': '7812fe2062cd04d494c1ed427c2bf37bb036c8864ab4f0330b96ceb928c5ce0a', 'docs/superpowers/specs/2026-07-16-t4ab-t8aq-further-local-refinement-design.md': '88fa71a39606b9b37ea202a0e16d25af7a2e4597bce0c697df02c57a666c365b', 'scripts/phase5_further_local_radial_gate.py': 'b1efa83f5b6686c2c9d7e14264e5147f1710e2c2f5a0c7b218f01b60a6260e2c', 'src/schwgw/io/tablei.py': '0269df14235a841c2102928bc981e0d46c8115763bdb4e471ab5b86f34592b43', 'src/schwgw/numerics/experimental/q018_rescaled_oracle.py': 'cbaf3bcdb8000ff0965997b59e1be4c62e1112c3a35162e2aca52758db45589d', 'src/schwgw/numerics/radial_solver.py': '70f6bbed3266fdcf229af80b73a51416b8be056acf3d8ecbd73f4c86e73c997e'}
CLASSIFICATION_SNAPSHOT_SHA256: str = "52889944b58ec8aae442afb7c743679fcbbd9d3dd21819cc61cf1364b683eb43"
CLASSIFICATION_SHA256: str = "3bfe7d84a463e332d77724f58189fe3f565d9a385a4431f5a92ea58f15d11696"
ORACLE_VALIDATION_SHA256: str = "82ebed2447f7566a391ea1915c88ee3bf55f0c86b8c0207e2bd1eb2ca075d0c0"

__all__ = [
    "FREQUENCIES",
    "FREQUENCY_TOKENS",
    "POINTS",
    "TRANSITION_SEGMENTS",
    "SOURCE_HASHES",
    "CLASSIFICATION_SNAPSHOT_SHA256",
    "CLASSIFICATION_SHA256",
    "ORACLE_VALIDATION_SHA256",
]
