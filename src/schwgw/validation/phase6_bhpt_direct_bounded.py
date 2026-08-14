"""Bounded, resumable Phase-6 BHPT direct-integration validation.

The first external-direct attempt requested 800 decimal digits from an upstream
boundary-condition routine whose stopping test is ``10**(-WorkingPrecision)``.
It also wrote only after all 30 keys completed.  This revision keeps the exact
upstream commit, applies one auditable and paper-independent boundary overlay,
and runs every key/precision node in a separate Wolfram kernel process.

The overlay changes only the two upstream infinity radii from ``100/|k|`` to
``max(300, 8 sqrt(ell(ell+1))/|k|)``.  The factor is a turning-radius margin,
not a paper-mode envelope.  It keeps the upstream 100-term asymptotic series in
its decreasing/minimal-term regime for the frozen 30-key calibration domain.
Odd and even sectors remain independent Regge--Wheeler and Zerilli solves.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time

from schwgw.validation.phase6_bhpt_direct import (
    BHPTDirectContractError,
    EXPECTED_SOURCE_SHA256,
    canonical_json_bytes,
    sha256_file,
    validate_execution_contract,
    validate_source_snapshot,
)
from schwgw.validation.phase6_execution_contract import (
    external_direct_calibration_keys,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
NODE_WLS_PATH = PROJECT_ROOT / "scripts" / "phase6_bhpt_direct_bounded_node.wls"
RUNNER_PATH = PROJECT_ROOT / "scripts" / "phase6_run_bhpt_direct_bounded.py"

PLAN_SCHEMA = "schwgw_phase6_bhpt_direct_bounded_plan_v1"
NODE_SCHEMA = "schwgw_phase6_bhpt_direct_bounded_node_v1"
KEY_RESULT_SCHEMA = "schwgw_phase6_bhpt_direct_bounded_key_result_v1"
SUMMARY_SCHEMA = "schwgw_phase6_bhpt_direct_bounded_summary_v1"
MANIFEST_SCHEMA = "schwgw_phase6_bhpt_direct_bounded_manifest_v1"

FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444
EXPECTED_KEY_COUNT = 30
OUTER_RADIUS_FLOOR_M = Decimal("300")
TURNING_MARGIN = Decimal("8")
NODE_TIMEOUT_SECONDS = 900.0

ORIGINAL_OUTER_LINE = b"rout =100*Abs[\\[Omega]]^-1;"
OVERLAY_OUTER_LINE = b"rout = Max[300, 8 Sqrt[l (l + 1)]/Abs[\\[Omega]]];"
EXPECTED_OUTER_REPLACEMENTS = 2

PRECISION_NODES = (
    ("wp40", 40, 20, 20, 30),
    ("wp60", 60, 30, 30, 40),
)
NUMERICAL_THRESHOLDS = {
    "precision_relative_complex_S": Decimal("1e-15"),
    "precision_log_abs_transmission": Decimal("1e-12"),
    "precision_wrapped_phase_transmission_rad": Decimal("1e-12"),
    "matching_radius_complex_S_spread": Decimal("1e-15"),
    "flux_unitarity_residual": Decimal("1e-15"),
}


class BHPTBoundedDirectError(ValueError):
    """Raised when source identity, a numerical node, or evidence drifts."""


@dataclass(frozen=True)
class DecimalComplex:
    real: Decimal
    imag: Decimal

    def __sub__(self, other: "DecimalComplex") -> "DecimalComplex":
        return DecimalComplex(self.real - other.real, self.imag - other.imag)

    def scale(self, factor: Decimal | int) -> "DecimalComplex":
        value = Decimal(factor)
        return DecimalComplex(self.real * value, self.imag * value)

    def absolute(self) -> Decimal:
        with localcontext() as context:
            context.prec = 100
            return (self.real * self.real + self.imag * self.imag).sqrt()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decimal(value: object, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise BHPTBoundedDirectError(f"{label} is not numeric")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise BHPTBoundedDirectError(f"{label} is not decimal") from exc
    if not result.is_finite():
        raise BHPTBoundedDirectError(f"{label} is not finite")
    return result


def _complex(value: object, label: str) -> DecimalComplex:
    if not isinstance(value, Mapping) or set(value) != {"real", "imag"}:
        raise BHPTBoundedDirectError(f"{label} complex schema changed")
    return DecimalComplex(
        _decimal(value["real"], f"{label}.real"),
        _decimal(value["imag"], f"{label}.imag"),
    )


def _complex_record(value: DecimalComplex) -> dict[str, str]:
    return {"imag": str(value.imag), "real": str(value.real)}


def _relative_complex(left: DecimalComplex, right: DecimalComplex) -> Decimal:
    return (left - right).absolute() / max(
        Decimal(1), left.absolute(), right.absolute()
    )


def _phase(value: DecimalComplex) -> float:
    scale = max(abs(value.real), abs(value.imag))
    if scale == 0:
        raise BHPTBoundedDirectError("phase of zero complex value is undefined")
    return math.atan2(float(value.imag / scale), float(value.real / scale))


def _wrapped_phase_difference(left: DecimalComplex, right: DecimalComplex) -> Decimal:
    return Decimal(str(abs(math.remainder(_phase(left) - _phase(right), 2 * math.pi))))


def _log_abs_difference(left: DecimalComplex, right: DecimalComplex) -> Decimal:
    left_abs, right_abs = left.absolute(), right.absolute()
    if left_abs == 0 or right_abs == 0:
        raise BHPTBoundedDirectError("transmission magnitude vanished exactly")
    with localcontext() as context:
        context.prec = 100
        return abs(left_abs.ln() - right_abs.ln())


def _file_identity(path: Path, *, formal: bool = False) -> dict[str, object]:
    absolute = path.absolute()
    try:
        info = absolute.lstat()
    except OSError as exc:
        raise BHPTBoundedDirectError(f"missing file: {absolute}") from exc
    required_mode = FORMAL_FILE_MODE if formal else None
    if (
        absolute.is_symlink()
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or (required_mode is not None and stat.S_IMODE(info.st_mode) != required_mode)
    ):
        raise BHPTBoundedDirectError(f"invalid regular-file identity: {absolute}")
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": sha256_file(absolute),
        "size": info.st_size,
    }


def _exclusive_json(path: Path, payload: object) -> dict[str, object]:
    data = canonical_json_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(path, FORMAL_FILE_MODE)
    return _file_identity(path, formal=True)


def _read_json(path: Path, *, formal: bool = False) -> Mapping[str, object]:
    if formal:
        _file_identity(path, formal=True)
    try:
        payload = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BHPTBoundedDirectError(f"invalid JSON: {path}") from exc
    if not isinstance(payload, Mapping):
        raise BHPTBoundedDirectError(f"JSON artifact is not an object: {path}")
    if formal and path.read_bytes() != canonical_json_bytes(payload):
        raise BHPTBoundedDirectError(f"formal JSON is not canonical: {path}")
    return payload


def _overlay_bytes(upstream_bytes: bytes) -> bytes:
    if (
        _sha256_bytes(upstream_bytes)
        != EXPECTED_SOURCE_SHA256["Kernel/NumericalIntegration.m"]
    ):
        raise BHPTBoundedDirectError("upstream NumericalIntegration hash changed")
    if upstream_bytes.count(ORIGINAL_OUTER_LINE) != EXPECTED_OUTER_REPLACEMENTS:
        raise BHPTBoundedDirectError("upstream outer-radius statements changed")
    transformed = upstream_bytes.replace(ORIGINAL_OUTER_LINE, OVERLAY_OUTER_LINE)
    if (
        transformed.count(OVERLAY_OUTER_LINE) != EXPECTED_OUTER_REPLACEMENTS
        or ORIGINAL_OUTER_LINE in transformed
    ):
        raise BHPTBoundedDirectError("adaptive outer-radius overlay failed")
    return transformed


def build_runtime_overlay(upstream_root: Path, destination: Path) -> dict[str, object]:
    """Create one deterministic temporary paclet overlay from the exact checkout."""

    source = upstream_root.resolve(strict=True)
    if destination.exists() or destination.is_symlink():
        raise BHPTBoundedDirectError("overlay destination must be absent")
    shutil.copytree(source, destination, symlinks=False)
    numerical = destination / "Kernel" / "NumericalIntegration.m"
    transformed = _overlay_bytes(
        (source / "Kernel" / "NumericalIntegration.m").read_bytes()
    )
    numerical.write_bytes(transformed)
    return {
        "algorithm": (
            "replace both upstream r_out=100/abs(k) statements with "
            "max(300,8*sqrt(ell*(ell+1))/abs(k))"
        ),
        "changed_file": "Kernel/NumericalIntegration.m",
        "changed_file_sha256": _sha256_bytes(transformed),
        "original_file_sha256": EXPECTED_SOURCE_SHA256["Kernel/NumericalIntegration.m"],
        "replacement_count": EXPECTED_OUTER_REPLACEMENTS,
        "unchanged_upstream_commit": source_snapshot_commit(source),
    }


def source_snapshot_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise BHPTBoundedDirectError("cannot read overlay source commit")
    return result.stdout.strip()


def _expected_outer_radius(key: Mapping[str, object]) -> Decimal:
    ell = int(key["ell"])
    k = Decimal(str(key["kM"]))
    with localcontext() as context:
        context.prec = 80
        turning = Decimal(ell * (ell + 1)).sqrt() / k
        return max(OUTER_RADIUS_FLOOR_M, TURNING_MARGIN * turning)


def validate_node(
    payload: object,
    *,
    expected_key: Mapping[str, object],
    precision_node: tuple[str, int, int, int, int],
    overlay_sha256: str,
) -> dict[str, object]:
    """Strictly validate one raw Wolfram node and its scattering identities."""

    expected_fields = {
        "schema",
        "key",
        "potential",
        "method",
        "boundary_conditions_solved",
        "parity_derived_even_used",
        "precision",
        "outer_boundary_radius_M",
        "match_records",
        "selected_match_index",
        "phase_factor",
        "reflection_ratio",
        "transmission",
        "matching_radius_phase_spread_abs",
        "selected_flux_unitarity_residual_abs",
        "solver_elapsed_seconds",
        "runtime",
        "loaded_numerical_integration",
        "global_green_permitted",
    }
    if not isinstance(payload, Mapping) or set(payload) != expected_fields:
        raise BHPTBoundedDirectError("bounded BHPT node schema changed")
    if payload["schema"] != NODE_SCHEMA or payload["key"] != dict(expected_key):
        raise BHPTBoundedDirectError("bounded BHPT node identity changed")
    sector, ell = str(expected_key["sector"]), int(expected_key["ell"])
    expected_potential = "ReggeWheeler" if sector == "odd" else "Zerilli"
    if (
        payload["potential"] != expected_potential
        or payload["method"] != "NumericalIntegration"
        or payload["boundary_conditions_solved"] != ["In", "Up"]
        or payload["parity_derived_even_used"] is not False
        or payload["selected_match_index"] != 1
        or payload["global_green_permitted"] is not False
    ):
        raise BHPTBoundedDirectError("bounded BHPT method/parity contract changed")
    _, wp, pg, ag, digits = precision_node
    if payload["precision"] != {
        "accuracy_goal_decimal_digits": ag,
        "precision_goal_decimal_digits": pg,
        "serialized_output_digits": digits,
        "working_precision_decimal_digits": wp,
    }:
        raise BHPTBoundedDirectError("bounded BHPT precision node changed")
    loaded = payload["loaded_numerical_integration"]
    if (
        not isinstance(loaded, Mapping)
        or loaded.get("sha256") != overlay_sha256
        or not str(loaded.get("path", "")).endswith("/Kernel/NumericalIntegration.m")
    ):
        raise BHPTBoundedDirectError("Wolfram did not prove the overlay source")
    outer = _decimal(payload["outer_boundary_radius_M"], "outer radius")
    expected_outer = _expected_outer_radius(expected_key)
    if abs(outer - expected_outer) > Decimal("1e-25") * max(Decimal(1), expected_outer):
        raise BHPTBoundedDirectError("adaptive outer radius changed")

    records = payload["match_records"]
    if not isinstance(records, list) or len(records) != 3:
        raise BHPTBoundedDirectError("match-radius ladder changed")
    phase_values: list[DecimalComplex] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise BHPTBoundedDirectError("match record is not an object")
        expected_match_fields = {
            "basis_wronskian_abs",
            "flux_unitarity_residual_abs",
            "fraction",
            "incidence",
            "phase_factor",
            "radius_M",
            "reflection",
            "reflection_ratio",
            "transmission",
        }
        if set(record) != expected_match_fields:
            raise BHPTBoundedDirectError("match record schema changed")
        if record["fraction"] != ("0.8", "0.88", "0.96")[index]:
            raise BHPTBoundedDirectError("match fraction changed")
        if _decimal(record["basis_wronskian_abs"], "basis Wronskian") <= 0:
            raise BHPTBoundedDirectError("basis Wronskian is not positive")
        reflection_ratio = _complex(record["reflection_ratio"], "reflection ratio")
        phase_factor = _complex(record["phase_factor"], "phase factor")
        expected_phase = reflection_ratio.scale(-1 if ell % 2 == 0 else 1)
        if _relative_complex(phase_factor, expected_phase) > Decimal("1e-25"):
            raise BHPTBoundedDirectError("phase-factor algebra changed")
        transmission = _complex(record["transmission"], "transmission")
        serialized_flux = _decimal(
            record["flux_unitarity_residual_abs"], "serialized flux residual"
        )
        recomputed_flux = abs(
            reflection_ratio.absolute() ** 2 + transmission.absolute() ** 2 - 1
        )
        if abs(serialized_flux - recomputed_flux) > Decimal("2e-25"):
            raise BHPTBoundedDirectError("match-record flux algebra changed")
        phase_values.append(phase_factor)
    selected_phase = _complex(payload["phase_factor"], "selected phase factor")
    selected_reflection = _complex(
        payload["reflection_ratio"], "selected reflection ratio"
    )
    selected_transmission = _complex(payload["transmission"], "selected transmission")
    if (
        _relative_complex(selected_phase, phase_values[1]) > Decimal("1e-25")
        or _relative_complex(
            selected_reflection,
            _complex(records[1]["reflection_ratio"], "selected reflection record"),
        )
        > Decimal("1e-25")
        or _relative_complex(
            selected_transmission,
            _complex(records[1]["transmission"], "selected transmission record"),
        )
        > Decimal("1e-25")
    ):
        raise BHPTBoundedDirectError("selected match record changed")
    spread = max((value - phase_values[1]).absolute() for value in phase_values)
    if abs(
        spread - _decimal(payload["matching_radius_phase_spread_abs"], "phase spread")
    ) > Decimal("2e-25"):
        raise BHPTBoundedDirectError("matching-radius spread algebra changed")
    _decimal(payload["solver_elapsed_seconds"], "solver elapsed seconds")
    return dict(payload)


def compare_precision_nodes(
    low: Mapping[str, object], high: Mapping[str, object]
) -> dict[str, object]:
    low_s, high_s = (
        _complex(low["phase_factor"], "low S"),
        _complex(high["phase_factor"], "high S"),
    )
    low_t, high_t = (
        _complex(low["transmission"], "low T"),
        _complex(high["transmission"], "high T"),
    )
    estimates = {
        "flux_unitarity_residual": _decimal(
            high["selected_flux_unitarity_residual_abs"], "high flux"
        ),
        "matching_radius_complex_S_spread": _decimal(
            high["matching_radius_phase_spread_abs"], "high match spread"
        ),
        "precision_log_abs_transmission": _log_abs_difference(low_t, high_t),
        "precision_relative_complex_S": _relative_complex(low_s, high_s),
        "precision_wrapped_phase_transmission_rad": _wrapped_phase_difference(
            low_t, high_t
        ),
    }
    checks = {
        name: {
            "estimate": str(estimate),
            "state": "PASS" if estimate <= NUMERICAL_THRESHOLDS[name] else "FAIL",
            "threshold": str(NUMERICAL_THRESHOLDS[name]),
        }
        for name, estimate in estimates.items()
    }
    overall = (
        "PASS" if all(item["state"] == "PASS" for item in checks.values()) else "FAIL"
    )
    return {
        "checks": checks,
        "high_precision_phase_factor": _complex_record(high_s),
        "high_precision_transmission": _complex_record(high_t),
        "overall_state": overall,
    }


def _node_filename(ordinal: int, key: Mapping[str, object], node_id: str) -> str:
    km = str(key["kM"]).replace(".", "p")
    return (
        f"node_{ordinal:02d}__kM_{km}__{key['sector']}__"
        f"ell_{int(key['ell']):04d}__{node_id}.json"
    )


def _result_filename(ordinal: int, key: Mapping[str, object]) -> str:
    km = str(key["kM"]).replace(".", "p")
    return (
        f"result_{ordinal:02d}__kM_{km}__{key['sector']}__"
        f"ell_{int(key['ell']):04d}.json"
    )


def _resolve_kernel(value: str | Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        resolved = shutil.which(str(value))
        if resolved is None:
            raise BHPTBoundedDirectError("WolframKernel executable was not found")
        candidate = Path(resolved)
    candidate = candidate.resolve(strict=True)
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise BHPTBoundedDirectError("WolframKernel is not executable")
    return candidate


def _plan(
    *,
    upstream_root: Path,
    source: Mapping[str, object],
    execution: Mapping[str, object],
) -> dict[str, object]:
    original = (upstream_root / "Kernel" / "NumericalIntegration.m").read_bytes()
    overlay = _overlay_bytes(original)
    return {
        "acceptance_scope": "FROZEN_SELECTED_30_KEY_EXTERNAL_DIRECT_CALIBRATION",
        "backend": {
            "boundary_conditions_solved": ["In", "Up"],
            "even_is_independent_zerilli_solve": True,
            "internal_solver_fallback_permitted": False,
            "method": "BlackHolePerturbationToolkit ReggeWheelerRadial NumericalIntegration",
            "parity_derived_even_used": False,
        },
        "domain": {
            "count": EXPECTED_KEY_COUNT,
            "records": [key.to_record() for key in external_direct_calibration_keys()],
        },
        "execution_contract": dict(execution),
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "numerical_thresholds": {
            key: str(value) for key, value in NUMERICAL_THRESHOLDS.items()
        },
        "outer_boundary_overlay": {
            "changed_file": "Kernel/NumericalIntegration.m",
            "changed_file_sha256": _sha256_bytes(overlay),
            "formula": "max(300M,8*sqrt(ell*(ell+1))/k)",
            "original_file_sha256": _sha256_bytes(original),
            "replacement_count": EXPECTED_OUTER_REPLACEMENTS,
            "role": "generic turning-radius/Jost-order applicability repair",
        },
        "precision_nodes": [
            {
                "accuracy_goal_decimal_digits": ag,
                "node_id": node_id,
                "precision_goal_decimal_digits": pg,
                "serialized_output_digits": digits,
                "working_precision_decimal_digits": wp,
            }
            for node_id, wp, pg, ag, digits in PRECISION_NODES
        ],
        "producer_sources": {
            "node_wls": _file_identity(NODE_WLS_PATH),
            "runner": _file_identity(RUNNER_PATH),
            "validation_module": _file_identity(Path(__file__)),
        },
        "schema": PLAN_SCHEMA,
        "toolkit_source": dict(source),
    }


def run_bounded_direct_campaign(
    *,
    output_root: str | Path,
    package_root: str | Path,
    wolfram_kernel: str | Path,
    timeout_seconds: float = NODE_TIMEOUT_SECONDS,
    limit: int | None = None,
) -> int:
    """Run and seal a fresh selected-domain campaign; no node is retried."""

    if timeout_seconds <= 0:
        raise BHPTBoundedDirectError("timeout_seconds must be positive")
    root = Path(output_root).absolute()
    if root.exists() or root.is_symlink():
        raise BHPTBoundedDirectError("output_root must be fresh and absent")
    upstream_root = Path(package_root).resolve(strict=True)
    try:
        source = validate_source_snapshot(upstream_root)
        execution = validate_execution_contract(PROJECT_ROOT)
    except BHPTDirectContractError as exc:
        raise BHPTBoundedDirectError(str(exc)) from exc
    kernel = _resolve_kernel(wolfram_kernel)
    keys = [key.to_record() for key in external_direct_calibration_keys()]
    if limit is not None:
        if limit < 1 or limit > EXPECTED_KEY_COUNT:
            raise BHPTBoundedDirectError("limit must lie in [1,30]")
        keys = keys[:limit]
    root.mkdir(parents=True, mode=0o700)
    os.chmod(root, 0o700)
    plan = _plan(upstream_root=upstream_root, source=source, execution=execution)
    plan["execution_limit"] = limit
    _exclusive_json(root / "plan.json", plan)
    overlay_sha = str(plan["outer_boundary_overlay"]["changed_file_sha256"])
    started = time.monotonic()
    key_results: list[dict[str, object]] = []
    node_failures: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="schwo_bhpt_bounded_overlay_") as temp:
        overlay_root = Path(temp) / "ReggeWheeler"
        overlay_record = build_runtime_overlay(upstream_root, overlay_root)
        if overlay_record["changed_file_sha256"] != overlay_sha:
            raise BHPTBoundedDirectError("runtime overlay hash changed")
        numerical_source = overlay_root / "Kernel" / "NumericalIntegration.m"
        for ordinal, key in enumerate(keys):
            nodes: dict[str, dict[str, object]] = {}
            for precision_node in PRECISION_NODES:
                node_id, wp, pg, ag, digits = precision_node
                raw_path = Path(temp) / f"raw_{ordinal}_{node_id}.json"
                environment = os.environ.copy()
                environment.update(
                    {
                        "SCHWO_BHPT_BOUNDED_AG": str(ag),
                        "SCHWO_BHPT_BOUNDED_DIGITS": str(digits),
                        "SCHWO_BHPT_BOUNDED_ELL": str(key["ell"]),
                        "SCHWO_BHPT_BOUNDED_KM": str(key["kM"]),
                        "SCHWO_BHPT_BOUNDED_NUMERICAL_SHA256": overlay_sha,
                        "SCHWO_BHPT_BOUNDED_NUMERICAL_SOURCE": str(numerical_source),
                        "SCHWO_BHPT_BOUNDED_OUTPUT": str(raw_path),
                        "SCHWO_BHPT_BOUNDED_PACKAGE_ROOT": str(overlay_root),
                        "SCHWO_BHPT_BOUNDED_PG": str(pg),
                        "SCHWO_BHPT_BOUNDED_SECTOR": str(key["sector"]),
                        "SCHWO_BHPT_BOUNDED_WP": str(wp),
                    }
                )
                try:
                    completed = subprocess.run(
                        [str(kernel), "-noprompt", "-script", str(NODE_WLS_PATH)],
                        cwd=PROJECT_ROOT,
                        env=environment,
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=timeout_seconds,
                    )
                    if completed.returncode != 0 or not raw_path.is_file():
                        raise BHPTBoundedDirectError(
                            f"Wolfram node exited {completed.returncode}: "
                            f"{completed.stdout[-500:]} {completed.stderr[-500:]}"
                        )
                    node = validate_node(
                        _read_json(raw_path),
                        expected_key=key,
                        precision_node=precision_node,
                        overlay_sha256=overlay_sha,
                    )
                    node["node_id"] = node_id
                    node["ordinal"] = ordinal
                    filename = _node_filename(ordinal, key, node_id)
                    _exclusive_json(root / filename, node)
                    nodes[node_id] = node
                except (
                    subprocess.TimeoutExpired,
                    OSError,
                    BHPTBoundedDirectError,
                ) as exc:
                    failure = {
                        "error": f"{type(exc).__name__}: {exc}",
                        "key": dict(key),
                        "node_id": node_id,
                        "ordinal": ordinal,
                        "status": "FAIL_CLOSED",
                    }
                    node_failures.append(failure)
                    _exclusive_json(
                        root / f"failure_{ordinal:02d}__{node_id}.json", failure
                    )
                    break
            if len(nodes) == len(PRECISION_NODES):
                comparison = compare_precision_nodes(nodes["wp40"], nodes["wp60"])
                result = {
                    "convention_uncertainty_budget": {
                        "absolute_phase_origin": "r_star=r+2*log(r/2-1), M=1",
                        "fourier_convention": "exp(-i*k*t)",
                        "phase_or_normalization_fit": False,
                        "scattering_definition": "S=-A_out/[(-1)^ell A_in]",
                        "state": "FROZEN_NOT_YET_CROSS_BACKEND_ACCEPTED",
                    },
                    "key": dict(key),
                    "node_files": [
                        _node_filename(ordinal, key, node_id)
                        for node_id, *_ in PRECISION_NODES
                    ],
                    "numerical_uncertainty_budget": comparison,
                    "ordinal": ordinal,
                    "overall_state": comparison["overall_state"],
                    "schema": KEY_RESULT_SCHEMA,
                }
                _exclusive_json(root / _result_filename(ordinal, key), result)
                key_results.append(result)

    pass_count = sum(result["overall_state"] == "PASS" for result in key_results)
    fail_count = len(keys) - pass_count
    overall = (
        "PASS"
        if fail_count == 0 and len(keys) == EXPECTED_KEY_COUNT
        else "PARTIAL"
        if fail_count == 0
        else "FAIL"
    )
    summary = {
        "acceptance_scope": "selected 30-key external direct calibration only",
        "completed_key_count": len(key_results),
        "elapsed_seconds": time.monotonic() - started,
        "even_is_independent_zerilli_solve": True,
        "execution_limit": limit,
        "failed_key_count": fail_count,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "node_failure_count": len(node_failures),
        "numerical_pass_key_count": pass_count,
        "overall_state": overall,
        "parity_derived_even_used": False,
        "record_count": len(keys),
        "schema": SUMMARY_SCHEMA,
        "scientific_acceptance": (
            "SELECTED_DOMAIN_NUMERICAL_PASS_PENDING_CROSS_BACKEND"
            if overall == "PASS"
            else "NOT_ACCEPTED"
        ),
    }
    _exclusive_json(root / "summary.json", summary)
    artifact_names = sorted(
        path.name
        for path in root.iterdir()
        if path.is_file() and path.name != "manifest.json"
    )
    manifest = {
        "artifacts": {
            name: _file_identity(root / name, formal=True) for name in artifact_names
        },
        "global_green_permitted": False,
        "overall_state": overall,
        "schema": MANIFEST_SCHEMA,
        "summary_sha256": sha256_file(root / "summary.json"),
    }
    _exclusive_json(root / "manifest.json", manifest)
    os.chmod(root, FORMAL_ROOT_MODE)
    validate_published_bounded_direct(root)
    return 0 if overall in {"PASS", "PARTIAL"} else 2


def validate_published_bounded_direct(root_path: str | Path) -> dict[str, object]:
    """Strictly reload one sealed bounded-direct root and every formal artifact."""

    root = Path(root_path).absolute()
    info = root.lstat()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_ROOT_MODE
    ):
        raise BHPTBoundedDirectError("bounded-direct root is not direct immutable 0555")
    manifest = _read_json(root / "manifest.json", formal=True)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BHPTBoundedDirectError("bounded-direct manifest schema changed")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise BHPTBoundedDirectError("bounded-direct manifest ledger is missing")
    actual_names = {path.name for path in root.iterdir() if path.is_file()}
    if actual_names != {*artifacts, "manifest.json"}:
        raise BHPTBoundedDirectError("bounded-direct artifact inventory changed")
    for name, expected in artifacts.items():
        actual = _file_identity(root / str(name), formal=True)
        if actual != expected:
            raise BHPTBoundedDirectError(f"artifact identity changed: {name}")
    plan = _read_json(root / "plan.json", formal=True)
    summary = _read_json(root / "summary.json", formal=True)
    if plan.get("schema") != PLAN_SCHEMA or summary.get("schema") != SUMMARY_SCHEMA:
        raise BHPTBoundedDirectError("bounded-direct plan/summary schema changed")
    if manifest.get("summary_sha256") != sha256_file(root / "summary.json"):
        raise BHPTBoundedDirectError("bounded-direct summary linkage changed")
    if summary.get("global_green_permitted") is not False:
        raise BHPTBoundedDirectError("bounded-direct global claim changed")
    return dict(summary)


__all__ = [
    "BHPTBoundedDirectError",
    "KEY_RESULT_SCHEMA",
    "MANIFEST_SCHEMA",
    "NODE_SCHEMA",
    "PLAN_SCHEMA",
    "PRECISION_NODES",
    "SUMMARY_SCHEMA",
    "build_runtime_overlay",
    "compare_precision_nodes",
    "run_bounded_direct_campaign",
    "validate_node",
    "validate_published_bounded_direct",
]
