"""Generated immutable T4aa targeted-adaptive Q018 envelope."""

from __future__ import annotations

FREQUENCIES: tuple[float, ...] = (0.35, 0.45, 0.85, 0.95, 1.55, 1.65, 1.725, 2.775, 2.85, 2.95, 3.775, 3.85, 3.95)
FREQUENCY_TOKENS: dict[float, str] = {0.35: '0p35', 0.45: '0p45', 0.85: '0p85', 0.95: '0p95', 1.55: '1p55', 1.65: '1p65', 1.725: '1p725', 2.775: '2p775', 2.85: '2p85', 2.95: '2p95', 3.775: '3p775', 3.85: '3p85', 3.95: '3p95'}
POINTS: tuple[tuple[str, float], ...] = (('near_axis_x0_z30', 30.0), ('near_axis_x1_z30', 30.01666203960727), ('near_axis_x2_z30', 30.066592756745816), ('near_axis_x3_z30', 30.14962686336267), ('far_axis_x10_z30', 31.622776601683793), ('far_axis_x15_z30', 33.54101966249684), ('far_axis_x20_z30', 36.05551275463989), ('far_axis_x25_z30', 39.05124837953327))
TRANSITION_SEGMENTS: dict[
    tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]
] = {
    (0.35, 'odd'): (),
    (0.35, 'even'): (),
    (0.45, 'odd'): (),
    (0.45, 'even'): (),
    (0.85, 'odd'): (),
    (0.85, 'even'): (),
    (0.95, 'odd'): (),
    (0.95, 'even'): (),
    (1.55, 'odd'): (),
    (1.55, 'even'): (),
    (1.65, 'odd'): (),
    (1.65, 'even'): (),
    (1.725, 'odd'): (),
    (1.725, 'even'): (),
    (2.775, 'odd'): ((163, 163, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (164, 172, ('far_axis_x20_z30', 'far_axis_x25_z30')), (173, 182, ('far_axis_x25_z30',))),
    (2.775, 'even'): ((163, 163, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (164, 172, ('far_axis_x20_z30', 'far_axis_x25_z30')), (173, 182, ('far_axis_x25_z30',))),
    (2.85, 'odd'): ((164, 164, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 166, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (167, 175, ('far_axis_x20_z30', 'far_axis_x25_z30')), (176, 186, ('far_axis_x25_z30',))),
    (2.85, 'even'): ((164, 164, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 166, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (167, 175, ('far_axis_x20_z30', 'far_axis_x25_z30')), (176, 186, ('far_axis_x25_z30',))),
    (2.95, 'odd'): ((166, 170, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (171, 180, ('far_axis_x20_z30', 'far_axis_x25_z30')), (181, 190, ('far_axis_x25_z30',))),
    (2.95, 'even'): ((166, 170, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (171, 180, ('far_axis_x20_z30', 'far_axis_x25_z30')), (181, 190, ('far_axis_x25_z30',))),
    (3.775, 'odd'): ((175, 188, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (189, 189, ('near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 196, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 205, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (206, 216, ('far_axis_x20_z30', 'far_axis_x25_z30')), (217, 229, ('far_axis_x25_z30',))),
    (3.775, 'even'): ((175, 188, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (189, 189, ('near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 196, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 205, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (206, 216, ('far_axis_x20_z30', 'far_axis_x25_z30')), (217, 229, ('far_axis_x25_z30',))),
    (3.85, 'odd'): ((176, 191, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (192, 192, ('near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (193, 199, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (200, 208, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (209, 219, ('far_axis_x20_z30', 'far_axis_x25_z30')), (220, 233, ('far_axis_x25_z30',))),
    (3.85, 'even'): ((176, 191, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (192, 192, ('near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (193, 199, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (200, 208, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (209, 219, ('far_axis_x20_z30', 'far_axis_x25_z30')), (220, 233, ('far_axis_x25_z30',))),
    (3.95, 'odd'): ((177, 195, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (196, 196, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 203, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (204, 212, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (213, 224, ('far_axis_x20_z30', 'far_axis_x25_z30')), (225, 238, ('far_axis_x25_z30',))),
    (3.95, 'even'): ((177, 195, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (196, 196, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (197, 203, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (204, 212, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (213, 224, ('far_axis_x20_z30', 'far_axis_x25_z30')), (225, 238, ('far_axis_x25_z30',))),
}
SOURCE_HASHES: dict[str, str] = {'src/schwgw/numerics/radial_solver.py': '745ab7dc07a62ceb9923313eed155c0975fad95f1b52934b6f94bba2fdbd35d4', 'src/schwgw/numerics/experimental/q018_rescaled_oracle.py': 'cbaf3bcdb8000ff0965997b59e1be4c62e1112c3a35162e2aca52758db45589d', 'src/schwgw/io/tablei.py': '0269df14235a841c2102928bc981e0d46c8115763bdb4e471ab5b86f34592b43', 'scripts/phase5_targeted_adaptive_radial_gate.py': 'c1ea41c47e17647449c22a6cbd23fe4326a0bacd81f53d05fe70077a05fff32b', 'docs/superpowers/specs/2026-07-15-t4aa-t8ap-targeted-adaptive-refinement-design.md': '4227f655093b0a91ef7a1a770ed6471cced94302bdfac635cd9538da3773a71a', 'docs/superpowers/plans/2026-07-15-t4aa-targeted-adaptive-radial-gate.md': '0f2fa49bba95c2775f4383c225d09e2acd48f74eb6e72bfc77be3a80b5a30f56', 'docs/prompts/phase5_t4aa_targeted_adaptive_radial_gate.md': '93fbf16b0e5c913bb025c7fdb8535aea35b4efe421237bfef61b8d43a8cc4957'}
CLASSIFICATION_SNAPSHOT_SHA256: str = "f20ae61c736034138d0dadded4512c8f1e7afa95124e5dd16624930f1e404c40"
CLASSIFICATION_SHA256: str = "aa3af55cd8454d610ebcd31fd8bbda5d37522a9a4e2279c8622decf3459a1b83"
ORACLE_VALIDATION_SHA256: str = "002889f81ebce0574b948912217bf1231add3411253855db71adf2769b441d02"

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
