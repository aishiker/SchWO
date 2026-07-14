"""Generated immutable T4z Delta0p1 risk-pilot Q018 envelope."""

from __future__ import annotations

FREQUENCIES: tuple[float, ...] = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
POINTS: tuple[tuple[str, float], ...] = (('near_axis_x0_z30', 30.0), ('near_axis_x1_z30', 30.01666203960727), ('near_axis_x2_z30', 30.066592756745816), ('near_axis_x3_z30', 30.14962686336267), ('far_axis_x10_z30', 31.622776601683793), ('far_axis_x15_z30', 33.54101966249684), ('far_axis_x20_z30', 36.05551275463989), ('far_axis_x25_z30', 39.05124837953327))
TRANSITION_SEGMENTS: dict[
    float, tuple[tuple[int, int, tuple[str, ...]], ...]
] = {
    0.4: (),
    0.8: (),
    0.9: (),
    1.6: (),
    1.7: (),
    2.8: ((164, 164, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (165, 173, ('far_axis_x20_z30', 'far_axis_x25_z30')), (174, 183, ('far_axis_x25_z30',))),
    2.9: ((165, 165, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (166, 168, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (169, 177, ('far_axis_x20_z30', 'far_axis_x25_z30')), (178, 188, ('far_axis_x25_z30',))),
    3.8: ((175, 189, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (190, 190, ('near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (191, 197, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (198, 206, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (207, 217, ('far_axis_x20_z30', 'far_axis_x25_z30')), (218, 231, ('far_axis_x25_z30',))),
    3.9: ((176, 193, ('near_axis_x0_z30', 'near_axis_x1_z30', 'near_axis_x2_z30', 'near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (194, 194, ('near_axis_x3_z30', 'far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (195, 201, ('far_axis_x10_z30', 'far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (202, 210, ('far_axis_x15_z30', 'far_axis_x20_z30', 'far_axis_x25_z30')), (211, 221, ('far_axis_x20_z30', 'far_axis_x25_z30')), (222, 235, ('far_axis_x25_z30',))),
}
CLASSIFICATION_SHA256: str = "ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54"
ORACLE_VALIDATION_SHA256: str = "8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9"

__all__ = [
    "FREQUENCIES",
    "POINTS",
    "TRANSITION_SEGMENTS",
    "CLASSIFICATION_SHA256",
    "ORACLE_VALIDATION_SHA256",
]
