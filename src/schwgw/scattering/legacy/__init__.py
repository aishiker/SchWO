"""Isolated legacy and diagnostic scattering paths.

Nothing exported here is a Phase-6 production observable.
"""

from schwgw.scattering.legacy.adapter import (
    LEGACY_EVEN_CHANNEL,
    LEGACY_ODD_CHANNEL,
    LegacyIncidentSourceAdapter,
    LegacyScalarRWZAdapter,
)
from schwgw.scattering.legacy.np_pseudoinverse import (
    FULL_NP_PSEUDOINVERSE_BRIDGE_NAME,
    FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED,
    compute_packaged_polarization_scalars,
)

__all__ = [
    "LEGACY_EVEN_CHANNEL",
    "LEGACY_ODD_CHANNEL",
    "LegacyIncidentSourceAdapter",
    "LegacyScalarRWZAdapter",
    "FULL_NP_PSEUDOINVERSE_BRIDGE_NAME",
    "FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED",
    "compute_packaged_polarization_scalars",
]
