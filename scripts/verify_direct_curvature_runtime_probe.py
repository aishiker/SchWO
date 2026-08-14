#!/usr/bin/env python3
"""Emit one deterministic direct-curvature probe for runtime comparison."""

from __future__ import annotations

import json

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.direct_tablei import DenseRadialSpanCache
from schwgw.numerics import BoundaryConfig
from schwgw.scattering.metric_curvature import compute_metric_curvature_polarization


def main() -> int:
    radius = 20.0
    span = 2.0e-4 * radius
    cache = DenseRadialSpanCache(
        lower=radius - 2.0 * span,
        anchor=radius,
        upper=radius + 2.0 * span,
    )
    result = compute_metric_curvature_polarization(
        background=SchwarzschildBackground(M=1.0),
        k=0.5,
        r=radius,
        theta=0.7,
        phi=0.0,
        A_plus=0.9 + 1.1j,
        A_cross=0.4 + 0.6j,
        lmax=12,
        boundary_config=BoundaryConfig(
            r_out=100.0,
            rtol=1.0e-11,
            atol=1.0e-13,
        ),
        radial_solver=cache,
    )
    print(
        json.dumps(
            {
                "h_plus": [
                    result.polarization.h_plus.real,
                    result.polarization.h_plus.imag,
                ],
                "h_cross": [
                    result.polarization.h_cross.real,
                    result.polarization.h_cross.imag,
                ],
                "diagnostics": dict(result.polarization.diagnostics),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
