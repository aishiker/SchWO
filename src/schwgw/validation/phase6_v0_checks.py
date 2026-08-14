"""Trusted, frozen runners for the four Phase-6 V0 implementation checks.

No state or count is accepted from the caller.  Three checks evaluate a fixed
assertion inventory over bound source files; the fourth launches the exact
Python 3.14 pytest command and derives one assertion per JUnit testcase.
Every run creates one fresh immutable check-report root.
"""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import xml.etree.ElementTree as ET

from schwgw.validation.phase6_domain import canonical_json_bytes, source_file_identity
from schwgw.validation.phase6_v0_verification import (
    CHECK_REPORT_SCHEMA,
    FORMAL_FILE_MODE,
    FORMAL_ROOT_MODE,
    REQUIRED_CHECK_IDS,
    Phase6V0VerificationError,
    validate_check_report_payload,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PYTHON314 = Path("/opt/homebrew/bin/python3.14")
RUNNER_PATH = PROJECT_ROOT / "scripts/phase6_run_v0_check.py"
OVERLAY_ROOT = (
    PROJECT_ROOT / "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314"
)
CHECK_ROOT_SCHEMA = "schwgw_phase6_v1_v0_trusted_check_root_v1"

_STATIC_TARGETS = {
    "stale_production_metadata": (
        PROJECT_ROOT / "src/schwgw/scattering/metric_curvature.py",
        PROJECT_ROOT / "src/schwgw/validation/contracts.py",
    ),
    "legacy_np_isolation": (
        PROJECT_ROOT / "src/schwgw/scattering/partial_wave.py",
        PROJECT_ROOT / "src/schwgw/scattering/legacy/__init__.py",
        PROJECT_ROOT / "src/schwgw/scattering/legacy/np_pseudoinverse.py",
        PROJECT_ROOT / "src/schwgw/scattering/metric_curvature.py",
        PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py",
        PROJECT_ROOT / "src/schwgw/validation/phase6_conditioning_scan.py",
        PROJECT_ROOT / "src/schwgw/validation/phase6_production_finite_radius.py",
        PROJECT_ROOT / "scripts/phase6_run_conditioning_scan_shard.py",
        PROJECT_ROOT / "scripts/phase6_run_production_finite_radius_shard.py",
    ),
    "legacy_pseudoinverse_isolation": (
        PROJECT_ROOT / "src/schwgw/scattering/partial_wave.py",
        PROJECT_ROOT / "src/schwgw/scattering/legacy/np_pseudoinverse.py",
        PROJECT_ROOT / "src/schwgw/scattering/metric_curvature.py",
        PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py",
        PROJECT_ROOT / "src/schwgw/validation/phase6_conditioning_scan.py",
        PROJECT_ROOT / "src/schwgw/validation/phase6_production_finite_radius.py",
        PROJECT_ROOT / "scripts/phase6_run_conditioning_scan_shard.py",
        PROJECT_ROOT / "scripts/phase6_run_production_finite_radius_shard.py",
    ),
}
_PRODUCTION_TARGETS = frozenset(
    {
        PROJECT_ROOT / "src/schwgw/scattering/metric_curvature.py",
        PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py",
        PROJECT_ROOT / "src/schwgw/validation/phase6_conditioning_scan.py",
        PROJECT_ROOT / "src/schwgw/validation/phase6_production_finite_radius.py",
        PROJECT_ROOT / "scripts/phase6_run_conditioning_scan_shard.py",
        PROJECT_ROOT / "scripts/phase6_run_production_finite_radius_shard.py",
    }
)


class Phase6V0CheckError(Phase6V0VerificationError):
    """Raised for an unsafe runner, malformed JUnit, or root drift."""


def _assertion(assertion_id: str, passed: bool, detail: str) -> dict[str, str]:
    return {
        "assertion_id": assertion_id,
        "outcome": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def _source_identity(path: Path) -> dict[str, object]:
    absolute = path.absolute()
    if (
        not absolute.is_file()
        or absolute.is_symlink()
        or any(component.is_symlink() for component in absolute.parents)
    ):
        raise Phase6V0CheckError(f"bound V0 check source is missing: {absolute}")
    identity = source_file_identity(absolute)
    if identity["nlink"] != 1:
        raise Phase6V0CheckError(f"bound V0 check source is aliased: {absolute}")
    return identity


def _source_inventory(paths: Sequence[Path]) -> list[dict[str, object]]:
    unique = sorted(set(paths), key=lambda path: str(path))
    before = [_source_identity(path) for path in unique]
    after = [_source_identity(path) for path in unique]
    if before != after:
        raise Phase6V0CheckError("V0 check sources changed during identity capture")
    return before


def _tree(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        raise Phase6V0CheckError(f"cannot parse bound Python source: {path}") from exc


def _imports(path: Path) -> tuple[tuple[str, tuple[str, ...]], ...]:
    records: list[tuple[str, tuple[str, ...]]] = []
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            records.extend((alias.name, ()) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            records.append(
                (node.module or "", tuple(sorted(alias.name for alias in node.names)))
            )
    return tuple(sorted(records))


def _call_names(path: Path) -> tuple[str, ...]:
    def dotted(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = dotted(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    return tuple(
        sorted(
            name
            for node in ast.walk(_tree(path))
            if isinstance(node, ast.Call) and (name := dotted(node.func))
        )
    )


def _stale_metadata_assertions() -> list[dict[str, str]]:
    from schwgw.scattering.metric_curvature import (  # noqa: PLC0415
        compute_direct_metric_polarization,
    )
    from schwgw.validation.contracts import (  # noqa: PLC0415
        legacy_np_diagnostic_metadata,
    )

    metadata = getattr(
        compute_direct_metric_polarization, "__schwgw_bridge_metadata__", None
    )
    current = isinstance(metadata, Mapping)
    assertions = [
        _assertion(
            "stale_metadata.direct_bridge",
            current
            and metadata.get("polarization_bridge_validated") is True
            and metadata.get("production_backend") == "direct RW metric-curvature"
            and "pseudoinverse"
            not in str(metadata.get("polarization_bridge_implementation", "")).lower(),
            "production bridge metadata names the direct metric-curvature path and not the legacy pseudoinverse",
        ),
        _assertion(
            "stale_metadata.required_conventions",
            current
            and all(
                "required" in str(metadata.get(name, ""))
                for name in (
                    "observer_worldline",
                    "tetrad",
                    "phase_origin",
                    "axis_regularization",
                )
            ),
            "observer worldline, tetrad, phase origin, and axis regularization remain explicit required metadata",
        ),
    ]
    legacy = legacy_np_diagnostic_metadata()
    assertions.append(
        _assertion(
            "stale_metadata.legacy_claim_boundary",
            legacy.get("legacy_diagnostic") is True
            and legacy.get("production_observable") is False
            and legacy.get("physical_claim") is False
            and legacy.get("polarization_bridge_validated") is False,
            "legacy NP metadata is diagnostic-only and cannot claim a production observable",
        )
    )
    return assertions


def _legacy_np_assertions() -> list[dict[str, str]]:
    assertions: list[dict[str, str]] = []
    violations: list[str] = []
    for path in sorted(_PRODUCTION_TARGETS, key=str):
        for module, names in _imports(path):
            if module.startswith("schwgw.scattering.legacy") or {
                "compute_packaged_polarization_scalars",
                "FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED",
            } & set(names):
                violations.append(f"{path.relative_to(PROJECT_ROOT)}:{module}:{names}")
    assertions.append(
        _assertion(
            "legacy_np.production_import_boundary",
            not violations,
            "production targets have no legacy-NP imports"
            if not violations
            else f"forbidden production imports: {violations}",
        )
    )
    partial_wave = PROJECT_ROOT / "src/schwgw/scattering/partial_wave.py"
    imports = _imports(partial_wave)
    assertions.append(
        _assertion(
            "legacy_np.diagnostic_caller_boundary",
            any(
                module == "schwgw.scattering.legacy"
                and "compute_packaged_polarization_scalars" in names
                for module, names in imports
            )
            and not any(
                module == "schwgw.scattering.weyl"
                and "compute_packaged_polarization_scalars" in names
                for module, names in imports
            ),
            "the remaining partial-wave diagnostic imports the bridge only through schwgw.scattering.legacy",
        )
    )
    from schwgw.scattering.partial_wave import compute_polarization  # noqa: PLC0415

    metadata = getattr(compute_polarization, "__schwgw_bridge_metadata__", None)
    assertions.append(
        _assertion(
            "legacy_np.runtime_claim_boundary",
            isinstance(metadata, Mapping)
            and metadata.get("legacy_diagnostic") is True
            and metadata.get("production_observable") is False
            and metadata.get("physical_claim") is False,
            "the active legacy diagnostic caller carries fail-closed runtime claim metadata",
        )
    )
    return assertions


def _pseudoinverse_assertions() -> list[dict[str, str]]:
    violations = {
        str(path.relative_to(PROJECT_ROOT)): [
            name
            for name in _call_names(path)
            if name == "pinv" or name.endswith(".pinv")
        ]
        for path in sorted(_PRODUCTION_TARGETS, key=str)
    }
    violations = {path: names for path, names in violations.items() if names}
    conditioned = (
        PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py"
    ).read_text(encoding="utf-8")
    return [
        _assertion(
            "pseudoinverse.production_call_boundary",
            not violations,
            "production targets contain no pinv call"
            if not violations
            else f"production pseudoinverse calls: {violations}",
        ),
        _assertion(
            "pseudoinverse.generic_backend",
            "q018" not in conditioned.lower()
            and not any(
                name.endswith(".pinv")
                for name in _call_names(
                    PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py"
                )
            ),
            "the conditioned backend has neither a Q018 envelope nor a pseudoinverse call",
        ),
        _assertion(
            "pseudoinverse.legacy_facade",
            any(
                module == "schwgw.scattering.weyl"
                and "compute_packaged_polarization_scalars" in names
                for module, names in _imports(
                    PROJECT_ROOT / "src/schwgw/scattering/legacy/np_pseudoinverse.py"
                )
            ),
            "the retained unvalidated bridge is exposed through the explicit legacy facade",
        ),
    ]


_STATIC_ASSERTION_BUILDERS: dict[str, Callable[[], list[dict[str, str]]]] = {
    "stale_production_metadata": _stale_metadata_assertions,
    "legacy_np_isolation": _legacy_np_assertions,
    "legacy_pseudoinverse_isolation": _pseudoinverse_assertions,
}


def _runner_command(check_id: str, output_root: Path) -> list[str]:
    return [
        str(PYTHON314),
        str(RUNNER_PATH),
        "--check-id",
        check_id,
        "--output-root",
        str(output_root),
    ]


def _counts(assertions: Sequence[Mapping[str, str]]) -> dict[str, int]:
    outcomes = Counter(assertion["outcome"] for assertion in assertions)
    return {
        "passed": outcomes["PASS"],
        "failed": outcomes["FAIL"],
        "skipped": outcomes["SKIP"],
    }


def _report_payload(
    *,
    check_id: str,
    output_root: Path,
    assertions: Sequence[Mapping[str, str]],
    source_identities: Sequence[Mapping[str, object]],
    command_argv: Sequence[str] | None = None,
) -> dict[str, object]:
    ordered = sorted(
        (dict(assertion) for assertion in assertions),
        key=lambda item: item["assertion_id"],
    )
    counts = _counts(ordered)
    report = {
        "schema": CHECK_REPORT_SCHEMA,
        "check_id": check_id,
        "command_argv": list(command_argv or _runner_command(check_id, output_root)),
        "working_directory": str(PROJECT_ROOT),
        "exit_status": 1 if counts["failed"] else 0,
        "assertions": ordered,
        "counts": counts,
        "source_identities": sorted(
            (dict(identity) for identity in source_identities),
            key=lambda identity: str(identity["path"]),
        ),
        "execution_complete": True,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
    }
    validate_check_report_payload(
        report,
        report_path=output_root / "check_report.json",
        expected_check_id=check_id,
        verify_sources=True,
    )
    return report


def _junit_assertions(
    path: Path, *, pytest_argv: Sequence[str], returncode: int
) -> list[dict[str, str]]:
    assertions: list[dict[str, str]] = []
    try:
        root = ET.parse(path).getroot()
        testcases = list(root.iter("testcase"))
    except (OSError, ET.ParseError) as exc:
        testcases = []
        assertions.append(
            _assertion(
                "full_test_suite.junit_parse",
                False,
                f"JUnit output missing/malformed for {list(pytest_argv)}: {type(exc).__name__}: {exc}",
            )
        )
    for index, testcase in enumerate(testcases):
        label = f"{testcase.get('classname', '')}::{testcase.get('name', '')}"
        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")
        outcome = (
            "FAIL"
            if failure is not None or error is not None
            else ("SKIP" if skipped is not None else "PASS")
        )
        token = hashlib.sha256(f"{index}:{label}".encode()).hexdigest()[:32]
        assertions.append(
            {
                "assertion_id": f"full_test_suite.test.{token}",
                "outcome": outcome,
                "detail": f"JUnit testcase {label}: {outcome}",
            }
        )
    if not testcases and not assertions:
        assertions.append(
            _assertion(
                "full_test_suite.nonempty",
                False,
                f"pytest produced no JUnit testcases: {list(pytest_argv)}",
            )
        )
    if returncode != 0 and not any(item["outcome"] == "FAIL" for item in assertions):
        assertions.append(
            _assertion(
                "full_test_suite.pytest_exit",
                False,
                f"pytest exited {returncode} without a failing JUnit testcase: {list(pytest_argv)}",
            )
        )
    if returncode == 0 and any(item["outcome"] == "FAIL" for item in assertions):
        assertions.append(
            _assertion(
                "full_test_suite.exit_junit_consistency",
                False,
                "pytest returned zero but JUnit or its parser reported a failure",
            )
        )
    return assertions


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _new_root(path: Path) -> Path:
    root = path.absolute()
    if any(component.is_symlink() for component in (root.parent, *root.parent.parents)):
        raise Phase6V0CheckError("V0 check output parent contains a symlink")
    try:
        normalized = root.parent.resolve(strict=True) / root.name
    except OSError as exc:
        raise Phase6V0CheckError("V0 check output parent is unavailable") from exc
    if root != normalized or root.exists() or root.is_symlink():
        raise Phase6V0CheckError("V0 check output root must be fresh and direct")
    os.mkdir(root, 0o700)
    _fsync_directory(root.parent)
    return root


def _publish_file(path: Path, data: bytes) -> dict[str, object]:
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
    _fsync_directory(path.parent)
    if path.read_bytes() != data:
        raise Phase6V0CheckError("V0 check artifact changed on readback")
    return _source_identity(path)


def _seal_root(root: Path) -> None:
    if not root.exists() or root.is_symlink():
        return
    for child in root.iterdir():
        if child.is_file() and not child.is_symlink():
            os.chmod(child, FORMAL_FILE_MODE)
    os.chmod(root, FORMAL_ROOT_MODE)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def _static_check(
    check_id: str, root: Path
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    paths = (
        PROJECT_ROOT / "src/schwgw/validation/phase6_v0_checks.py",
        RUNNER_PATH,
        *_STATIC_TARGETS[check_id],
    )
    before = _source_inventory(paths)
    assertions = _STATIC_ASSERTION_BUILDERS[check_id]()
    after = _source_inventory(paths)
    if before != after:
        assertions.append(
            _assertion(
                f"{check_id}.temporal_source_identity",
                False,
                "bound source identity changed during the trusted check",
            )
        )
    return assertions, before


def _full_suite_check(
    root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, object]], list[str]]:
    junit_path = root / "junit.xml"
    pytest_argv = [
        str(PYTHON314),
        "-m",
        "pytest",
        "-q",
        f"--junitxml={junit_path}",
    ]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = f"{OVERLAY_ROOT}:{PROJECT_ROOT / 'src'}"
    result = subprocess.run(
        pytest_argv,
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout = (
        result.stdout
        if isinstance(result.stdout, bytes)
        else str(result.stdout).encode()
    )
    stderr = (
        result.stderr
        if isinstance(result.stderr, bytes)
        else str(result.stderr).encode()
    )
    stdout_identity = _publish_file(root / "pytest.stdout.txt", stdout)
    stderr_identity = _publish_file(root / "pytest.stderr.txt", stderr)
    identities = [stdout_identity, stderr_identity]
    if junit_path.is_file() and not junit_path.is_symlink():
        os.chmod(junit_path, FORMAL_FILE_MODE)
        identities.append(_source_identity(junit_path))
    assertions = _junit_assertions(
        junit_path,
        pytest_argv=pytest_argv,
        returncode=result.returncode,
    )
    identities.extend(
        _source_inventory(
            (
                PROJECT_ROOT / "pyproject.toml",
                PROJECT_ROOT / "src/schwgw/validation/phase6_v0_checks.py",
                RUNNER_PATH,
            )
        )
    )
    return (
        assertions,
        sorted(identities, key=lambda identity: str(identity["path"])),
        pytest_argv,
    )


def validate_published_check_root(
    root: str | Path,
    *,
    expected_check_id: str,
) -> dict[str, object]:
    """Reload one trusted check root and rederive its exact state."""

    if expected_check_id not in REQUIRED_CHECK_IDS:
        raise Phase6V0CheckError("unknown V0 check id")
    path = Path(root).absolute()
    if any(component.is_symlink() for component in (path, *path.parents)):
        raise Phase6V0CheckError("V0 check root contains an alias")
    try:
        resolved = path.resolve(strict=True)
        root_info = path.lstat()
    except OSError as exc:
        raise Phase6V0CheckError("V0 check root is unavailable") from exc
    names = {child.name for child in path.iterdir()}
    allowed = {"check_report.json"}
    if expected_check_id == "full_test_suite":
        allowed |= {"pytest.stdout.txt", "pytest.stderr.txt"}
        if "junit.xml" in names:
            allowed.add("junit.xml")
    if (
        resolved != path
        or not stat.S_ISDIR(root_info.st_mode)
        or stat.S_IMODE(root_info.st_mode) != FORMAL_ROOT_MODE
        or names != allowed
    ):
        raise Phase6V0CheckError("V0 check root layout/mode changed")
    for child in path.iterdir():
        info = child.lstat()
        if (
            child.is_symlink()
            or not stat.S_ISREG(info.st_mode)
            or stat.S_IMODE(info.st_mode) != FORMAL_FILE_MODE
            or info.st_nlink != 1
        ):
            raise Phase6V0CheckError("V0 check artifact is mutable/aliased")
    report_path = path / "check_report.json"
    raw = report_path.read_bytes()
    try:
        report = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6V0CheckError("V0 check report is not JSON") from exc
    if not isinstance(report, Mapping) or canonical_json_bytes(report) != raw:
        raise Phase6V0CheckError("V0 check report is not canonical JSON")
    try:
        state, _, passed, failed, skipped = validate_check_report_payload(
            report,
            report_path=report_path,
            expected_check_id=expected_check_id,
            verify_sources=True,
        )
    except Phase6V0VerificationError as exc:
        raise Phase6V0CheckError(str(exc)) from exc
    identity = _source_identity(report_path)
    return {
        "schema": CHECK_ROOT_SCHEMA,
        "check_id": expected_check_id,
        "state": state,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "report_path": str(report_path),
        "report_sha256": identity["sha256"],
        "evidence_root": str(path),
        "global_green_permitted": False,
    }


def run_v0_check(check_id: str, output_root: str | Path) -> dict[str, object]:
    """Execute one frozen check and publish a fresh immutable report root."""

    if check_id not in REQUIRED_CHECK_IDS:
        raise Phase6V0CheckError("unknown V0 check id")
    root = _new_root(Path(output_root))
    try:
        if check_id == "full_test_suite":
            assertions, identities, command_argv = _full_suite_check(root)
        else:
            assertions, identities = _static_check(check_id, root)
            command_argv = _runner_command(check_id, root)
        report = _report_payload(
            check_id=check_id,
            output_root=root,
            assertions=assertions,
            source_identities=identities,
            command_argv=command_argv,
        )
        _publish_file(root / "check_report.json", canonical_json_bytes(report))
        _seal_root(root)
        return validate_published_check_root(root, expected_check_id=check_id)
    except BaseException:
        _seal_root(root)
        raise


__all__ = [
    "CHECK_ROOT_SCHEMA",
    "OVERLAY_ROOT",
    "PROJECT_ROOT",
    "PYTHON314",
    "Phase6V0CheckError",
    "RUNNER_PATH",
    "run_v0_check",
    "validate_published_check_root",
]
