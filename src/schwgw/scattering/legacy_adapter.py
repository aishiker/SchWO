"""Compatibility import for the isolated legacy diagnostic namespace.

New code must import from :mod:`schwgw.scattering.legacy`.  This module is
retained so historical scripts and evidence readers remain import-compatible.
"""

from schwgw.scattering.legacy.adapter import (
    LEGACY_EVEN_CHANNEL,
    LEGACY_ODD_CHANNEL,
    LegacyIncidentSourceAdapter,
    LegacyScalarRWZAdapter,
)

__all__ = [
    "LEGACY_EVEN_CHANNEL",
    "LEGACY_ODD_CHANNEL",
    "LegacyIncidentSourceAdapter",
    "LegacyScalarRWZAdapter",
]
