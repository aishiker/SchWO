"""Explicit legacy namespace for the unvalidated NP pseudoinverse bridge.

The implementation remains in :mod:`schwgw.scattering.weyl` for historical
import compatibility.  Active diagnostic callers import it only through this
module so the legacy status is visible at the dependency boundary.
"""

from schwgw.scattering.weyl import (
    FULL_NP_PSEUDOINVERSE_BRIDGE_NAME,
    FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED,
    compute_packaged_polarization_scalars,
)

__all__ = [
    "FULL_NP_PSEUDOINVERSE_BRIDGE_NAME",
    "FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED",
    "compute_packaged_polarization_scalars",
]
