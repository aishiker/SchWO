"""Frozen T4ac literal failed-child radial/Q018 gate.

The numerical kernel and atomic-checkpoint machinery are reused from the
reviewed T4ab runner.  This module freezes a distinct contract, source
identity, output root, and final-adapter identity for the exact 41-frequency
T4ac package.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import phase5_further_local_radial_gate as _base
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.perturbations import Sector


SCHEMA_VERSION = "phase5_t4ac_literal_failed_child_radial_gate_v1"
CHECKPOINT_SCHEMA_VERSION = (
    "phase5_t4ac_literal_failed_child_radial_checkpoint_v1"
)
PREFLIGHT_SCHEMA_VERSION = (
    "phase5_t4ac_literal_failed_child_radial_preflight_v1"
)
FREQUENCIES = (
    0.3125, 0.3375, 0.3625, 0.3875,
    0.8625, 0.9125, 0.9375, 0.9625, 0.9875,
    1.5125, 1.5375, 1.5625, 1.5875, 1.6125, 1.6375, 1.6625,
    1.6875, 1.70625, 1.71875,
    2.78125, 2.79375, 2.8125, 2.8375, 2.8625, 2.8875, 2.9125,
    2.9375, 2.9625, 2.9875,
    3.75625, 3.76875, 3.78125, 3.79375, 3.8125, 3.8375, 3.8625,
    3.8875, 3.9125, 3.9375, 3.9625, 3.9875,
)
FREQUENCY_TOKENS = {k: str(k).replace(".", "p") for k in FREQUENCIES}
LMAX_VALUES = {
    0.3125: (24, 36, 60, 84), 0.3375: (24, 36, 60, 84),
    0.3625: (24, 36, 60, 84), 0.3875: (24, 36, 60, 84),
    0.8625: (24, 36, 60, 84), 0.9125: (24, 36, 60, 84),
    0.9375: (24, 48, 72, 96), 0.9625: (24, 48, 72, 96),
    0.9875: (24, 48, 72, 96),
    1.5125: (72, 96, 120, 144), 1.5375: (72, 96, 120, 144),
    1.5625: (72, 96, 120, 144), 1.5875: (72, 96, 120, 144),
    1.6125: (84, 108, 132, 156), 1.6375: (84, 108, 132, 156),
    1.6625: (84, 108, 132, 156), 1.6875: (84, 108, 132, 156),
    1.70625: (84, 108, 132, 156), 1.71875: (84, 108, 132, 156),
    2.78125: (180, 204, 228, 252), 2.79375: (180, 204, 228, 252),
    2.8125: (192, 216, 240, 264), 2.8375: (192, 216, 240, 264),
    2.8625: (192, 216, 240, 264), 2.8875: (192, 216, 240, 264),
    2.9125: (192, 216, 240, 264), 2.9375: (204, 228, 252, 276),
    2.9625: (204, 228, 252, 276), 2.9875: (204, 228, 252, 276),
    3.75625: (276, 300, 324, 348), 3.76875: (276, 300, 324, 348),
    3.78125: (276, 300, 324, 348), 3.79375: (276, 300, 324, 348),
    3.8125: (276, 300, 324, 348), 3.8375: (276, 300, 324, 348),
    3.8625: (276, 300, 324, 348), 3.8875: (288, 312, 336, 360),
    3.9125: (288, 312, 336, 360), 3.9375: (288, 312, 336, 360),
    3.9625: (288, 312, 336, 360), 3.9875: (288, 312, 336, 360),
}
EXPECTED_RECORD_COUNT = 146_416
CLASSIFICATION_PARENT = "f3a64522642abfaa2e0f3933125df06ae76895e4"
CLASSIFICATION_PARENT_PARENT = "fa22f20f775c1b15ae533c03047d156687e5f3bf"
CLASSIFICATION_RADIAL_BLOB = "12a3bd178499548c4b3ad338266eb20c46271595"
T8AQ_COMMIT = "c34268b6977d9e4e228f0bcc29b628390bd1b1bb"
T8AQ_PARENT = "c3a6479703f6c2d64aa2903edc7cf2db3d1ed112"
T8AQ_GENERATION_CONTRACT = (
    "a43ab0769a73768723505b2bee0715646e215624cc5b5efd880d97bcfff778f1"
)
T8AQ_METADATA_CONTRACT = (
    "ff4210c449dfedb5b37228f76e9d91d71488935c7c5064c40b1ddefb961e8d96"
)

OUTPUT_DIR = Path("runs/phase5/fig5_fig6_literal_failed_child_radial_gate")
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoint"
CLASSIFICATION_PATH = OUTPUT_DIR / "classification_manifest.json"
ORACLE_PATH = OUTPUT_DIR / "oracle_validation.json"
PREFLIGHT_PATH = OUTPUT_DIR / "resume_preflight.json"
MANIFEST_PATH = OUTPUT_DIR / "manifest.md"
ENVELOPE_PATH = Path(
    "src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py"
)
ADAPTER_NAME = "q018_tablei_literal_failed_child_transition"
ADAPTER_SOLVER = "q018_tablei_literal_failed_child_transition_oracle"
ADAPTER_WARNING = "q018_tablei_literal_failed_child_transition_oracle_used"

CLASSIFICATION_SOURCE_PATHS = (
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("src/schwgw/numerics/experimental/q018_rescaled_oracle.py"),
    Path("src/schwgw/io/tablei.py"),
    Path("scripts/phase5_further_local_radial_gate.py"),
    Path("scripts/phase5_literal_failed_child_radial_gate.py"),
    Path(
        "docs/superpowers/specs/"
        "2026-07-18-t4ac-t8ar-literal-failed-child-refinement-design.md"
    ),
    Path(
        "docs/superpowers/plans/"
        "2026-07-18-t4ac-literal-failed-child-radial-gate.md"
    ),
    Path("docs/prompts/phase5_t4ac_literal_failed_child_radial_gate.md"),
)
FROZEN_INPUT_HASHES = {
    Path("runs/phase5/fig5_fig6_further_local_refinement/checkpoint_ledger.json"):
        "7b63e0689a01e32e27397007a3e458c800e2802bdd72c3f582a6e8a6bec4ae72",
    Path("runs/phase5/fig5_fig6_further_local_refinement/further_local_values.npz"):
        "27c263e8cb4b3270fe3103a9d79617a345a383a636da0ab3af4f954432fdf50b",
    Path("runs/phase5/fig5_fig6_further_local_refinement/further_local_values.npz.json"):
        "df30e1f3cb3d17f87bc8f62470a87d5bca2e6819543fe9430b5c48a1d9552a8e",
    Path("runs/phase5/fig5_fig6_further_local_refinement/further_local_sampling_audit.json"):
        "a5f5e9d91d1b932fbec307244d35ebee688cfecaf2b11a54672b7eb2d33a2395",
    Path("runs/phase5/fig5_fig6_further_local_refinement/manifest.md"):
        "f84d6a1fb2cee35d2a00e81756110d2b75b99edca2946e79e2f70362f7350f3c",
    Path("runs/phase5/fig5_fig6_further_local_radial_gate/classification_manifest.json"):
        "3bfe7d84a463e332d77724f58189fe3f565d9a385a4431f5a92ea58f15d11696",
    Path("runs/phase5/fig5_fig6_further_local_radial_gate/oracle_validation.json"):
        "82ebed2447f7566a391ea1915c88ee3bf55f0c86b8c0207e2bd1eb2ca075d0c0",
    Path("runs/phase5/fig5_fig6_further_local_radial_gate/resume_preflight.json"):
        "8fdabdbd1bc4765d1ee5155824df1ba88b154c58e14058d68129d58ec36a1021",
    Path("runs/phase5/fig5_fig6_further_local_radial_gate/manifest.md"):
        "ef479476d683366654c3c2209aba817fa8ca35a68bbf86782a39e88ce9a60bc0",
    Path("docs/handoffs/T7_current.md"):
        "57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01",
    Path("docs/handoffs/archive/T7_2026-07-16_pre_t7cb_further_local_review.md"):
        "f7b46bf1e04bb5fdbe75ad522ec9673ca9df30d317fa0356cdd29295d80a91ef",
    Path("docs/superpowers/specs/2026-07-16-t4ab-t8aq-further-local-refinement-design.md"):
        "88fa71a39606b9b37ea202a0e16d25af7a2e4597bce0c697df02c57a666c365b",
    Path("docs/superpowers/plans/2026-07-16-t4ab-further-local-radial-gate.md"):
        "7812fe2062cd04d494c1ed427c2bf37bb036c8864ab4f0330b96ceb928c5ce0a",
    Path("docs/superpowers/plans/2026-07-16-t8aq-further-local-refinement.md"):
        "56891ef34f168a05e43806d7177ca721c10180483224c75ef95df5a1e118b56b",
    Path("docs/prompts/phase5_t4ab_further_local_radial_gate.md"):
        "2e6dbb5508d800442b0cfec9e89c5de4daacfe34abbd475963fabeae24727e3e",
    Path("docs/prompts/phase5_t7ca_further_local_radial_review.md"):
        "132e6ec9cca4d91fbcef38d1354ee0e9028f2d30de73e308b8acb1ed1571cb85",
    Path("docs/prompts/phase5_t8aq_further_local_refinement.md"):
        "ad34bc2338fadcc51685b499910ff13a4ecda5f7567af186f0d39bc99f33f354",
    Path("docs/prompts/phase5_t7cb_further_local_refinement_review.md"):
        "99f03928c2b3e51d2cd30614d6401fb4da81375a99fa08bf330fdb2d4459e10b",
    Path("docs/superpowers/specs/2026-07-18-t4ac-t8ar-literal-failed-child-refinement-design.md"):
        "0052af7360e06f5218360839a50e21b6d154cfc98dffd526328c43d962f58b58",
    Path("docs/superpowers/plans/2026-07-18-t4ac-literal-failed-child-radial-gate.md"):
        "824594ad257f39d7e56d738837b16ceb8cde081bf12acba5e294fcaad594a75d",
    Path("docs/superpowers/plans/2026-07-18-t8ar-literal-failed-child-refinement.md"):
        "972c74186364a3506001616b4f8fe8deb1563a1a1f44548b89bd96f08bd6ef7c",
    Path("docs/prompts/phase5_t4ac_literal_failed_child_radial_gate.md"):
        "9189e68169774cfdf9abe6afee31c81ef95c30cc15269c7d9a8ede76d77ee655",
    Path("docs/prompts/phase5_t7cc_literal_failed_child_radial_review.md"):
        "4a8097a3b8728b290139596e4611440a3de34a1a26c4503c3c38c074c462a3b7",
    Path("docs/prompts/phase5_t8ar_literal_failed_child_refinement.md"):
        "dcdb2849111475cd2dbe45371607bc96181ca4abcadcf27d28f2cf20dc9fb242",
    Path("docs/prompts/phase5_t7cd_literal_failed_child_refinement_review.md"):
        "0e9fcb766e722aa15f59544e5997eb81f861f2c2375f861389604a944b9395ed",
}
IMPLEMENTATION_PATHS = (
    Path("scripts/phase5_literal_failed_child_radial_gate.py"),
    Path("src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py"),
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("tests/physics/test_q018_production_integration_design.py"),
    Path("tests/physics/test_radial_solver.py"),
)

_ORIGINAL_GLOBAL_CONTRACT = _base._global_contract
_ORIGINAL_AGGREGATE = _base._aggregate
_ORIGINAL_FINAL_ADAPTER_SNAPSHOT = _base._final_adapter_snapshot
_ORIGINAL_RUN_PREFLIGHT = _base._run_preflight


def _git_text(*args: str) -> str:
    return subprocess.run(
        ("git", *args), check=True, capture_output=True, text=True
    ).stdout.strip()


def _verify_frozen_inputs() -> dict[str, str]:
    actual = {str(path): _base._sha256(path) for path in FROZEN_INPUT_HASHES}
    mismatches = {
        str(path): {"expected": expected, "actual": actual[str(path)]}
        for path, expected in FROZEN_INPUT_HASHES.items()
        if actual[str(path)] != expected
    }
    if mismatches:
        raise RuntimeError(
            "frozen input hash mismatch: "
            f"{json.dumps(mismatches, sort_keys=True)}"
        )
    if _git_text("rev-parse", f"{CLASSIFICATION_PARENT}^") != (
        CLASSIFICATION_PARENT_PARENT
    ):
        raise RuntimeError("classification parent ancestry mismatch")
    if _git_text(
        "rev-parse", f"{CLASSIFICATION_PARENT}:src/schwgw/numerics/radial_solver.py"
    ) != CLASSIFICATION_RADIAL_BLOB:
        raise RuntimeError("classification parent radial blob mismatch")
    ledger = _base._load_json(
        Path(
            "runs/phase5/fig5_fig6_further_local_refinement/"
            "checkpoint_ledger.json"
        )
    )
    if (
        ledger.get("generation_contract_hash") != T8AQ_GENERATION_CONTRACT
        or ledger.get("metadata_contract_hash") != T8AQ_METADATA_CONTRACT
        or ledger.get("implementation", {}).get("commit") != T8AQ_COMMIT
        or _git_text("rev-parse", f"{T8AQ_COMMIT}^") != T8AQ_PARENT
    ):
        raise RuntimeError("immutable T8aq contract or implementation mismatch")
    prior_classification = _base._load_json(
        Path(
            "runs/phase5/fig5_fig6_further_local_radial_gate/"
            "classification_manifest.json"
        )
    )
    prior_preflight = _base._load_json(
        Path(
            "runs/phase5/fig5_fig6_further_local_radial_gate/"
            "resume_preflight.json"
        )
    )
    if (
        prior_classification.get("classification_snapshot_sha256")
        != "52889944b58ec8aae442afb7c743679fcbbd9d3dd21819cc61cf1364b683eb43"
        or prior_preflight.get("final_adapter_snapshot_sha256")
        != "ba6e63d87c7cc2cad4a64300a775bc07059d7a21760dbd431e411f6508febcb3"
    ):
        raise RuntimeError("immutable T4ab snapshot mismatch")
    if not CLASSIFICATION_PATH.exists():
        if _git_text("rev-parse", "HEAD") != CLASSIFICATION_PARENT:
            raise RuntimeError("classification must start at frozen candidate HEAD")
        if _git_text("hash-object", "src/schwgw/numerics/radial_solver.py") != (
            CLASSIFICATION_RADIAL_BLOB
        ):
            raise RuntimeError("pre-adapter radial worktree blob mismatch")
    return actual


def _global_contract(frozen_input_hashes: Mapping[str, str]) -> dict[str, Any]:
    contract = _ORIGINAL_GLOBAL_CONTRACT(frozen_input_hashes)
    contract["expected_record_count"] = EXPECTED_RECORD_COUNT
    contract["classification_parent_commit"] = CLASSIFICATION_PARENT
    contract["classification_parent_parent"] = CLASSIFICATION_PARENT_PARENT
    contract["classification_parent_radial_blob"] = CLASSIFICATION_RADIAL_BLOB
    contract["selection"] = "exact_41_unique_literal_failed_child_midpoints"
    return contract


def _write_envelope_module(
    *,
    segments: Mapping[
        tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]
    ],
    classification_sha256: str,
    oracle_validation_sha256: str,
    classification_snapshot: Mapping[str, Any],
) -> None:
    points = tuple((point.point_id, point.r) for point in TABLEI_POINTS)
    lines = [
        '"""Generated immutable T4ac literal failed-child Q018 envelope."""',
        "",
        "from __future__ import annotations",
        "",
        f"FREQUENCIES: tuple[float, ...] = {FREQUENCIES!r}",
        f"FREQUENCY_TOKENS: dict[float, str] = {FREQUENCY_TOKENS!r}",
        f"POINTS: tuple[tuple[str, float], ...] = {points!r}",
        "TRANSITION_SEGMENTS: dict[",
        "    tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]",
        "] = {",
    ]
    for k in FREQUENCIES:
        for sector in (Sector.ODD, Sector.EVEN):
            key = (k, sector.value)
            lines.append(f"    {key!r}: {segments[key]!r},")
    lines.extend(
        [
            "}",
            f"SOURCE_HASHES: dict[str, str] = {classification_snapshot['payload']['source_hashes']!r}",
            f'CLASSIFICATION_SNAPSHOT_SHA256: str = "{classification_snapshot["sha256"]}"',
            f'CLASSIFICATION_SHA256: str = "{classification_sha256}"',
            f'ORACLE_VALIDATION_SHA256: str = "{oracle_validation_sha256}"',
            "",
            "__all__ = [",
            '    "FREQUENCIES", "FREQUENCY_TOKENS", "POINTS",',
            '    "TRANSITION_SEGMENTS", "SOURCE_HASHES",',
            '    "CLASSIFICATION_SNAPSHOT_SHA256", "CLASSIFICATION_SHA256",',
            '    "ORACLE_VALIDATION_SHA256",',
            "]",
            "",
        ]
    )
    _base._atomic_text(ENVELOPE_PATH, "\n".join(lines))


def _aggregate(checkpoints: Sequence[Mapping[str, Any]]) -> None:
    _ORIGINAL_AGGREGATE(checkpoints)
    classification = _base._load_json(CLASSIFICATION_PATH)
    classification.update(
        {
            "thread": "T4ac",
            "decision_candidate": (
                "GREEN / LITERAL FAILED-CHILD RADIAL GATE READY"
            ),
        }
    )
    classification["non_artifact_statement"].update(
        {
            "no_t8ar": True,
            "not_uniform_or_full_grid": True,
            "literal_failed_child_midpoints_only": True,
        }
    )
    _base._atomic_json(CLASSIFICATION_PATH, classification)
    oracle = _base._load_json(ORACLE_PATH)
    oracle["thread"] = "T4ac"
    oracle["classification_sha256"] = _base._sha256(CLASSIFICATION_PATH)
    oracle["non_artifact_statement"] = classification["non_artifact_statement"]
    _base._atomic_json(ORACLE_PATH, oracle)
    segments = _base._compress_transition_records(
        classification["transition_records"]
    )
    _write_envelope_module(
        segments=segments,
        classification_sha256=_base._sha256(CLASSIFICATION_PATH),
        oracle_validation_sha256=_base._sha256(ORACLE_PATH),
        classification_snapshot=classification["classification_snapshot"],
    )


def _final_adapter_snapshot(
    classification_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    snapshot = _ORIGINAL_FINAL_ADAPTER_SNAPSHOT(classification_snapshot)
    payload = dict(snapshot["payload"])
    payload["schema_version"] = "phase5_t4ac_final_adapter_snapshot_v1"
    payload["implementation_parent"] = _git_text("rev-parse", "HEAD^")
    if payload["implementation_parent"] != CLASSIFICATION_PARENT:
        raise RuntimeError("implementation commit parent is not frozen candidate")
    return {"payload": payload, "sha256": _base._canonical_sha256(payload)}


def _write_manifest(preflight: Mapping[str, Any]) -> None:
    classification = _base._load_json(CLASSIFICATION_PATH)
    oracle = _base._load_json(ORACLE_PATH)
    checkpoint_lines = [
        f"- `{_base._checkpoint_path(k)}`: `{_base._sha256(_base._checkpoint_path(k))}`"
        for k in FREQUENCIES
    ]
    lines = [
        "# T4ac Literal Failed-Child Radial Gate Manifest",
        "",
        "- Decision candidate: `GREEN / LITERAL FAILED-CHILD RADIAL GATE READY`",
        f"- Classification rows: `{classification['summary']['total_records']}`",
        f"- Transition rows: `{classification['summary']['transition_record_count']}`",
        f"- Oracle validated: `{oracle['summary']['oracle_validated']}`",
        f"- Adapter preflight validated: `{preflight['summary']['adapter_validated']}`",
        f"- Classification SHA-256: `{_base._sha256(CLASSIFICATION_PATH)}`",
        f"- Oracle SHA-256: `{_base._sha256(ORACLE_PATH)}`",
        f"- Preflight SHA-256: `{_base._sha256(PREFLIGHT_PATH)}`",
        f"- Classification snapshot: `{classification['classification_snapshot_sha256']}`",
        f"- Final adapter snapshot: `{preflight['final_adapter_snapshot_sha256']}`",
        "",
        "## Checkpoints",
        "",
        *checkpoint_lines,
        "",
        "Radial-only evidence for exactly 41 literal failed-child midpoints.",
        "No T8ar, amplification, production, plot, fixture, Kirchhoff, paper",
        "artifact, lmax extension, full/uniform grid, or recursive midpoint.",
        "",
    ]
    _base._atomic_text(MANIFEST_PATH, "\n".join(lines))


def _run_preflight() -> None:
    envelope = importlib.import_module(
        "schwgw.numerics.q018_tablei_literal_failed_child_envelope"
    )
    legacy_envelope = importlib.import_module(
        "schwgw.numerics.q018_further_local_envelope"
    )
    for name in (
        "CLASSIFICATION_SHA256",
        "CLASSIFICATION_SNAPSHOT_SHA256",
        "ORACLE_VALIDATION_SHA256",
    ):
        setattr(legacy_envelope, name, getattr(envelope, name))
    _ORIGINAL_RUN_PREFLIGHT()
    preflight = _base._load_json(PREFLIGHT_PATH)
    preflight["schema_version"] = PREFLIGHT_SCHEMA_VERSION
    preflight["thread"] = "T4ac"
    preflight["non_artifact_statement"].update(
        {
            "no_t8ar": True,
            "not_uniform_or_full_grid": True,
            "literal_failed_child_midpoints_only": True,
        }
    )
    _base._atomic_json(PREFLIGHT_PATH, preflight)
    _write_manifest(preflight)


def _configure_base() -> None:
    assignments = {
        "SCHEMA_VERSION": SCHEMA_VERSION,
        "CHECKPOINT_SCHEMA_VERSION": CHECKPOINT_SCHEMA_VERSION,
        "PREFLIGHT_SCHEMA_VERSION": PREFLIGHT_SCHEMA_VERSION,
        "FREQUENCIES": FREQUENCIES,
        "FREQUENCY_TOKENS": FREQUENCY_TOKENS,
        "LMAX_VALUES": LMAX_VALUES,
        "OUTPUT_DIR": OUTPUT_DIR,
        "CHECKPOINT_DIR": CHECKPOINT_DIR,
        "CLASSIFICATION_PATH": CLASSIFICATION_PATH,
        "ORACLE_PATH": ORACLE_PATH,
        "PREFLIGHT_PATH": PREFLIGHT_PATH,
        "MANIFEST_PATH": MANIFEST_PATH,
        "ENVELOPE_PATH": ENVELOPE_PATH,
        "ADAPTER_NAME": ADAPTER_NAME,
        "ADAPTER_SOLVER": ADAPTER_SOLVER,
        "ADAPTER_WARNING": ADAPTER_WARNING,
        "CLASSIFICATION_SOURCE_PATHS": CLASSIFICATION_SOURCE_PATHS,
        "FROZEN_INPUT_HASHES": FROZEN_INPUT_HASHES,
        "IMPLEMENTATION_PATHS": IMPLEMENTATION_PATHS,
        "_verify_frozen_inputs": _verify_frozen_inputs,
        "_global_contract": _global_contract,
        "_write_envelope_module": _write_envelope_module,
        "_aggregate": _aggregate,
        "_final_adapter_snapshot": _final_adapter_snapshot,
        "_write_manifest": _write_manifest,
    }
    for name, value in assignments.items():
        setattr(_base, name, value)


def _verify_exact_contract() -> None:
    if len(FREQUENCIES) != 41 or len(set(FREQUENCIES)) != 41:
        raise RuntimeError("literal failed-child frequency cardinality mismatch")
    if tuple(LMAX_VALUES) != FREQUENCIES:
        raise RuntimeError("frequency/lmax ordering mismatch")
    if max(max(values) for values in LMAX_VALUES.values()) != 360:
        raise RuntimeError("frozen maximum lmax mismatch")
    actual = sum(
        (max(LMAX_VALUES[k]) - 1) * 2 * len(TABLEI_POINTS)
        for k in FREQUENCIES
    )
    if actual != EXPECTED_RECORD_COUNT:
        raise RuntimeError(
            f"classification cardinality mismatch: {actual} != {EXPECTED_RECORD_COUNT}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the frozen T4ac literal failed-child radial/Q018 gate."
    )
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--resume-preflight", action="store_true")
    args = parser.parse_args()
    if args.audit and args.resume_preflight:
        parser.error("choose only one of --audit or --resume-preflight")
    _verify_exact_contract()
    _configure_base()
    if args.audit:
        _base._audit()
    elif args.resume_preflight:
        _run_preflight()
    else:
        _base._run_classification()


if __name__ == "__main__":
    main()
