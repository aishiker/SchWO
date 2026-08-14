"""Frozen T4ad another-bounded-local radial/Q018 gate.

The numerical kernel and atomic-checkpoint machinery are reused from the
reviewed T4ab/T4ac runners.  This module freezes a distinct 55-frequency
contract, source identity, output root, and final-adapter identity.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import phase5_further_local_radial_gate as _base
import phase5_literal_failed_child_radial_gate as _previous
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.perturbations import Sector


SCHEMA_VERSION = "phase5_t4ad_another_bounded_local_radial_gate_v1"
CHECKPOINT_SCHEMA_VERSION = (
    "phase5_t4ad_another_bounded_local_radial_checkpoint_v1"
)
PREFLIGHT_SCHEMA_VERSION = (
    "phase5_t4ad_another_bounded_local_radial_preflight_v1"
)
FREQUENCIES = (
    0.86875,
    0.94375, 0.95625, 0.96875,
    1.54375, 1.56875, 1.58125, 1.59375, 1.63125, 1.65625,
    1.69375, 1.703125, 1.715625,
    2.778125, 2.784375, 2.80625, 2.81875, 2.83125, 2.84375,
    2.85625, 2.86875, 2.88125, 2.89375, 2.90625, 2.91875,
    2.93125, 2.94375, 2.95625, 2.96875, 2.98125, 2.99375,
    3.753125, 3.759375, 3.765625, 3.771875, 3.778125, 3.784375,
    3.790625, 3.796875, 3.80625, 3.81875, 3.83125, 3.84375,
    3.85625, 3.86875, 3.88125, 3.89375, 3.90625, 3.91875,
    3.93125, 3.94375, 3.95625, 3.96875, 3.98125, 3.99375,
)
FREQUENCY_TOKENS = {k: str(k).replace(".", "p") for k in FREQUENCIES}


def _lmax_values(k: float) -> tuple[int, ...]:
    seed = 12 * int(-(-max(84.0, 90.0 * k) // 12.0))
    return tuple(sorted({max(24, seed - 72), seed - 48, seed - 24, seed}))


LMAX_VALUES = {k: _lmax_values(k) for k in FREQUENCIES}
EXPECTED_RECORD_COUNT = 239_120
CLASSIFICATION_PARENT = "9a12fef8e09a46b4ed738723f4127896e64bf4c1"
CLASSIFICATION_PARENT_PARENT = "366a517c71b56026bb0f3ca37c14cc75243985b2"
CLASSIFICATION_RADIAL_BLOB = "c1237739e0002024c802272564167cc590d37f7f"
T8AR_COMMIT = "366a517c71b56026bb0f3ca37c14cc75243985b2"
T8AR_PARENT = "6e86d8b419d8c09af38e226400f7439f7cdfed79"
T8AR_GENERATION_CONTRACT = (
    "b9ed45769f1bf61925ac5b59e6ab14b5e31a1aecc858bec076adf0e7e398da56"
)
T8AR_METADATA_CONTRACT = (
    "949041c7bd7b5ee41409e0a9b19ad73515aeb73674a5f3cd6e7782b4c4385d97"
)

OUTPUT_DIR = Path(
    "runs/phase5/fig5_fig6_another_bounded_local_radial_gate"
)
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoint"
CLASSIFICATION_PATH = OUTPUT_DIR / "classification_manifest.json"
ORACLE_PATH = OUTPUT_DIR / "oracle_validation.json"
PREFLIGHT_PATH = OUTPUT_DIR / "resume_preflight.json"
MANIFEST_PATH = OUTPUT_DIR / "manifest.md"
ENVELOPE_PATH = Path(
    "src/schwgw/numerics/q018_tablei_another_bounded_local_envelope.py"
)
ADAPTER_NAME = "q018_tablei_another_bounded_local_transition"
ADAPTER_SOLVER = "q018_tablei_another_bounded_local_transition_oracle"
ADAPTER_WARNING = (
    "q018_tablei_another_bounded_local_transition_oracle_used"
)

CLASSIFICATION_SOURCE_PATHS = (
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("src/schwgw/numerics/experimental/q018_rescaled_oracle.py"),
    Path("src/schwgw/io/tablei.py"),
    Path("scripts/phase5_further_local_radial_gate.py"),
    Path("scripts/phase5_literal_failed_child_radial_gate.py"),
    Path("scripts/phase5_another_bounded_local_radial_gate.py"),
    Path(
        "docs/superpowers/specs/"
        "2026-07-20-t4ad-t8as-another-bounded-local-refinement-design.md"
    ),
    Path(
        "docs/superpowers/plans/"
        "2026-07-20-t4ad-another-bounded-local-radial-gate.md"
    ),
    Path("docs/prompts/phase5_t4ad_another_bounded_local_radial_gate.md"),
)
FROZEN_INPUT_HASHES = {
    Path("runs/phase5/fig5_fig6_literal_failed_child_radial_gate/classification_manifest.json"):
        "e5c934568ff1a9f80838df3fc674fea153e4c638777e6d7c9c2c2d32d0024e5b",
    Path("runs/phase5/fig5_fig6_literal_failed_child_radial_gate/oracle_validation.json"):
        "b4954a152aa81853fe53931bcb9ee9820b6d6da6d923019288f276d0519c52c6",
    Path("runs/phase5/fig5_fig6_literal_failed_child_radial_gate/resume_preflight.json"):
        "08b5542a26c0b95f6bf10005aeb21681f75735f53b924f894f1c133081ee2873",
    Path("runs/phase5/fig5_fig6_literal_failed_child_radial_gate/manifest.md"):
        "6b55500aae750f7b2400627825220f18e2ca9f608a4c977707e4f2ec363e78c8",
    Path("runs/phase5/fig5_fig6_literal_failed_child_refinement/checkpoint_ledger.json"):
        "0ba6a6ae8ecd44552af2524e556d99b00977efe4e141ea17a78113cde67d2e4c",
    Path("runs/phase5/fig5_fig6_literal_failed_child_refinement/literal_failed_child_values.npz"):
        "a3ba554efb94d6620c8b267077d0e57f843ad599e40586213f2a2ef8e1fdaf42",
    Path("runs/phase5/fig5_fig6_literal_failed_child_refinement/literal_failed_child_values.npz.json"):
        "1c8f02d8d930f1f51439c15d5f0dad975f4a21567fbdc1dff830f95c84c8f8d2",
    Path("runs/phase5/fig5_fig6_literal_failed_child_refinement/literal_failed_child_sampling_audit.json"):
        "1d9a701eb714ebd38fec2a37d7066f2aae188d25e80447e0abbecc717062bb70",
    Path("runs/phase5/fig5_fig6_literal_failed_child_refinement/manifest.md"):
        "1b3003bf59a3989f54ef125484cffaada7913fabab0ab010464c94bd12f5b6e3",
    Path("docs/handoffs/T7_current.md"):
        "99b669d8f7b1000dd9f002c27d1234a286d00690ad82c84f1ebc159ec33bb3fc",
    Path("docs/handoffs/archive/T7_2026-07-18_pre_t7cd_literal_failed_child_review.md"):
        "acfd4e53a8fc63a2e33eb7c5051508e5a1f918e6dcbe3768b1256452a5ff7298",
    Path("docs/superpowers/specs/2026-07-20-t4ad-t8as-another-bounded-local-refinement-design.md"):
        "852e0a7bbadf1366fdcf04d6906f6d35fc5746c4d119f53b764f660dee96720e",
    Path("docs/superpowers/plans/2026-07-20-t4ad-another-bounded-local-radial-gate.md"):
        "f8d0e7e4cab9c4bb3d87ac80b420862472aa6997b5ff108ffc34609f600ba1cd",
    Path("docs/superpowers/plans/2026-07-20-t8as-another-bounded-local-refinement.md"):
        "7794253246d38392411377a788b29be951cac75e6ff81175509d1265520c039b",
    Path("docs/prompts/phase5_t4ad_another_bounded_local_radial_gate.md"):
        "962f046b69f3ba8c835592528673d83d81c2e4928e5f43bc07c4c4f2acaec905",
    Path("docs/prompts/phase5_t7ce_another_bounded_local_radial_review.md"):
        "57cc31ae35dd31f8dd4eba1762553837b1e729411bd6fbaed8fedc6670a2f241",
    Path("docs/prompts/phase5_t8as_another_bounded_local_refinement.md"):
        "245e945d52bbc43be94720fee7699f1c5f24f2005275b185a7da7a8a265fa292",
    Path("docs/prompts/phase5_t7cf_another_bounded_local_refinement_review.md"):
        "c0403638d8419788a8f7817fbbcc969dab1be0d994d4661958dcf8d4f26dae09",
}
IMPLEMENTATION_PATHS = (
    Path("scripts/phase5_another_bounded_local_radial_gate.py"),
    Path("src/schwgw/numerics/q018_tablei_another_bounded_local_envelope.py"),
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("tests/physics/test_q018_production_integration_design.py"),
    Path("tests/physics/test_radial_solver.py"),
)

_ORIGINAL_GLOBAL_CONTRACT = _previous._ORIGINAL_GLOBAL_CONTRACT
_ORIGINAL_AGGREGATE = _previous._ORIGINAL_AGGREGATE
_ORIGINAL_FINAL_ADAPTER_SNAPSHOT = _previous._ORIGINAL_FINAL_ADAPTER_SNAPSHOT
_ORIGINAL_RUN_PREFLIGHT = _previous._ORIGINAL_RUN_PREFLIGHT


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
            "runs/phase5/fig5_fig6_literal_failed_child_refinement/"
            "checkpoint_ledger.json"
        )
    )
    if (
        ledger.get("generation_contract_hash") != T8AR_GENERATION_CONTRACT
        or ledger.get("metadata_contract_hash") != T8AR_METADATA_CONTRACT
        or ledger.get("implementation", {}).get("commit") != T8AR_COMMIT
        or _git_text("rev-parse", f"{T8AR_COMMIT}^") != T8AR_PARENT
    ):
        raise RuntimeError("immutable T8ar contract or implementation mismatch")
    prior_classification = _base._load_json(
        Path(
            "runs/phase5/fig5_fig6_literal_failed_child_radial_gate/"
            "classification_manifest.json"
        )
    )
    prior_preflight = _base._load_json(
        Path(
            "runs/phase5/fig5_fig6_literal_failed_child_radial_gate/"
            "resume_preflight.json"
        )
    )
    if (
        prior_classification.get("classification_snapshot_sha256")
        != "e675b751fd4beae2446597034b99f847e0cc3528551bfc30f8efd3460ad944fe"
        or prior_preflight.get("final_adapter_snapshot_sha256")
        != "8188b306fea0190654f752190f0ab6e96ef6970b16fea704b9cdb99ca96c7ccc"
    ):
        raise RuntimeError("immutable T4ac snapshot mismatch")
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
    contract["selection"] = "exact_55_unique_t7cd_failed_child_midpoints"
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
        '"""Generated immutable T4ad another-bounded-local Q018 envelope."""',
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
            "thread": "T4ad",
            "decision_candidate": (
                "GREEN / ANOTHER BOUNDED LOCAL RADIAL GATE READY"
            ),
        }
    )
    classification["non_artifact_statement"].update(
        {
            "no_t8as": True,
            "not_uniform_or_full_grid": True,
            "another_bounded_local_failed_child_midpoints_only": True,
        }
    )
    _base._atomic_json(CLASSIFICATION_PATH, classification)
    oracle = _base._load_json(ORACLE_PATH)
    oracle["thread"] = "T4ad"
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
    payload["schema_version"] = "phase5_t4ad_final_adapter_snapshot_v1"
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
        "# T4ad Another Bounded Local Radial Gate Manifest",
        "",
        "- Decision candidate: `GREEN / ANOTHER BOUNDED LOCAL RADIAL GATE READY`",
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
        "Radial-only evidence for exactly 55 literal T7cd failed-child midpoints.",
        "No T8as, amplification, production, plot, fixture, Kirchhoff, paper",
        "artifact, lmax extension, full/uniform grid, or recursive midpoint.",
        "",
    ]
    _base._atomic_text(MANIFEST_PATH, "\n".join(lines))


def _run_preflight() -> None:
    envelope = importlib.import_module(
        "schwgw.numerics.q018_tablei_another_bounded_local_envelope"
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
    preflight["thread"] = "T4ad"
    preflight["non_artifact_statement"].update(
        {
            "no_t8as": True,
            "not_uniform_or_full_grid": True,
            "another_bounded_local_failed_child_midpoints_only": True,
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
    if len(FREQUENCIES) != 55 or len(set(FREQUENCIES)) != 55:
        raise RuntimeError("another-bounded-local frequency cardinality mismatch")
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
        description="Run the frozen T4ad another-bounded-local radial/Q018 gate."
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
