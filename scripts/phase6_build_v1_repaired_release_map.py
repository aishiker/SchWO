#!/usr/bin/env python3
"""Build the post-repair Phase-6 V1 release map from immutable evidence.

The map deliberately omits superseded failure roots from the current release
snapshot.  Those roots remain immutable historical diagnostics.  Scientific
states are still derived by the release preparation validators; this builder
only selects terminal roots, binds their bytes, and declares exact scopes.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path

from schwgw.validation.phase6_domain import canonical_json_bytes, source_file_identity
from schwgw.validation.phase6_release_preparation import (
    POLICY,
    RELEASE_MAP_SCHEMA,
    Phase6PreparationError,
    preflight_release_map,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLD_MAP = PROJECT_ROOT / "configs/phase6_v1_release_map_20260809.json"
FINAL_BASELINE_ROOT = (
    PROJECT_ROOT
    / "runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314"
)
SELECTED_ACCEPTANCE_ROOT = (
    PROJECT_ROOT
    / "runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314"
)
AP_SELECTED_ROOT = (
    PROJECT_ROOT
    / "runs/phase6/radial_validation/v1_ap_selected_evidence_v1_20260810_py314"
)
PRODUCTION_STATE_ROOT = (
    PROJECT_ROOT
    / "runs/phase6/radial_validation/v1_production_state_evidence_v2_20260810_py314"
)
V0_VERIFICATION_ROOT = PROJECT_ROOT / "runs/phase6/v1_v0_verification_v2_20260810_py314"

RETAINED_CERTIFICATE_IDS = frozenset(
    {
        "cert_v1_bhpt_mst_odd_selected_84",
        "cert_v2_master_to_strain_flux_selected_2",
        "cert_v2_metric_psi4_external_selected_2",
        "cert_v3_spin2_scattering_limits_selected_3",
        "cert_v4_finite_radius_tidal_detector_selected_2",
        "cert_v5_complex_lensing_matrix_selected_2",
        "cert_v6_release_uncertainty_policy",
    }
)


def _load_json(
    path: Path, *, require_domain_canonical_bytes: bool
) -> dict[str, object]:
    """Load JSON while respecting the producing schema's byte convention.

    Phase-6 domain/release maps use compact canonical JSON, whereas several
    independently validated numerical producers use stable indented JSON.
    Native evidence validators remain responsible for the latter byte format;
    this builder must not silently impose the domain-map serializer on them.
    """

    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6PreparationError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise Phase6PreparationError(f"JSON root is not an object: {path}")
    if require_domain_canonical_bytes and canonical_json_bytes(value) != raw:
        raise Phase6PreparationError(f"noncanonical domain/release JSON: {path}")
    return value


def _source(
    *,
    evidence_id: str,
    adapter: str,
    root: Path,
    filenames: tuple[str, ...],
    selector: dict[str, object] | None = None,
) -> dict[str, object]:
    absolute = root.absolute()
    artifacts = []
    for filename in sorted(filenames):
        identity = source_file_identity(absolute / filename)
        artifacts.append({"relative_path": filename, "sha256": identity["sha256"]})
    return {
        "adapter": adapter,
        "evidence_id": evidence_id,
        "expected_artifacts": artifacts,
        "origin_root": str(absolute),
        "selector": selector or {},
    }


def _report_domain(report: dict[str, object]) -> dict[str, object]:
    raw = report.get("parameter_domain")
    if not isinstance(raw, dict):
        raise Phase6PreparationError("typed report parameter domain is missing")
    domain = deepcopy(raw)
    expected_ids = domain.pop("expected_item_ids", None)
    if not isinstance(expected_ids, list) or len(expected_ids) != domain.get(
        "expected_items"
    ):
        raise Phase6PreparationError("typed report expected-item inventory changed")
    return domain


def _certificate(
    *,
    certificate_id: str,
    evidence_id: str,
    gate: str,
    observable: str,
    domain: dict[str, object],
    primary_acceptance_gate: str,
) -> dict[str, object]:
    return {
        "certificate_id": certificate_id,
        "evidence_ids": [evidence_id],
        "gate": gate,
        "observable": observable,
        "parameter_domain": domain,
        "primary_acceptance_gate": primary_acceptance_gate,
    }


def build_repaired_release_map() -> dict[str, object]:
    old = _load_json(OLD_MAP, require_domain_canonical_bytes=True)
    old_certificates = {
        str(item["certificate_id"]): deepcopy(item)
        for item in old.get("certificates", [])
        if isinstance(item, dict)
    }
    retained_certificates = [
        old_certificates[certificate_id]
        for certificate_id in sorted(RETAINED_CERTIFICATE_IDS)
    ]
    retained_evidence_ids = {
        str(evidence_id)
        for certificate in retained_certificates
        for evidence_id in certificate["evidence_ids"]
    }
    retained_sources = [
        deepcopy(source)
        for source in old.get("sources", [])
        if isinstance(source, dict)
        and str(source.get("evidence_id")) in retained_evidence_ids
    ]
    if {str(source["evidence_id"]) for source in retained_sources} != (
        retained_evidence_ids
    ):
        raise Phase6PreparationError("retained release evidence inventory changed")
    v0_certificate = deepcopy(old_certificates["cert_v0_final_verification"])
    v0_certificate["evidence_ids"] = ["v0_final_verification_repaired"]

    selected_report = _load_json(
        SELECTED_ACCEPTANCE_ROOT / "report.json",
        require_domain_canonical_bytes=False,
    )
    final_report = _load_json(
        FINAL_BASELINE_ROOT / "report.json",
        require_domain_canonical_bytes=False,
    )
    ap_report = _load_json(
        AP_SELECTED_ROOT / "report.json",
        require_domain_canonical_bytes=False,
    )
    production_report = _load_json(
        PRODUCTION_STATE_ROOT / "report.json",
        require_domain_canonical_bytes=False,
    )

    new_sources = [
        _source(
            evidence_id="v0_final_verification_repaired",
            adapter="V0_IMPLEMENTATION_VERIFICATION_V1",
            root=V0_VERIFICATION_ROOT,
            filenames=("verification.json",),
        ),
        _source(
            evidence_id="v1_ap_selected_24",
            adapter="V1_AP_SELECTED_EVIDENCE_V1",
            root=AP_SELECTED_ROOT,
            filenames=("manifest.json", "report.json", "source_ledger.json"),
        ),
        _source(
            evidence_id="v1_final_turning_d_union_17818",
            adapter="V1_FINAL_RADIAL_BASELINE_V2",
            root=FINAL_BASELINE_ROOT,
            filenames=("manifest.json", "report.json", "summary.json"),
            selector={"projection": "radial_s_matrix_flux"},
        ),
        _source(
            evidence_id="v1_production_states_repaired_16048",
            adapter="V1_PRODUCTION_STATE_EVIDENCE_V1",
            root=PRODUCTION_STATE_ROOT,
            filenames=("manifest.json", "report.json", "source_ledger.json"),
            selector={"projection": "radial_s_matrix_flux"},
        ),
        _source(
            evidence_id="v1_selected_bhpt_direct_30",
            adapter="V1_RADIAL_SELECTED_ACCEPTANCE_V1",
            root=SELECTED_ACCEPTANCE_ROOT,
            filenames=("manifest.json", "report.json", "summary.json"),
        ),
        _source(
            evidence_id="v1q_final_turning_d_union_17818",
            adapter="V1_FINAL_RADIAL_BASELINE_V2",
            root=FINAL_BASELINE_ROOT,
            filenames=("manifest.json", "report.json", "summary.json"),
            selector={"projection": "generic_conditioning_backend"},
        ),
        _source(
            evidence_id="v1q_production_backend_repaired_16048",
            adapter="V1_PRODUCTION_STATE_EVIDENCE_V1",
            root=PRODUCTION_STATE_ROOT,
            filenames=("manifest.json", "report.json", "source_ledger.json"),
            selector={"projection": "generic_conditioning_backend"},
        ),
    ]

    q018_domain = _report_domain(production_report)
    q018_domain.update(
        {
            "description": (
                "exact repaired D_prod generic-backend radial-state coverage; "
                "independent full-domain backend comparison remains open"
            ),
            "domain_id": "production_d_prod_backend_repaired_16048",
            "selection_policy": (
                "exact frozen D_prod original 12666 plus generic scaled-tortoise "
                "repair 3382; no domain extrapolation"
            ),
        }
    )
    q018_union_domain = _report_domain(final_report)
    q018_union_domain.update(
        {
            "description": (
                "exact frozen D_union unified turning-aware generic backend; "
                "independent full-domain backend comparison remains open"
            ),
            "domain_id": "final_turning_aware_d_union_backend_17818",
            "selection_policy": (
                "exact ordered D_union through one generic turning-proxy and "
                "Jost-quality policy; no named-mode envelope"
            ),
        }
    )
    new_certificates = [
        v0_certificate,
        _certificate(
            certificate_id="cert_v1_ap_selected_24",
            evidence_id="v1_ap_selected_24",
            gate="V1",
            observable="radial_s_matrix_flux",
            domain=_report_domain(ap_report),
            primary_acceptance_gate=(
                "independent arbitrary-precision and step-size ladders on the "
                "frozen selected domain"
            ),
        ),
        _certificate(
            certificate_id="cert_v1_final_turning_d_union_17818",
            evidence_id="v1_final_turning_d_union_17818",
            gate="V1",
            observable="radial_s_matrix_flux",
            domain=_report_domain(final_report),
            primary_acceptance_gate=(
                "turning-aware finite, flux, Jost-quality, and legacy-isolation "
                "invariants over exact D_union"
            ),
        ),
        _certificate(
            certificate_id="cert_v1_production_states_repaired_16048",
            evidence_id="v1_production_states_repaired_16048",
            gate="V1",
            observable="radial_s_matrix_flux",
            domain=_report_domain(production_report),
            primary_acceptance_gate=(
                "exact eight-radius radial master-state coverage over frozen D_prod"
            ),
        ),
        _certificate(
            certificate_id="cert_v1_selected_bhpt_direct_30",
            evidence_id="v1_selected_bhpt_direct_30",
            gate="V1",
            observable="radial_s_matrix_flux",
            domain=_report_domain(selected_report),
            primary_acceptance_gate=(
                "external direct Regge-Wheeler and Zerilli amplitudes plus frozen "
                "boundary and precision ladders"
            ),
        ),
        _certificate(
            certificate_id="cert_v1q_final_turning_d_union_17818",
            evidence_id="v1q_final_turning_d_union_17818",
            gate="V1Q",
            observable="generic_conditioning_backend",
            domain=q018_union_domain,
            primary_acceptance_gate=(
                "one generic turning-aware backend and frozen Jost-quality "
                "invariants over exact D_union"
            ),
        ),
        _certificate(
            certificate_id="cert_v1q_production_backend_repaired_16048",
            evidence_id="v1q_production_backend_repaired_16048",
            gate="V1Q",
            observable="generic_conditioning_backend",
            domain=q018_domain,
            primary_acceptance_gate=(
                "generic non-envelope backend availability and exact production "
                "radial-state coverage"
            ),
        ),
    ]
    sources = sorted(
        [*retained_sources, *new_sources], key=lambda item: str(item["evidence_id"])
    )
    certificates = sorted(
        [*retained_certificates, *new_certificates],
        key=lambda item: str(item["certificate_id"]),
    )
    return {
        "certificates": certificates,
        "policy": deepcopy(POLICY),
        "preparation_id": "phase6_v1_preparation_repaired_v2_20260810",
        "release_id": "phase6_v1_release_repaired_v2_20260810",
        "schema": RELEASE_MAP_SCHEMA,
        "sources": sources,
    }


def _publish(path: Path, payload: dict[str, object]) -> None:
    absolute = path.absolute()
    if absolute.exists() or absolute.is_symlink():
        raise Phase6PreparationError("repaired release-map target must be absent")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(absolute, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(canonical_json_bytes(payload))
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(absolute, 0o444)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-only", action="store_true")
    action.add_argument("--output", type=Path)
    args = parser.parse_args()
    release_map = build_repaired_release_map()
    preflight = preflight_release_map(release_map)
    if args.output is not None:
        _publish(args.output, release_map)
    print(json.dumps(preflight, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
