"""Shared image-plane geometry for Li--Hou--Zhao figure overlays."""

from __future__ import annotations

import math


EVENT_HORIZON_RADIUS_OVER_M = 2.0

# The paper's gray image-plane disk follows the Schwarzschild critical curve.
# Its screen radius is the critical impact parameter b_c = 3 sqrt(3) M.  This
# is distinct from the Schwarzschild-coordinate photon-sphere radius r = 3 M.
LIGHT_RING_IMAGE_RADIUS_OVER_M = 3.0 * math.sqrt(3.0)


__all__ = [
    "EVENT_HORIZON_RADIUS_OVER_M",
    "LIGHT_RING_IMAGE_RADIUS_OVER_M",
]
