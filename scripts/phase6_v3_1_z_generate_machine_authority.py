#!/usr/bin/env python3
"""Build and verify the frozen V3.1-Z generated machine-authority bundle.

This package-time compiler is deliberately stdlib-only and zero-science.  It
accepts one canonical declarative specification, expands the closed authority
catalog, and publishes only into a fresh absent output directory.
"""

from __future__ import annotations

import argparse
import ast
import base64
import csv
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import platform
import re
import resource
import stat
import sys
import time
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any, Final


SCHEMA: Final = "phase6_v3_1_z_machine_authority_spec_v1"
GATE_ID: Final = "phase6_v3_1_z_generated_machine_authority_redesign_v1"
SPEC_REVISION: Final = 1
MAX_SHARD_ROWS: Final = 4096
MAX_OUTPUT_BYTES: Final = 2 * 1024**3
MAX_GENERATION_SECONDS: Final = 600.0
MAX_RSS_BYTES: Final = 4 * 1024**3
EXPECTED_ROOT_PARENT: Final = (
    "/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/"
    "runs/phase6/classic_scattering"
)

EXPECTED_STAGE_ROWS: Final = (
    ("P00_REQUEST_RAW_PARENT", "PARENT_ONLY_PRELAUNCH", "PARENT_ONLY_PRELAUNCH"),
    ("P01_RUNTIME_ENTRY", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P02_REQUEST_RAWJSON", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P03_LEDGER_SCHEMA", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P04_LEDGER_PROJECTION", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P05_PRELOAD_STATE", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P06_PACLET_LOAD", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P07_CONTEXT_LOAD", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    (
        "P08_FIND_FILE",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "CHILD_PREDICATES",
    ),
    (
        "P09_SOURCE_START_CHILD",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "CHILD_PREDICATES",
    ),
    (
        "P10_SOURCE_START_PARENT",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "LOGICAL_PREDICATE_BARRIER_THEN_PARENT_OBSERVATIONS",
    ),
    (
        "P11_PRE_SCIENCE_COMMIT",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "CHILD_PREDICATES",
    ),
    (
        "P12_OPERATION",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "CHILD_PREDICATES",
    ),
    (
        "P13_SOURCE_END_CHILD",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "CHILD_PREDICATES",
    ),
    (
        "P14_SOURCE_END_PARENT",
        "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
        "LOGICAL_PREDICATE_BARRIER_THEN_PARENT_OBSERVATIONS",
    ),
    ("P15_COUNTERS", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P16_RESULT", "CHILD_PREDICATES", "CHILD_PREDICATES"),
    ("P17_CHILD_TERMINAL", "PARENT_ONLY_POSTREAP", "PARENT_ONLY_POSTREAP"),
)

COMPATIBILITY_STAGE_COUNTS: Final = (
    5,
    9,
    9,
    5,
    6,
    17,
    10,
    8,
    11,
    11,
    7,
    6,
    4,
    8,
    16,
    7,
    4,
    8,
)
PRODUCTION_STAGE_COUNTS: Final = (
    5,
    9,
    5,
    10,
    120,
    4,
    3,
    16,
    24,
    24,
    67,
    7,
    4,
    24,
    68,
    7,
    4,
    8,
)

EXPECTED_OPERATION_ROWS: Final = (
    (
        "compatibility",
        "COMPAT",
        "COMPATIBILITY",
        False,
        1,
        151,
        82,
        COMPATIBILITY_STAGE_COUNTS,
    ),
    (
        "source_load_micro",
        "MICRO",
        "PRODUCTION_PRE_API_EXIT",
        False,
        1,
        409,
        263,
        PRODUCTION_STAGE_COUNTS,
    ),
    (
        "full_sentinel",
        "SENTINEL",
        "PRODUCTION_SENTINEL",
        True,
        35,
        14_315,
        9_205,
        PRODUCTION_STAGE_COUNTS,
    ),
    (
        "official",
        "OFFICIAL",
        "PRODUCTION_OFFICIAL",
        True,
        161,
        65_849,
        42_343,
        PRODUCTION_STAGE_COUNTS,
    ),
)

EXPECTED_ROUTE_C_ANCHORS: Final = (
    (0, "0.1", 2, "odd"),
    (1, "0.1", 3, "odd"),
    (2, "0.1", 4, "odd"),
    (3, "0.1", 8, "odd"),
    (4, "0.5", 2, "odd"),
    (5, "0.5", 3, "odd"),
    (6, "0.5", 4, "odd"),
    (7, "0.5", 10, "odd"),
    (8, "1", 2, "odd"),
    (9, "1", 3, "odd"),
    (10, "1", 4, "odd"),
    (11, "1", 5, "odd"),
    (12, "1", 13, "odd"),
    (13, "2", 2, "odd"),
    (14, "2", 3, "odd"),
    (15, "2", 4, "odd"),
    (16, "2", 10, "odd"),
    (17, "2", 18, "odd"),
    (18, "4", 2, "odd"),
    (19, "4", 3, "odd"),
    (20, "4", 4, "odd"),
    (21, "4", 20, "odd"),
    (22, "4", 28, "odd"),
)
EXPECTED_ROUTE_C_NODES: Final = ("P0", "P1", "I0", "I2", "O2", "O4", "O8")
EXPECTED_ROUTE_C_NODE_PRECISION: Final = (
    ("P0", 90, 45, 45),
    ("P1", 120, 60, 60),
    ("I0", 120, 60, 60),
    ("I2", 120, 60, 60),
    ("O2", 120, 60, 60),
    ("O4", 120, 60, 60),
    ("O8", 120, 60, 60),
)

EXPECTED_STATE_MACHINE: Final = (
    ("SEED_P00", "NO_ROOT_EVENTS", "P00_EVENTS", "PARENT", "stage0_seed"),
    ("P00_EVENT", "P00_EVENTS", "P00_EVENTS_OR_FINAL0", "PARENT", "event_then_prefix"),
    ("OPEN_P01", "FINAL0", "P01_FRAME", "PARENT", "final_then_open"),
    (
        "ORDINARY_FRAME",
        "P01_FRAME",
        "EVENT_PREFIX_ACK_OR_FINAL",
        "CHILD_TO_PARENT",
        "validate_commit_ack",
    ),
    (
        "STAGE_FINAL",
        "EVENT_PREFIX_ACK_OR_FINAL",
        "NEXT_STAGE_FRAME",
        "PARENT",
        "final_open_ack",
    ),
    (
        "COMPAT_BARRIER",
        "BARRIER_FRAME",
        "PARENT_FIXTURE_EVENTS",
        "PARENT",
        "finite_fixture_loop",
    ),
    (
        "PRODUCTION_BARRIER",
        "BARRIER_FRAME",
        "PARENT_SOURCE_EVENTS",
        "PARENT",
        "logical_request_plus_parent_facts",
    ),
    ("P16_EXIT", "P16_LAST_EVENT", "CHILD_EOF", "PARENT", "final16_exit_ack"),
    (
        "RECEIPT",
        "CHILD_EOF",
        "P17_OPEN",
        "PARENT",
        "wait_reap_pgempty_receipt",
    ),
    ("P17_EVENTS", "P17_OPEN", "FINAL17", "PARENT", "eight_parent_events"),
    (
        "CALL_TERMINAL",
        "FINAL17",
        "CALL_SEALED",
        "PARENT",
        "manifest_checkpoint_chmod_closeout",
    ),
    (
        "NEXT_CALL",
        "CALL_SEALED",
        "NEXT_SEED",
        "PARENT",
        "bind_prior_manifest_checkpoint_seal",
    ),
    (
        "OPERATION_TERMINAL",
        "ALL_CALLS_SEALED",
        "ROOT_SEALED",
        "PARENT",
        "operation_manifest_root_checkpoint",
    ),
    (
        "WRITER_RELEASE",
        "ROOT_SEALED",
        "EXTERNAL_CLOSEOUT",
        "EXTERNAL_OBSERVER",
        "release_after_checkpoint",
    ),
    (
        "FAILURE",
        "ANY_ACTIVE_STATE",
        "TERMINAL_FAILURE",
        "PARENT",
        "no_advance_ack_terminate_wait_reap",
    ),
)

RESOURCE_ARTIFACT_MAX_ENCODED_BYTES: Final = (
    ("parent_event", 8_192),
    ("prefix_checkpoint", 4_096),
    ("final_stage_checkpoint", 8_192),
    ("stage_open_authority", 8_192),
    ("stage0_seed", 16_384),
    ("child_exit_authority", 4_096),
    ("lifecycle_receipt", 32_768),
    ("p17_closure", 8_192),
    ("terminal_manifest", 65_536),
    ("operation_terminal_manifest", 65_536),
    ("root_terminal_checkpoint", 32_768),
)

EXPECTED_PROJECTED_ROOT_BYTES: Final = (
    ("compatibility", 4_313_088),
    ("source_load_micro", 8_595_456),
    ("full_sentinel", 295_270_400),
    ("official", 1_357_654_016),
)

EXPECTED_RESOURCE_LIMITS: Final = {
    "ack_max_bytes": 2_048,
    "artifact_max_encoded_record_bytes": [
        [schema_id, maximum]
        for schema_id, maximum in RESOURCE_ARTIFACT_MAX_ENCODED_BYTES
    ],
    "compatibility_wall_seconds_max": 120,
    "compatibility_whole_root_bytes_max": 16 * 1024**2,
    "concurrency": 1,
    "fixed_authority_bytes_per_call": 65_536,
    "fixed_authority_bytes_per_operation": 65_536,
    "frame_max_bytes": 4_096,
    "free_space_rule": (
        "projected_root_bytes <= floor(free_bytes/4) and "
        "free_bytes >= 4*projected_root_bytes"
    ),
    "generated_bundle_bytes_strict_max": MAX_OUTPUT_BYTES,
    "generation_wall_seconds_max": 600,
    "micro_wall_seconds_max": 120,
    "micro_whole_root_bytes_max": 16 * 1024**2,
    "official_rss_bytes_max": 8 * 1024**3,
    "official_wall_seconds_max": 36 * 60 * 60,
    "peak_rss_bytes_strict_max": MAX_RSS_BYTES,
    "projected_root_bytes": [
        [operation, projected] for operation, projected in EXPECTED_PROJECTED_ROOT_BYTES
    ],
    "projection_formula": (
        "fixed_authority_bytes_per_call*calls + "
        "fixed_authority_bytes_per_operation + frame_max_bytes*child_frames + "
        "ack_max_bytes*acks + raw_stdout_limit_bytes_per_call*calls + "
        "raw_stderr_limit_bytes_per_call*calls + "
        "sum(artifact_max_encoded_record_bytes[schema]*"
        "declared_output_record_count[schema])"
    ),
    "raw_stderr_limit_bytes_per_call": 262_144,
    "raw_stdout_limit_bytes_per_call": 1_048_576,
    "sentinel_rss_bytes_max": 8 * 1024**3,
    "sentinel_wall_seconds_max": 8 * 60 * 60,
}

# Independent compiler-side commitments to the behavior-bearing declarative
# tables.  These are deliberately not stored in the spec: the compiler first
# reconstructs and type-checks every semantic edge below, then uses these
# domain-separated commitments as a second line of defense against a
# self-consistent but unauthorized rewrite or an orphan row.
EXPECTED_SEMANTIC_SECTION_SHA256: Final = {
    "type_registry": "eed5cc350a17ce961a8b0aac55d169b0612cc4842ccfef8de8aa6bd608de3c26",
    "json_shape_registry": "52b8fc775351de41e3e6eb7b7b90089617a272b12f041aaabf000c91dea55dad",
    "value_schema_registry": "894a0dccc54bd3ccaba5da07418e98d6fca5f1c6601a02ce23cedac0832c15f6",
    "algorithm_registry": "4f52a82aa22e76da74b8d2c1d499078c60fed1464c9f3a4346acb4c5f5b93712",
    "policy_registry": "d6d533dc7956fc5924527d23e22a0319ac0dee725228ea7d2095440a010c6328",
    "null_rule_registry": "629f24398898a8f669bff9f88fbb7528816028879770fa7787440b6e01892503",
    "null_matrix_registry": "b8252d568375ac59cbbdf227ddc0452768e106dbe49cd7ed5c90b591af124a15",
    "fixture_constructor_registry": "e1da5b2ba0ba8ede69bab3d247e0cef698c0c8a816b1b402232e7f78469fc7aa",
    "selector_registry": "62fb5937195957997f0f82ad882b8c622b32cbe77ea430fb1f76b59fbbe4500a",
    "catalog_registry": "a241de71457f4542565bcd0b5f18c03842f4c80e579a824518fbe76cece3dc03",
    "reason_code_registry": "a9df488af36cf6370506490775323b86fa65bb93bed917b3bc7b9e0a39299afc",
    "observer_registry": "9c01aed2c82fd61b7e9669130bf815292182e9ad17b672e6dd1c9ff530e75c54",
    "executor_registry": "c48d837887d3c7edece3b5ba0b781555570e4b4c2763835683f2170f8455e966",
    "comparison_registry": "dfbd7f86d23f7c0f5cdc7d0876d7a50895929e9ee4cbd6785a70ce92911c3251",
    "expected_expression_registry": "ee21c48d70768bf7c33f6fc256c08dc2ede507bd2a95b01b334bdf7be92a09f4",
    "evidence_input_registry": "60965aa5636e8fecde950b778ef92ac643b0c78a6c2e7a16645b81f6dbad4a35",
    "identity_policy_registry": "d6a1412417d05da5784fe207395dce31c6ff29a04d8f3858f80d18c9dec94676",
    "path_expression_registry": "eb4084e85a11920e4a43ea7bdfb4c3277c43cfa3e23721c834b14f35ffa9c938",
    "conformance_vector_registry": "5b16ca7757e7a72658ab005668864ca92a73fcc97333fc579cb94dbf884595e4",
    "conformance_vector_plans": "b26221f1318d09b8a93382c51f96606af2753cc737bbf05a1ed237ef23d84863",
    "mutation_operator_registry": "6a9b1dd476eec6b18be9efd765e7ccf47a60ba8bd42b010720c31e4967288f97",
    "mutation_plans": "d3fc2369750ecca656206d3a1ddbe409e30149f31331de96934adc5c035c93cf",
    "artifact_schemas": "1d5b6022f1cc96532f4ef2bef766a5af8ca20427b3b58423d89eae068e3a2941",
    "immutable_inputs": "c73894a75b1fb5aa5e67cde0c06b28c60f90905b40c29ac2acd05c6eaf6f7ab9",
    "digest_nodes": "b74cade9e9470b8e25de9b869fb7034f44c640a74e0c9380aeb9e40f1e9e7ff2",
    "predicate_families": "0682f8976d525846f49f324d4865e02f73bb19856441d03364b1e81ad4f703b4",
}

COMPATIBILITY_FIXTURE_ALGORITHM_ID: Final = "Z.ALG.COMPATIBILITY.LITERAL_OPERATION_V1"
COMPATIBILITY_FIXTURE_PAYLOAD_FIELDS: Final = (
    "payload_schema",
    "payload_revision",
    "case_ordinal",
    "case_id",
    "input_fixture_id",
    "subject_predicate_id",
    "stage_ordinal",
    "owner",
    "observer_id",
    "executor_id",
    "operation_id",
    "algorithm_id",
    "raw_input_hex",
    "raw_input_sha256",
    "expected_kind",
    "expected_tagged_value_or_null",
    "case_expected_disposition",
    "reject_reason_or_null",
    "earliest_rejection_state_or_null",
    "science_call_count",
)
BOOTSTRAP_FIXTURE_PAYLOAD_FIELDS: Final = (
    "payload_schema",
    "payload_revision",
    "vector_ordinal",
    "vector_id",
    "scope_id",
    "operation_or_schema_id",
    "raw_input_hex",
    "raw_input_sha256",
    "expected_kind",
    "expected_tagged_value",
    "science_call_count",
)
EXPECTED_COMPATIBILITY_OPERATION_TABLE: Final = [
    [
        "Z.OP.RAWJSON_DECODE_V1",
        "RAW_BYTES",
        [
            "UTF8",
            "NO_BOM",
            "EXACT_ONE_LF",
            "DUPLICATE_MEMBER_REJECT",
            "NAN_INFINITY_REJECT",
            "CANONICAL_REENCODE_EQUAL",
        ],
        "TAGGED_JSON_VALUE_OR_REJECTION",
    ],
    [
        "Z.OP.NAMED_SIX_FIELD_PROJECTION_V1",
        "RAW_JSON_RECORD_ARRAY",
        [
            "EXACT_KEYS",
            ["context", "mode", "nlink", "path", "sha256", "size"],
            "PROJECT",
            ["context", "path", "sha256", "size", "mode", "nlink"],
            "PRESERVE_RECORD_ORDER",
            "NO_SORT_NO_SET",
        ],
        "ORDERED_PROJECTION_SHA256_OR_REJECTION",
    ],
    [
        "Z.OP.EXACT_RELATION_V1",
        "TAGGED_OPERAND_PAIR",
        [
            "TYPE_EXACT",
            "VALUE_EXACT",
            "ORDER_SENSITIVE",
            "SYMBOLIC_IS_INDETERMINATE",
        ],
        "BOOLEAN_OR_INDETERMINATE",
    ],
    [
        "Z.OP.UNICODE_NORMALIZE_V1",
        "UTF8_STRING_OPERANDS",
        [
            "NFC",
            "NFD",
            "PRESERVE_RAW_BYTES",
            "REJECT_CONFUSABLE_AND_INVISIBLE_BY_LITERAL_ALLOWLIST",
        ],
        "STRING_BOOLEAN_OR_DIAGNOSTIC",
    ],
    [
        "Z.OP.ASCII_PATH_GRAMMAR_V1",
        "UTF8_STRING",
        [
            "ASCII_ONLY",
            "RELATIVE",
            "SLASH_SEPARATOR",
            ("NO_COLON_BACKSLASH_REPEATED_SLASH_LEADING_TRAILING_SLASH_DOT_DOTDOT"),
            "WHOLE_INPUT",
        ],
        "STRING_OR_REJECTION",
    ],
    [
        "Z.OP.REGEX_DIAGNOSTIC_V1",
        "LITERAL_PATTERN_AND_INPUT",
        ["DIAGNOSTIC_ONLY", "NO_PRODUCTION_REGEX_DISPATCH"],
        "PATTERN_OR_COUNTER",
    ],
    [
        "Z.OP.LOWER_HEX64_SHAPE_V1",
        "RAW_STRING_OR_FILE_BYTES",
        ["ASCII_LOWER_HEX", "EXACT_LENGTH_64", "RAW_FILE_SHA256_AND_SIZE"],
        "HASH_OR_FILE_IDENTITY_OR_REJECTION",
    ],
    [
        "Z.OP.EXACT_INTEGER_DOMAIN_V1",
        "JSON_TOKEN_OR_MISSING",
        [
            "INTEGER_TOKEN_ONLY",
            "BOOLEAN_NOT_INTEGER",
            "ARBITRARY_PRECISION",
            "DOMAIN_NONNEGATIVE_WHERE_DECLARED",
        ],
        "INTEGER_OR_REJECTION",
    ],
    [
        "Z.OP.FRAME_CODEC_MODEL_V1",
        "RAW_FRAME_OR_LITERAL_CHUNK_PLAN",
        [
            "ONE_COMPACT_ARRAY_PER_LF",
            "UTF8",
            "EXACT_SCHEMA_SESSION_SEQUENCE_PREDECESSOR_TYPE_OUTCOME",
            "MAX_BYTES_1048576",
            "FLUSH_BEFORE_WAIT",
        ],
        "DECODED_VALUE_OR_REJECTION",
    ],
    [
        "Z.OP.ACK_FSM_MODEL_V1",
        "LITERAL_ACK_TRACE",
        [
            "AFTER_FILE_FSYNC",
            "AFTER_PREFIX_AND_FINAL",
            "EXACT_SESSION_FRAME_SEQUENCE",
            "ONCE",
            "NO_REPLAY_NO_DELAY",
        ],
        "ACK_TRANSITION_OR_REJECTION",
    ],
    [
        "Z.OP.POSIX_NOFOLLOW_TEMPFS_V1",
        "LITERAL_TEMPFS_RECIPE",
        [
            "LSTAT_NOFOLLOW",
            "OPEN_NOFOLLOW",
            "DEVICE_INODE",
            "MODE_NLINK_SIZE_HASH",
            "NO_ALIAS",
        ],
        "OBSERVED_IDENTITY_VALUE",
    ],
    [
        "Z.OP.SYNTHETIC_SOURCE_ENV_MODEL_V1",
        "LITERAL_SOURCE_ENV_RECIPE",
        [
            "SYNTHETIC_ONLY",
            "NO_PACLET_NO_SOURCE_LOAD",
            "EXACT_CONTEXT_PATH_SOURCE_IDENTITIES",
        ],
        "CLEAN_STATE_OR_REJECTION",
    ],
    [
        "Z.OP.FAKE_CHILD_IDENTITY_MODEL_V1",
        "LITERAL_CHILD_IDENTITY_RECIPE",
        [
            "PARENT_OWNS_EXPECTED_AND_IDENTITY",
            "FAKE_VALUES_CANNOT_CONFIRM_EXECUTABLE_RUNTIME_PROCESS_SOURCE",
        ],
        "REJECTION_ONLY",
    ],
    [
        "Z.OP.OEXCL_PUBLICATION_MODEL_V1",
        "LITERAL_PUBLICATION_TRACE",
        [
            "FRESH_ABSENT",
            "O_EXCL_NOFOLLOW",
            "WRITE_FSYNC_RELOAD",
            "MODE0444_NLINK1",
            "NO_EXTRA_PATH",
            "IMMUTABLE_AFTER_CLOSE",
        ],
        "REJECTION_ONLY",
    ],
    [
        "Z.OP.CHILD_LIFECYCLE_FSM_MODEL_V1",
        "LITERAL_PROCESS_TRACE",
        [
            "ONE_LAUNCH",
            "EOF",
            "EXIT",
            "WAIT",
            "TERMINATE_WAIT_KILL_WAIT",
            "REAP",
            "PROCESS_GROUP_EMPTY",
        ],
        "PROCESS_CLOSURE_VALUE",
    ],
    [
        "Z.OP.STAGE_EDGE_FSM_MODEL_V1",
        "LITERAL_AUTHORITY_EDGE",
        [
            "EXACT_BARRIER_OBSERVER_SEED_OPEN_PARENT_TERMINAL",
            "NO_REPLAY_NO_SKIP_NO_REORDER",
        ],
        "REJECTION_ONLY",
    ],
]
COMPATIBILITY_OPERATION_BY_CASE_FAMILY: Final = {
    "JSON": "Z.OP.RAWJSON_DECODE_V1",
    "PROJECT": "Z.OP.NAMED_SIX_FIELD_PROJECTION_V1",
    "EQUALITY": "Z.OP.EXACT_RELATION_V1",
    "UNICODE": "Z.OP.UNICODE_NORMALIZE_V1",
    "STRING": "Z.OP.ASCII_PATH_GRAMMAR_V1",
    "REGEX-DIAGNOSTIC": "Z.OP.REGEX_DIAGNOSTIC_V1",
    "HASH": "Z.OP.LOWER_HEX64_SHAPE_V1",
    "INTEGER": "Z.OP.EXACT_INTEGER_DOMAIN_V1",
    "FRAME": "Z.OP.FRAME_CODEC_MODEL_V1",
    "ACK": "Z.OP.ACK_FSM_MODEL_V1",
    "FS": "Z.OP.POSIX_NOFOLLOW_TEMPFS_V1",
    "PACLET-FIXTURE": "Z.OP.SYNTHETIC_SOURCE_ENV_MODEL_V1",
    "FAKE": "Z.OP.FAKE_CHILD_IDENTITY_MODEL_V1",
    "PUBLISH": "Z.OP.OEXCL_PUBLICATION_MODEL_V1",
    "LIFECYCLE": "Z.OP.CHILD_LIFECYCLE_FSM_MODEL_V1",
    "STAGE-EDGE": "Z.OP.STAGE_EDGE_FSM_MODEL_V1",
}

EXPECTED_ARTIFACT_SCOPES: Final = {
    **{
        schema_id: "SESSION"
        for schema_id in (
            "child_observation_frame",
            "parent_event",
            "prefix_checkpoint",
            "final_stage_checkpoint",
            "ack",
            "stage_open_authority",
            "stage0_seed",
            "child_exit_authority",
            "lifecycle_receipt",
            "p17_closure",
            "terminal_manifest",
        )
    },
    "operation_terminal_manifest": "OPERATION_ROOT",
    "root_terminal_checkpoint": "OPERATION_ROOT",
    **{
        schema_id: "NESTED_SUPPORTING"
        for schema_id in (
            "FileIdentity",
            "DirectoryIdentity",
            "RootIdentity",
            "StreamIdentity",
            "ProcessClosure",
            "CallDirectorySealCloseout",
            "WriterHeldClosure",
            "WriterReleaseCloseout",
            "ResolvedEvidence",
            "ScienceCounters",
            "FailureClosure",
            "DispatchConsumption",
            "RunContract",
            "SourceLedger",
            "FailureTerminationAuthority",
            "PreRootControlFailure",
            "TerminalCheckpoint",
        )
    },
}

EXPECTED_P00_PREDICATES: Final = (
    (
        "RAW_BYTES",
        "Z.FIELD.REQUEST_RAW_SHA256",
        "Z.TYPE.HASH256",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_HASH256",
        "Z.VALUE.HASH256",
        "DERIVED",
        None,
        "Z.EXPR.P00.REQUEST_RAW",
        ("Z.EVID.P00.REQUEST_RAW", "Z.EVID.P00.DISPATCH"),
    ),
    (
        "NO_DUPLICATE_MEMBER",
        "Z.FIELD.DUPLICATE_MEMBER_FREE",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        True,
        None,
        ("Z.EVID.P00.REQUEST_RAW", "Z.EVID.P00.STRICT_PARSE"),
    ),
    (
        "CANONICAL_BYTES",
        "Z.FIELD.REQUEST_CANONICAL_SHA256",
        "Z.TYPE.HASH256",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_HASH256",
        "Z.VALUE.HASH256",
        "DERIVED",
        None,
        "Z.EXPR.P00.CANONICAL",
        ("Z.EVID.P00.REQUEST_RAW", "Z.EVID.P00.CANONICAL_REQUEST"),
    ),
    (
        "DISPATCH_IDENTITY",
        "Z.FIELD.DISPATCH_FILE_IDENTITY_SHA256",
        "Z.TYPE.HASH256",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_HASH256",
        "Z.VALUE.HASH256",
        "DERIVED",
        None,
        "Z.EXPR.P00.DISPATCH",
        ("Z.EVID.P00.DISPATCH", "Z.EVID.P00.DISPATCH_CONSUMPTION"),
    ),
    (
        "ROOT_IDENTITY",
        "Z.FIELD.ROOT_IDENTITY_SHA256",
        "Z.TYPE.HASH256",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_HASH256",
        "Z.VALUE.HASH256",
        "DERIVED",
        None,
        "Z.EXPR.P00.ROOT",
        ("Z.EVID.P00.ROOT", "Z.EVID.P00.DISPATCH_CONSUMPTION"),
    ),
)

EXPECTED_P17_PREDICATES: Final = (
    (
        "RETURN_CODE",
        "Z.FIELD.RETURN_CODE",
        "Z.TYPE.INT",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_INT",
        "Z.VALUE.INT",
        "LITERAL",
        0,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT"),
    ),
    (
        "SIGNAL",
        "Z.FIELD.SIGNAL_OR_NULL",
        "Z.TYPE.INT",
        True,
        "Z.NULL.IS_NULL",
        "Z.CMP.EXACT_TAGGED",
        "Z.VALUE.OPTIONAL_INT",
        "LITERAL",
        None,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT"),
    ),
    (
        "TIMEOUT",
        "Z.FIELD.TIMED_OUT",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        False,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT"),
    ),
    (
        "WAITED",
        "Z.FIELD.WAITED",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        True,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT"),
    ),
    (
        "REAPED",
        "Z.FIELD.REAPED",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        True,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT"),
    ),
    (
        "PROCESS_GROUP_EMPTY",
        "Z.FIELD.PROCESS_GROUP_EMPTY",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        True,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT"),
    ),
    (
        "RAW_STDOUT_BOUND",
        "Z.FIELD.STDOUT_WITHIN_BOUND",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        True,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT", "Z.EVID.P17.STDOUT"),
    ),
    (
        "RAW_STDERR_BOUND",
        "Z.FIELD.STDERR_WITHIN_BOUND",
        "Z.TYPE.BOOL",
        False,
        "Z.NULL.NEVER",
        "Z.CMP.EXACT_BOOL",
        "Z.VALUE.BOOL",
        "LITERAL",
        True,
        None,
        ("Z.EVID.P17.EXIT", "Z.EVID.P17.RECEIPT", "Z.EVID.P17.STDERR"),
    ),
)

TOP_LEVEL_KEYS: Final = frozenset(
    {
        "schema",
        "gate_id",
        "spec_revision",
        "canonical_codec",
        "type_registry",
        "json_shape_registry",
        "value_schema_registry",
        "algorithm_registry",
        "policy_registry",
        "null_rule_registry",
        "null_matrix_registry",
        "fixture_constructor_registry",
        "selector_registry",
        "catalog_registry",
        "reason_code_registry",
        "observer_registry",
        "executor_registry",
        "comparison_registry",
        "expected_expression_registry",
        "evidence_input_registry",
        "identity_policy_registry",
        "path_expression_registry",
        "immutable_inputs",
        "stages",
        "operations",
        "call_plans",
        "predicate_families",
        "artifact_schemas",
        "digest_nodes",
        "state_machine",
        "path_grammar",
        "authority_progression",
        "conformance_vector_registry",
        "conformance_vector_plans",
        "mutation_operator_registry",
        "mutation_plans",
        "generated_output_plan",
        "resource_limits",
        "nonclaims",
    }
)

REGISTRY_ROW_FIELDS: Final = {
    "type_registry": (
        "type_id",
        "wire_tag",
        "json_shape_id",
        "python_type_predicate_id",
        "wolfram_head_predicate_id",
        "canonicalizer_id",
        "domain_expression_id",
        "nullable",
        "ordered_mutation_operator_ids",
    ),
    "json_shape_registry": (
        "json_shape_id",
        "shape_kind",
        "exact_length_or_null",
        "ordered_member_schema_ids_or_null",
        "additional_members_allowed",
        "duplicate_members_allowed",
        "number_token_policy_id_or_null",
    ),
    "value_schema_registry": (
        "value_schema_id",
        "type_id",
        "nullable",
        "null_rule_id",
        "element_schema_id_or_null",
        "exact_length_or_null",
        "minimum_or_null",
        "maximum_or_null",
        "enum_values_or_null",
        "field_schema_ids_or_null",
    ),
    "algorithm_registry": (
        "algorithm_id",
        "algorithm_kind",
        "ordered_input_value_schema_ids",
        "output_value_schema_id",
        "closed_typed_ast_or_literal_table",
        "null_rule_id",
        "ordered_success_reason_codes",
        "ordered_failure_reason_codes",
        "science_capable",
    ),
    "policy_registry": (
        "policy_id",
        "policy_kind",
        "ordered_input_schema_ids",
        "literal_payload_schema_id",
        "literal_payload",
        "decision_expression_id_or_null",
        "output_schema_id",
        "ordered_failure_reason_codes",
    ),
    "null_rule_registry": (
        "null_rule_id",
        "null_matrix_id",
        "row_ordinal",
        "ordered_operand_null_bitmap",
        "resulting_outcome",
        "resulting_value_or_null",
        "reason_code",
    ),
    "null_matrix_registry": (
        "null_matrix_id",
        "comparison_id",
        "operand_count",
        "ordered_null_rule_ids",
        "required_bitmap_count",
        "bitmap_order",
    ),
    "fixture_constructor_registry": (
        "constructor_id",
        "constructor_kind",
        "ordered_input_schema_ids",
        "output_schema_id",
        "algorithm_id",
        "literal_parameters",
        "expected_output_authority_sha256",
    ),
    "selector_registry": (
        "selector_id",
        "input_catalog_id",
        "output_row_kind",
        "closed_typed_selector_ast",
        "ordered_result_policy_id",
        "expected_cardinality_expression_id",
    ),
    "catalog_registry": (
        "catalog_id",
        "row_value_schema_id",
        "ordered_row_source_id",
        "expected_row_count_expression_id",
        "ordered_row_digest_node_id",
    ),
    "reason_code_registry": (
        "reason_code",
        "reason_class",
        "terminality",
        "earliest_rejection_state",
        "science_claim_permitted",
    ),
    "observer_registry": (
        "observer_id",
        "actor",
        "source_kind",
        "observation_algorithm_id",
        "output_value_schema_id",
        "ordered_default_evidence_plan_ids",
        "science_capable",
    ),
    "executor_registry": (
        "executor_id",
        "runtime_identity_id",
        "entrypoint_id",
        "argv_template_id",
        "cwd_policy_id",
        "environment_policy_id",
        "callgraph_allowlist_id",
        "stdout_protocol_id",
        "science_capable",
    ),
    "comparison_registry": (
        "comparison_id",
        "left_value_schema_id",
        "right_value_schema_id",
        "operator_id",
        "null_matrix_id",
        "tolerance_authority_id_or_null",
        "result_schema_id",
        "pass_result_literal",
        "pass_reason_code",
        "fail_reason_code",
        "indeterminate_reason_code",
    ),
    "expected_expression_registry": (
        "expression_id",
        "result_value_schema_id",
        "typed_ast",
        "ordered_dependency_ids",
    ),
    "evidence_input_registry": (
        "evidence_plan_id",
        "role",
        "kind",
        "path_expression_id",
        "identity_policy_id",
        "required_digest_node_id",
    ),
    "identity_policy_registry": (
        "identity_policy_id",
        "allowed_kind",
        "require_nofollow",
        "required_mode_or_null",
        "required_nlink_or_null",
        "require_device_inode",
        "require_size",
        "require_content_sha256",
        "alias_policy_id",
        "start_end_policy_id",
    ),
    "path_expression_registry": (
        "path_expression_id",
        "base_authority_id",
        "ordered_literal_and_typed_segments",
        "normalization_policy_id",
        "direct_child_required",
        "namespace_regex_id",
    ),
    "conformance_vector_registry": (
        "vector_id",
        "vector_plan_id",
        "vector_ordinal",
        "scope_id",
        "initial_authority_fixture_ids",
        "operation_or_schema_id",
        "typed_input_values",
        "expected_encoded_bytes",
        "expected_artifact_or_wire_sha256",
        "expected_disposition",
        "expected_reason_code",
        "expected_terminal_state",
        "expected_science_counters",
    ),
    "mutation_operator_registry": (
        "operator_id",
        "applicable_target_kinds",
        "applicable_type_ids",
        "parameter_schema_id",
        "exact_transform_algorithm_id",
        "output_canonicality",
        "default_disposition",
        "default_reason_code",
        "earliest_rejection_state",
    ),
}

REGISTRY_ID_FIELDS: Final = {
    name: fields[0] for name, fields in REGISTRY_ROW_FIELDS.items()
}

CONFORMANCE_PLAN_FIELDS: Final = (
    "vector_plan_id",
    "expansion_axis_ids",
    "expansion_axis_values",
    "expansion_order",
    "fixture_constructor_id",
    "expected_constructor_id",
    "required_coverage_ids",
)

MUTATION_PLAN_FIELDS: Final = (
    "mutation_plan_id",
    "source_vector_selector_id",
    "target_selector_id",
    "ordered_operator_ids",
    "parameter_expansion_values",
    "rehash_descendants",
    "expected_disposition_override_or_null",
    "expected_reason_override_or_null",
)

PRIMARY_SCHEMA_IDS: Final = (
    "child_observation_frame",
    "parent_event",
    "prefix_checkpoint",
    "final_stage_checkpoint",
    "ack",
    "stage_open_authority",
    "stage0_seed",
    "child_exit_authority",
    "lifecycle_receipt",
    "p17_closure",
    "terminal_manifest",
    "operation_terminal_manifest",
    "root_terminal_checkpoint",
)

NESTED_SCHEMA_IDS: Final = (
    "FileIdentity",
    "DirectoryIdentity",
    "RootIdentity",
    "StreamIdentity",
    "ProcessClosure",
    "CallDirectorySealCloseout",
    "WriterHeldClosure",
    "WriterReleaseCloseout",
    "ResolvedEvidence",
    "ScienceCounters",
    "FailureClosure",
    "DispatchConsumption",
    "RunContract",
    "SourceLedger",
    "FailureTerminationAuthority",
    "PreRootControlFailure",
    "TerminalCheckpoint",
)

REQUIRED_DIGEST_NODE_IDS: Final = (
    "predicate_row",
    "call_plan_entry",
    "session",
    "ordered_predicate_ids",
    "ordered_event_authorities",
    "observer_plan",
    "path_grammar",
    "zero_event_chain_seed",
    "event",
    "prefix_chain",
    "stage_final",
    "stage_open",
    "child_exit",
    "failure_termination",
    "lifecycle_receipt",
    "p17_closure",
    "call_premanifest_inventory",
    "terminal_manifest",
    "call_postmanifest_inventory",
    "call_terminal_checkpoint",
    "call_directory_seal_closeout",
    "ordered_call_terminal_chain",
    "operation_premanifest_inventory",
    "operation_terminal_manifest",
    "operation_postmanifest_inventory",
    "writer_held_closure",
    "root_terminal_checkpoint",
    "writer_release_closeout",
)

PREDICATE_ROW_FIELDS: Final = (
    "predicate_id",
    "predicate_row_revision",
    "operation",
    "call_ordinal",
    "call_key_digest",
    "axis_bindings",
    "record_ordinal_or_null",
    "stage_ordinal",
    "stage_id",
    "stage_instance_ordinal",
    "operation_instance_ordinal",
    "global_instance_ordinal",
    "owner",
    "observer_id",
    "executor_id",
    "field_id",
    "value_type_id",
    "nullable",
    "null_rule_id",
    "comparison_id",
    "expected_value_schema_id",
    "expected_kind",
    "expected_literal_or_null",
    "expected_expression_or_null",
    "ordered_evidence_plan",
    "science_capable",
)

ARTIFACT_FIELD_FIELDS: Final = (
    "name",
    "value_schema_id",
    "value_source_kind",
    "value_rule",
    "ordered_digest_dependency_ids",
)

ARTIFACT_SOURCE_AUTHORITY_PREFIX: Final = "ARTIFACT_SOURCE:"
ARTIFACT_SELF_REFERENCE_PREFIX: Final = "ARTIFACT_FIELD:"

ARTIFACT_SOURCE_EVIDENCE_BY_KIND: Final = {
    "DERIVED_EXPRESSION": "Z.EVID.RUNTIME",
    "PARENT_OBSERVATION": "Z.EVID.P17.RECEIPT",
    "CHILD_OBSERVATION": "Z.EVID.P17.STDOUT",
    "NESTED_AUTHORITY": "Z.EVID.RUNTIME",
}

ARTIFACT_DERIVATION_DIGEST_BY_SCHEMA: Final = {
    "child_observation_frame": "session",
    "parent_event": "event",
    "prefix_checkpoint": "prefix_chain",
    "final_stage_checkpoint": "stage_final",
    "ack": "prefix_chain",
    "stage_open_authority": "stage_open",
    "stage0_seed": "zero_event_chain_seed",
    "child_exit_authority": "child_exit",
    "p17_closure": "p17_closure",
    "terminal_manifest": "terminal_manifest",
    "operation_terminal_manifest": "operation_terminal_manifest",
    "root_terminal_checkpoint": "root_terminal_checkpoint",
    "CallDirectorySealCloseout": "call_directory_seal_closeout",
    "ResolvedEvidence": "event",
    "ScienceCounters": "event",
    "FailureClosure": "failure_termination",
    "DispatchConsumption": "session",
    "RunContract": "session",
    "SourceLedger": "event",
    "FailureTerminationAuthority": "failure_termination",
    "PreRootControlFailure": "failure_termination",
    "TerminalCheckpoint": "call_terminal_checkpoint",
}

ARTIFACT_PARENT_OBSERVER_BY_SCHEMA: Final = {
    "lifecycle_receipt": "Z.OBS.PY_CHILD_LIFECYCLE_V1",
    "FileIdentity": "Z.OBS.PY_POSIX_NOFOLLOW_V1",
    "DirectoryIdentity": "Z.OBS.PY_POSIX_NOFOLLOW_V1",
    "RootIdentity": "Z.OBS.PY_POSIX_NOFOLLOW_V1",
    "StreamIdentity": "Z.OBS.PY_RAW_STREAM_V1",
    "ProcessClosure": "Z.OBS.PY_CHILD_LIFECYCLE_V1",
    "WriterHeldClosure": "Z.OBS.PY_POSIX_NOFOLLOW_V1",
    "WriterReleaseCloseout": "Z.OBS.PY_POSIX_NOFOLLOW_V1",
}

SESSION_PREFIX: Final = (
    "schema_id",
    "schema_revision",
    "bundle_root",
    "gate_id",
    "operation",
    "call_ordinal",
    "call_plan_entry_sha256",
    "session_sha256",
    "dispatch_sha256",
    "request_sha256",
)

OPERATION_ROOT_PREFIX: Final = (
    "schema_id",
    "schema_revision",
    "bundle_root",
    "gate_id",
    "operation",
    "dispatch_consumption_sha256",
    "run_contract_sha256",
    "root_identity_sha256",
)

PRIMARY_SCHEMA_SUFFIXES: Final = {
    "child_observation_frame": (
        "frame_sequence",
        "proposed_event_sequence",
        "stage_ordinal",
        "stage_id",
        "frame_kind",
        "predicate_or_barrier_id",
        "predicate_row_sha256_or_null",
        "record_ordinal_or_null",
        "field_id",
        "observer_id",
        "value_type_id",
        "observed_value",
        "stage_authority_sha256",
        "previous_child_frame_raw_sha256_or_null",
        "prior_prefix_checkpoint_sha256",
        "raw_stream_offset",
    ),
    "parent_event": (
        "event_sequence",
        "stage_ordinal",
        "stage_id",
        "predicate_id",
        "predicate_row_sha256",
        "stage_instance_ordinal",
        "owner",
        "observer_id",
        "executor_id",
        "field_id",
        "value_type_id",
        "comparison_id",
        "expected_value",
        "observed_value",
        "outcome",
        "child_frame_sequence_or_null",
        "child_frame_raw_sha256_or_null",
        "barrier_id_or_null",
        "stage_authority_sha256",
        "previous_event_authority_sha256_or_null",
        "ordered_resolved_evidence",
    ),
    "prefix_checkpoint": (
        "through_event_sequence",
        "total_event_count",
        "stage_event_count",
        "current_event_authority_sha256",
        "previous_prefix_authority_sha256_or_null",
        "prior_chain_sha256",
        "stage_authority_sha256",
        "prefix_chain_sha256",
        "all_pass_through",
    ),
    "final_stage_checkpoint": (
        "stage_ordinal",
        "stage_id",
        "stage_authority_sha256",
        "first_event_sequence",
        "last_event_sequence",
        "declared_event_count",
        "ordered_predicate_ids_sha256",
        "ordered_event_authorities_sha256",
        "first_prefix_authority_sha256",
        "last_prefix_authority_sha256",
        "prior_stage_final_authority_sha256_or_null",
        "barrier_id_or_null",
        "actor_profile_id",
        "all_pass",
    ),
    "ack": (
        "frame_sequence",
        "acknowledged_frame_raw_sha256",
        "committed_through_event_sequence",
        "durable_prefix_authority_sha256",
        "final_stage_authority_sha256_or_null",
        "next_stage_open_authority_sha256_or_null",
        "child_exit_authority_sha256_or_null",
        "expected_next_frame_sequence_or_null",
        "expected_next_event_sequence_or_null",
        "ack_kind",
        "outcome",
    ),
    "stage_open_authority": (
        "from_stage_ordinal",
        "from_stage_id",
        "from_stage_final_authority_sha256",
        "from_last_prefix_authority_sha256",
        "prior_open_or_seed_authority_sha256",
        "to_stage_ordinal",
        "to_stage_id",
        "actor_profile_id",
        "expected_first_frame_sequence_or_null",
        "expected_first_event_sequence",
        "expected_first_predicate_id",
        "declared_event_count",
        "ordered_predicate_ids_sha256",
        "barrier_id_or_null",
        "observer_plan_sha256",
        "path_grammar_sha256",
        "child_exit_authority_sha256_or_null",
        "lifecycle_receipt_authority_sha256_or_null",
        "status",
    ),
    "stage0_seed": (
        "root_relative_path",
        "root_identity_sha256",
        "dispatch_raw_sha256",
        "dispatch_canonical_sha256",
        "request_raw_sha256",
        "request_canonical_sha256",
        "run_contract_sha256",
        "source_start_plan_sha256",
        "prior_call_terminal_manifest_sha256_or_null",
        "prior_call_terminal_checkpoint_file_identity_sha256_or_null",
        "prior_call_directory_seal_closeout_authority_sha256_or_null",
        "expected_p00_predicate_ids_sha256",
        "expected_p00_count",
        "zero_event_chain_seed_sha256",
        "p00_observer_plan_sha256",
        "path_grammar_sha256",
        "status",
    ),
    "child_exit_authority": (
        "stage16_final_authority_sha256",
        "stage16_last_prefix_authority_sha256",
        "expected_return_code",
        "expected_first_p17_event_sequence",
        "stdout_raw_limit_bytes",
        "stderr_raw_limit_bytes",
        "exit_timeout_ns",
        "status",
    ),
    "lifecycle_receipt": (
        "exit_authority_kind",
        "child_exit_authority_sha256_or_null",
        "failure_termination_authority_sha256_or_null",
        "executable_file_identity",
        "argv",
        "cwd_directory_identity",
        "requested_environment",
        "observed_environment",
        "pid",
        "sid",
        "pgid",
        "started_monotonic_ns",
        "ended_monotonic_ns",
        "stdout_stream_identity",
        "stderr_stream_identity",
        "accepted_frame_count",
        "last_frame_raw_sha256_or_null",
        "eof_observed",
        "return_code",
        "signal_or_null",
        "timed_out",
        "terminate_attempted",
        "terminate_result",
        "kill_attempted",
        "kill_result",
        "waited",
        "reaped",
        "process_group_empty",
        "wait_error_count",
        "ordered_wait_error_digests",
        "related_process_closure",
        "writer_lock_identity",
        "status",
    ),
    "p17_closure": (
        "open17_authority_sha256",
        "child_exit_authority_sha256",
        "lifecycle_receipt_authority_sha256",
        "first_p17_event_sequence",
        "last_p17_event_sequence",
        "p17_event_count",
        "ordered_p17_predicate_ids_sha256",
        "ordered_p17_event_authorities_sha256",
        "last_p17_prefix_authority_sha256",
        "final17_authority_sha256",
        "all_pass",
    ),
    "terminal_manifest": (
        "terminal_kind",
        "spec_sha256",
        "generator_sha256",
        "generated_leaf_inventory_sha256",
        "root_identity_sha256",
        "stage0_seed_authority_sha256",
        "prior_call_terminal_manifest_sha256_or_null",
        "prior_call_terminal_checkpoint_file_identity_sha256_or_null",
        "prior_call_directory_seal_closeout_authority_sha256_or_null",
        "ordered_stage_final_authorities_sha256",
        "ordered_stage_open_authorities_sha256",
        "last_event_authority_sha256_or_null",
        "last_prefix_authority_sha256_or_null",
        "child_exit_authority_sha256_or_null",
        "lifecycle_receipt_authority_sha256_or_null",
        "p17_closure_authority_sha256_or_null",
        "result_artifact_identity_or_null",
        "failure_artifact_identity_or_null",
        "session_output_inventory_sha256",
        "premanifest_inventory_file_identity_sha256",
        "source_ledger_start_sha256",
        "source_ledger_end_sha256",
        "source_ledger_equal",
        "science_counters",
        "threshold_bundle_sha256_or_null",
        "certificate_bundle_sha256_or_null",
        "writer_held_closure_sha256",
        "process_closure_sha256",
        "nonclaims_sha256",
        "terminal_status",
    ),
    "operation_terminal_manifest": (
        "terminal_kind",
        "operation_plan_sha256",
        "expected_call_count",
        "completed_call_count",
        "failing_call_ordinal_or_null",
        "next_call_ordinal_or_null",
        "failure_closure_sha256_or_null",
        "ordered_call_plan_entry_sha256s",
        "ordered_call_session_ids",
        "ordered_call_terminal_checkpoint_file_identity_sha256s",
        "ordered_call_terminal_manifest_authority_sha256s",
        "ordered_call_directory_seal_closeout_authority_sha256s",
        "ordered_call_terminal_chain_sha256",
        "operation_premanifest_inventory_file_identity_sha256",
        "source_ledger_start_sha256",
        "source_ledger_end_sha256",
        "source_ledger_equal",
        "aggregate_science_counters",
        "threshold_bundle_sha256_or_null",
        "certificate_bundle_sha256_or_null",
        "writer_held_closure_sha256",
        "aggregate_process_closure_sha256",
        "nonclaims_sha256",
        "terminal_status",
    ),
    "root_terminal_checkpoint": (
        "operation_terminal_manifest_file_identity_sha256",
        "operation_premanifest_inventory_file_identity_sha256",
        "operation_postmanifest_precheckpoint_inventory_file_identity_sha256",
        "dispatch_consumption_file_identity_sha256",
        "writer_held_closure_sha256",
        "aggregate_process_closure_sha256",
        "terminal_kind",
        "seal_commit",
    ),
}

NESTED_SCHEMA_FIELDS: Final = {
    "FileIdentity": (
        "relative_path",
        "resolved_path",
        "kind",
        "device",
        "inode",
        "mode",
        "nlink",
        "size",
        "content_sha256",
        "nofollow_reopen",
        "alias_group_id",
    ),
    "DirectoryIdentity": (
        "relative_path",
        "resolved_path",
        "kind",
        "device",
        "inode",
        "mode",
        "nlink",
        "ordered_entry_names_sha256",
        "nofollow_reopen",
        "alias_group_id",
    ),
    "RootIdentity": (
        "resolved_root",
        "relative_root",
        "parent_directory_identity_sha256",
        "basename",
        "namespace_id",
        "device",
        "inode",
        "mode",
        "nlink",
        "direct_child",
        "no_alias",
    ),
    "StreamIdentity": (
        "role",
        "relative_path",
        "file_identity_sha256",
        "raw_size",
        "raw_content_sha256",
        "frame_count",
        "last_frame_sha256_or_null",
        "exactly_one_final_lf",
        "within_frozen_limit",
    ),
    "ProcessClosure": (
        "pid",
        "sid",
        "pgid",
        "return_code",
        "signal_or_null",
        "timed_out",
        "terminate_attempted",
        "terminate_result",
        "kill_attempted",
        "kill_result",
        "waited",
        "reaped",
        "process_group_empty",
        "wait_error_count",
        "ordered_wait_error_sha256s",
        "related_process_count",
    ),
    "CallDirectorySealCloseout": (
        "bundle_root",
        "gate_id",
        "operation",
        "call_ordinal",
        "session_sha256",
        "terminal_checkpoint_file_identity_sha256",
        "call_directory_identity_sha256_before_close",
        "call_directory_identity_sha256_after_close",
        "closed_mode",
        "directory_fsynced",
        "parent_directory_fsynced",
        "operation_lock_still_held",
        "post_close_mutation_count",
        "status",
    ),
    "WriterHeldClosure": (
        "lock_relative_path",
        "lock_file_identity_sha256",
        "flock_acquired",
        "exclusive_owner_pid",
        "exclusive_owner_sid",
        "exclusive_owner_pgid",
        "competing_writer_count",
        "lock_scope",
        "held_at_observation",
        "required_hold_through_root_checkpoint",
        "expected_release_after_root_close",
    ),
    "WriterReleaseCloseout": (
        "bundle_root",
        "gate_id",
        "operation",
        "dispatch_consumption_sha256",
        "root_terminal_checkpoint_file_identity_sha256",
        "lock_file_identity_sha256",
        "former_owner_pid",
        "former_owner_sid",
        "former_owner_pgid",
        "flock_released",
        "root_mode_after_close",
        "root_directory_identity_sha256_after_close",
        "active_writer_count_after_release",
        "related_process_count_after_release",
        "closeout_observer_id",
        "status",
    ),
    "ResolvedEvidence": (
        "plan_ordinal",
        "evidence_plan_id",
        "role",
        "kind",
        "relative_path",
        "resolved_identity_schema_id",
        "resolved_identity_authority_sha256",
        "content_sha256_or_null",
        "required_digest_authority_sha256",
        "identity_policy_result",
    ),
    "ScienceCounters": (
        "wolfram_kernel_launches",
        "bhpt_public_api_calls",
        "regge_wheeler_radial_calls",
        "external_api_calls",
        "solver_calls",
        "boundary_solutions",
        "overlap_records",
        "route_a_modes",
        "route_a_ladder_records",
        "route_u_modes",
        "route_u_precision_records",
        "route_b_modes",
        "route_b_records",
        "route_c_anchors",
        "route_c_api_calls",
        "route_c_boundary_solutions",
        "route_c_overlap_records",
    ),
    "FailureClosure": (
        "failure_class",
        "stage_ordinal_or_null",
        "predicate_id_or_null",
        "edge_id_or_null",
        "reason_code",
        "exception_type_or_null",
        "exception_message_sha256_or_null",
        "offending_raw_sha256_or_null",
        "last_frame_sha256_or_null",
        "last_event_authority_sha256_or_null",
        "last_prefix_authority_sha256_or_null",
        "last_stage_final_authority_sha256_or_null",
        "last_stage_open_authority_sha256_or_null",
        "failure_termination_authority_sha256_or_null",
        "lifecycle_receipt_authority_sha256_or_null",
        "resumable",
        "scientific_pass",
    ),
    "DispatchConsumption": (
        "dispatch_file_identity_sha256",
        "dispatch_raw_sha256",
        "dispatch_canonical_sha256",
        "attempt_ordinal",
        "operation",
        "exact_root",
        "prior_review_path",
        "prior_review_sha256",
        "package_sha256",
        "bundle_root",
        "executable_identity_sha256",
        "exact_argv",
        "exact_cwd_directory_identity_sha256",
        "requested_environment",
        "expected_observed_environment",
        "consumed_file_identity_sha256",
        "one_use",
        "consumed_before_child",
    ),
    "RunContract": (
        "gate_id",
        "operation",
        "bundle_root",
        "dispatch_consumption_sha256",
        "root_identity_sha256",
        "executable_identity_sha256",
        "exact_argv",
        "cwd_directory_identity_sha256",
        "requested_environment",
        "observed_environment_contract_sha256",
        "source_plan_sha256",
        "operation_plan_sha256",
        "resource_limits_sha256",
        "nonclaims_sha256",
    ),
    "SourceLedger": (
        "boundary_kind",
        "source_plan_sha256",
        "ordered_file_identity_authorities",
        "ordered_directory_identity_authorities",
        "wolfram_runtime_identity_sha256",
        "bhpt_snapshot_metadata_sha256",
        "bhpt_content_inventory_sha256",
        "bhpt_identity_inventory_sha256",
        "ordered_loaded_context_source_tuples",
        "ordered_dependency_tree_identities",
        "source_inventory_sha256",
        "compared_boundary_authority_sha256_or_null",
        "start_end_equal_or_null",
    ),
    "FailureTerminationAuthority": (
        "failure_closure_prefix_sha256",
        "pid",
        "sid",
        "pgid",
        "terminate_after_ns",
        "kill_after_ns",
        "stdout_limit",
        "stderr_limit",
        "expected_next_frame",
        "status",
    ),
    "PreRootControlFailure": (
        "schema_id",
        "schema_revision",
        "bundle_root",
        "gate_id",
        "operation",
        "package_checkpoint_file_identity_sha256",
        "package_review_file_identity_sha256",
        "implementation_review_file_identity_sha256_or_null",
        "prior_operation_review_file_identity_sha256_or_null",
        "dispatch_file_identity_sha256",
        "dispatch_consumed",
        "executable_file_identity_sha256",
        "exact_argv_sha256",
        "cwd_directory_identity_sha256",
        "requested_environment_sha256",
        "observed_environment_sha256",
        "requested_root",
        "root_created",
        "failure_stage",
        "reason_code",
        "related_process_count",
        "science_counters",
        "terminal_status",
    ),
    "TerminalCheckpoint": (
        "terminal_manifest_file_identity_sha256",
        "premanifest_inventory_file_identity_sha256",
        "postmanifest_precheckpoint_inventory_file_identity_sha256",
        "call_directory_identity_sha256_before_close",
        "expected_closed_call_directory_mode",
        "writer_held_closure_sha256",
        "process_closure_sha256",
        "terminal_kind",
        "seal_commit",
    ),
}

ALGORITHM_KINDS: Final = frozenset(
    {
        "PURE_TYPED_AST",
        "STRICT_JSON_DECODE",
        "CANONICAL_TAGGED_ENCODE",
        "SHA256_RAW_BYTES",
        "POSIX_LSTAT_NOFOLLOW",
        "POSIX_OPEN_NOFOLLOW_READ_HASH",
        "POSIX_DIRECTORY_INVENTORY",
        "POSIX_ALIAS_GRAPH",
        "RAW_STREAM_FRAME_DECODE",
        "PROCESS_LIFECYCLE_OBSERVE",
        "CANONICAL_DECIMAL_EVALUATE",
        "OBSERVATION_PROJECTION",
        "MUTATION_BYTE_TRANSFORM",
        "MUTATION_TYPED_ROW_TRANSFORM",
    }
)

POLICY_KINDS: Final = frozenset(
    {
        "RUNTIME_IDENTITY",
        "ENTRYPOINT",
        "ARGV_TEMPLATE",
        "CWD_DIRECTORY",
        "REQUESTED_ENVIRONMENT",
        "OBSERVED_ENVIRONMENT",
        "CALLGRAPH_ALLOWLIST",
        "STDOUT_PROTOCOL",
        "TOLERANCE_AUTHORITY",
        "ALIAS_POLICY",
        "START_END_POLICY",
        "PATH_BASE",
        "NORMALIZATION_POLICY",
        "NAMESPACE_FULLMATCH",
        "FILE_MODE_NLINK_POLICY",
        "RESOURCE_LIMIT",
        "NUMBER_TOKEN_POLICY",
        "ORDERED_RESULT_POLICY",
    }
)

AST_CONSTRUCTORS: Final = frozenset(
    {
        "CONST",
        "AUTHORITY_REF",
        "FIELD",
        "AXIS",
        "INDEX",
        "LENGTH",
        "HASH",
        "CONCAT",
        "AND",
        "OR",
        "NOT",
        "EQ",
        "LT",
        "LE",
        "ABS",
        "ADD",
        "SUBTRACT",
        "MULTIPLY",
        "DIVIDE",
        "SQUARE",
        "SQRT",
        "LN",
        "MAX",
        "MIN",
        "WRAP_TO_PI",
    }
)

SELECTOR_CONSTRUCTORS: Final = frozenset(
    {
        "CATALOG",
        "FIELD",
        "EQ",
        "LT",
        "AND",
        "OR",
        "NOT",
        "RANGE",
        "LENGTH",
        "ORDERED_PROJECT",
        "CONST",
    }
)


class AuthorityError(RuntimeError):
    """A fail-closed package-authority violation."""


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuthorityError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def canonical_object_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def compact_array_bytes(value: Sequence[Any]) -> bytes:
    if not isinstance(value, (list, tuple)):
        raise AuthorityError("compact authority payload must be an array")
    return (
        json.dumps(
            list(value),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def S(value: str) -> list[Any]:
    if type(value) is not str:
        raise AuthorityError("S requires an exact string")
    return ["s", value]


def I(value: int) -> list[Any]:  # noqa: E743 - frozen tagged-integer constructor
    if type(value) is not int:
        raise AuthorityError("I requires a plain integer; bool is forbidden")
    return ["i", str(value)]


def B(value: bool) -> list[Any]:
    if type(value) is not bool:
        raise AuthorityError("B requires a boolean")
    return ["b", value]


def N() -> list[Any]:
    return ["n"]


def H(value: str) -> list[Any]:
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise AuthorityError("H requires exactly 64 lowercase hexadecimal characters")
    return ["h", value]


_CANONICAL_DECIMAL_RE = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?e[+-](?:0|[1-9][0-9]*)"
)


def D(value: str) -> list[Any]:
    if (
        type(value) is not str
        or _CANONICAL_DECIMAL_RE.fullmatch(value) is None
        or value.startswith("-0")
    ):
        raise AuthorityError("D requires a canonical arbitrary-precision decimal")
    return ["d", value]


def A(schema_id: str, *members: Sequence[Any]) -> list[Any]:
    if type(schema_id) is not str or not schema_id:
        raise AuthorityError("A requires a nonempty schema ID")
    result: list[Any] = ["a", schema_id]
    for ordinal, member in enumerate(members):
        _validate_tagged_value(member, f"{schema_id}[{ordinal}]")
        result.append(list(member))
    return result


def _validate_tagged_value(value: Any, context: str = "tagged value") -> None:
    if type(value) is not list or not value or type(value[0]) is not str:
        raise AuthorityError(f"{context} is not an explicitly tagged value")
    tag = value[0]
    if tag == "s":
        if len(value) != 2 or type(value[1]) is not str:
            raise AuthorityError(f"invalid S value in {context}")
        return
    if tag == "i":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or re.fullmatch(r"0|-?[1-9][0-9]*", value[1]) is None
        ):
            raise AuthorityError(f"invalid I value in {context}")
        return
    if tag == "b":
        if len(value) != 2 or type(value[1]) is not bool:
            raise AuthorityError(f"invalid B value in {context}")
        return
    if tag == "n":
        if value != ["n"]:
            raise AuthorityError(f"invalid N value in {context}")
        return
    if tag == "h":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or re.fullmatch(r"[0-9a-f]{64}", value[1]) is None
        ):
            raise AuthorityError(f"invalid H value in {context}")
        return
    if tag == "d":
        D(value[1] if len(value) == 2 else "")
        return
    if tag == "a":
        if len(value) < 2 or type(value[1]) is not str or not value[1]:
            raise AuthorityError(f"invalid A header in {context}")
        for ordinal, member in enumerate(value[2:]):
            _validate_tagged_value(member, f"{context}.{value[1]}[{ordinal}]")
        return
    raise AuthorityError(f"unknown authority tag {tag!r} in {context}")


def tagged_array_bytes(values: Sequence[Sequence[Any]]) -> bytes:
    tagged = list(values)
    for ordinal, value in enumerate(tagged):
        _validate_tagged_value(value, f"tagged array[{ordinal}]")
    return compact_array_bytes(tagged)


def enc(
    schema_id: str, revision: int, tagged_payload: Sequence[Sequence[Any]]
) -> bytes:
    if type(revision) is not int or revision < 0:
        raise AuthorityError("schema revision must be a nonnegative plain integer")
    return tagged_array_bytes([S(schema_id), I(revision), *tagged_payload])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _regular_identity(
    path: Path, *, expected_sha256: str | None = None
) -> dict[str, Any]:
    lexical = path.absolute()
    if lexical.is_symlink():
        raise AuthorityError(f"immutable input is a symlink: {path}")
    resolved = lexical.resolve(strict=True)
    info_before = resolved.lstat()
    if not stat.S_ISREG(info_before.st_mode) or info_before.st_nlink != 1:
        raise AuthorityError(f"immutable input is not regular/nlink1: {path}")
    digest = hashlib.sha256()
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(resolved, flags)
    try:
        opened = os.fstat(fd)
        if (opened.st_dev, opened.st_ino) != (info_before.st_dev, info_before.st_ino):
            raise AuthorityError(f"immutable input changed before open: {path}")
        while True:
            block = os.read(fd, 1024 * 1024)
            if not block:
                break
            digest.update(block)
        opened_after = os.fstat(fd)
    finally:
        os.close(fd)
    info_after = resolved.lstat()

    def stat_tuple(item: os.stat_result) -> tuple[int, int, int, int, int, int]:
        return (
            item.st_dev,
            item.st_ino,
            item.st_mode,
            item.st_nlink,
            item.st_size,
            item.st_mtime_ns,
        )

    if stat_tuple(info_before) != stat_tuple(opened_after) or stat_tuple(
        info_before
    ) != stat_tuple(info_after):
        raise AuthorityError(f"immutable input drift during read: {path}")
    observed_sha = digest.hexdigest()
    if expected_sha256 is not None and observed_sha != expected_sha256:
        raise AuthorityError(f"immutable input SHA drift: {path}")
    return {
        "path": str(path),
        "resolved_path": str(resolved),
        "sha256": observed_sha,
        "size": info_before.st_size,
        "mode": stat.S_IMODE(info_before.st_mode),
        "nlink": info_before.st_nlink,
        "device": info_before.st_dev,
        "inode": info_before.st_ino,
    }


def _immutable_input_ledger(spec: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    immutable = spec["immutable_inputs"]
    _require_exact_keys(
        immutable,
        {
            "accepted_analysis",
            "accepted_archive",
            "bhpt_snapshot",
            "denied_science_control",
            "design_prompt",
            "external_runtime",
            "helper_import_graph",
            "helper_symbol_edges",
            "liveness",
            "mpmath_overlay",
            "project_import_closure",
            "protected_sources",
            "runtime_authority_input_catalog",
            "science_graph",
            "science_observation_helpers",
            "threat_model_only",
            "threat_nonpromotion_rules",
            "v3_authorities",
        },
        "immutable inputs",
    )
    records: list[dict[str, Any]] = []
    for key in ("accepted_analysis", "accepted_archive", "design_prompt", "liveness"):
        row = immutable[key]
        _require_exact_keys(row, {"path", "sha256"}, f"immutable {key}")
        records.append(
            _regular_identity(repo_root / row["path"], expected_sha256=row["sha256"])
        )
    for path, digest in [*immutable["v3_authorities"], *immutable["protected_sources"]]:
        records.append(_regular_identity(repo_root / path, expected_sha256=digest))

    runtime = immutable["external_runtime"]
    _require_exact_keys(runtime, {"cpython314", "wolfram_kernel"}, "external runtime")
    python_row = runtime["cpython314"]
    wolfram_row = runtime["wolfram_kernel"]
    _require_exact_keys(
        python_row, {"path", "sha256", "version", "cache_tag"}, "CPython authority"
    )
    _require_exact_keys(wolfram_row, {"path", "sha256", "version"}, "Wolfram authority")
    python_identity = _regular_identity(
        Path(python_row["path"]), expected_sha256=python_row["sha256"]
    )
    wolfram_identity = _regular_identity(
        Path(wolfram_row["path"]), expected_sha256=wolfram_row["sha256"]
    )
    if (python_identity["mode"], python_identity["nlink"], python_identity["size"]) != (
        0o755,
        1,
        52_448,
    ):
        raise AuthorityError("CPython runtime stat identity drift")
    if (
        wolfram_identity["mode"],
        wolfram_identity["nlink"],
        wolfram_identity["size"],
    ) != (0o755, 1, 167_488):
        raise AuthorityError("Wolfram runtime stat identity drift")
    if (
        platform.python_version() != python_row["version"]
        or sys.implementation.cache_tag != python_row["cache_tag"]
    ):
        raise AuthorityError("running CPython authority mismatch")
    if Path(sys.executable).resolve(strict=True) != Path(python_row["path"]).resolve(
        strict=True
    ):
        raise AuthorityError("generator was not run with the frozen CPython executable")
    records.extend((python_identity, wolfram_identity))

    def imported_modules(path: Path) -> list[str]:
        try:
            tree = ast.parse(path.read_bytes(), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            raise AuthorityError(f"cannot parse source import closure: {path}") from exc
        observed: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                observed.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                observed.append("." * node.level + (node.module or ""))
            elif isinstance(node, ast.Call) and (
                (isinstance(node.func, ast.Name) and node.func.id == "__import__")
                or (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "importlib"
                )
            ):
                raise AuthorityError(f"dynamic import is forbidden: {path}")
        return observed

    helper_records: list[dict[str, Any]] = []
    helper_import_by_path = {row[0]: row[1] for row in immutable["helper_import_graph"]}
    if len(helper_import_by_path) != 3:
        raise AuthorityError("science helper import graph cardinality drift")
    for ordinal, row in enumerate(immutable["science_observation_helpers"]):
        if type(row) is not list or len(row) != 9:
            raise AuthorityError(f"malformed science helper row: {ordinal}")
        (
            relative,
            expected_sha,
            expected_size,
            expected_mode,
            expected_nlink,
            role,
            observation_only,
            allowed_symbols,
            forbidden_symbols,
        ) = row
        if (
            type(role) is not str
            or observation_only is not True
            or type(allowed_symbols) is not list
            or type(forbidden_symbols) is not list
            or relative not in helper_import_by_path
        ):
            raise AuthorityError(f"science helper authority row drift: {relative}")
        identity = _regular_identity(repo_root / relative, expected_sha256=expected_sha)
        if (identity["size"], identity["mode"], identity["nlink"]) != (
            expected_size,
            expected_mode,
            expected_nlink,
        ):
            raise AuthorityError(f"science helper stat drift: {relative}")
        if imported_modules(repo_root / relative) != helper_import_by_path[relative]:
            raise AuthorityError(f"science helper import graph drift: {relative}")
        source = (repo_root / relative).read_text(encoding="utf-8")
        parsed = ast.parse(source, filename=relative)
        defined = {
            node.name
            for node in parsed.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        if not set(allowed_symbols).issubset(defined) or not set(
            forbidden_symbols
        ).issubset(defined):
            raise AuthorityError(f"science helper symbol allow/deny drift: {relative}")
        helper_records.append(identity)
    records.extend(helper_records)

    symbol_edges = immutable["helper_symbol_edges"]
    if symbol_edges != [
        [
            "src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py",
            "src/schwgw/validation/phase6_mpmath_radial.py",
            [
                "MpmathMode",
                "MpmathRadialContractError",
                "MpmathSolveConfig",
                "_integrate_state_to_radii",
                "_integrate_to_radii",
                "independent_jost_basis",
                "schwarzschild_rstar",
            ],
        ]
    ]:
        raise AuthorityError("science helper symbol-edge contract drift")
    hp_path = repo_root / symbol_edges[0][0]
    hp_tree = ast.parse(hp_path.read_bytes(), filename=str(hp_path))
    observed_imported_symbols: list[str] = []
    for node in hp_tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "schwgw.validation.phase6_mpmath_radial"
        ):
            observed_imported_symbols.extend(alias.name for alias in node.names)
    if observed_imported_symbols != symbol_edges[0][2]:
        raise AuthorityError("science helper imported-symbol edge drift")

    project_import_records: list[dict[str, Any]] = []
    for ordinal, row in enumerate(immutable["project_import_closure"]):
        if type(row) is not list or len(row) != 6:
            raise AuthorityError(f"malformed project import row: {ordinal}")
        relative, expected_sha, size, mode, nlink, expected_imports = row
        identity = _regular_identity(repo_root / relative, expected_sha256=expected_sha)
        if (identity["size"], identity["mode"], identity["nlink"]) != (
            size,
            mode,
            nlink,
        ) or imported_modules(repo_root / relative) != expected_imports:
            raise AuthorityError(f"project import closure drift: {relative}")
        project_import_records.append(identity)
    records.extend(project_import_records)

    denied = immutable["denied_science_control"]
    if type(denied) is not list or len(denied) != 7:
        raise AuthorityError("denied science control row malformed")
    denied_relative, denied_sha, denied_size, denied_mode, denied_nlink, flag, use = (
        denied
    )
    if flag is not False or use != "THREAT_MODEL_ONLY":
        raise AuthorityError("denied science control promotion drift")
    denied_identity = _regular_identity(
        repo_root / denied_relative, expected_sha256=denied_sha
    )
    if (
        denied_identity["size"],
        denied_identity["mode"],
        denied_identity["nlink"],
    ) != (denied_size, denied_mode, denied_nlink):
        raise AuthorityError("denied science control stat drift")

    overlay = immutable["mpmath_overlay"]
    _require_exact_keys(
        overlay,
        {
            "backend_environment",
            "canonical_content_inventory_sha256",
            "canonical_directory_inventory_sha256",
            "canonical_identity_inventory_sha256",
            "canonical_tree_sha256",
            "directory_count",
            "directory_mode",
            "expected_backend",
            "file_count",
            "forbidden_import_candidates",
            "inventory_order",
            "path",
            "pre_science_requirements",
            "regular_file_mode",
            "regular_file_nlink",
            "total_file_bytes",
            "version",
        },
        "mpmath overlay authority",
    )
    if (
        overlay["backend_environment"]
        != [["MPMATH_NOGMPY", "1"], ["PYTHONNOUSERSITE", "1"]]
        or overlay["expected_backend"] != "python"
        or overlay["forbidden_import_candidates"] != ["gmp", "gmpy2"]
        or overlay["inventory_order"] != "PYTHON_PATH_PART_LEXICOGRAPHIC"
        or overlay["pre_science_requirements"]
        != [
            "MPMATH_NOGMPY_EQUALS_1",
            "MPMATH_BACKEND_EQUALS_PYTHON",
            "GMP_AND_GMPY2_NOT_LOADED_OR_IMPORTABLE_UNDER_EXACT_CLEAN_PATH",
        ]
    ):
        raise AuthorityError("mpmath backend authority drift")
    overlay_root = repo_root / overlay["path"]
    if (
        overlay_root.is_symlink()
        or overlay_root.resolve(strict=True) != overlay_root.absolute()
    ):
        raise AuthorityError("mpmath overlay root is missing or aliased")
    overlay_files: list[dict[str, Any]] = []
    overlay_directories: list[dict[str, Any]] = []
    for path in [overlay_root, *sorted(overlay_root.rglob("*"))]:
        info = path.lstat()
        relative = (
            "." if path == overlay_root else path.relative_to(overlay_root).as_posix()
        )
        if stat.S_ISLNK(info.st_mode) or (
            not stat.S_ISREG(info.st_mode) and not stat.S_ISDIR(info.st_mode)
        ):
            raise AuthorityError(f"mpmath overlay has aliased/special node: {relative}")
        if stat.S_ISREG(info.st_mode):
            if (
                stat.S_IMODE(info.st_mode) != overlay["regular_file_mode"]
                or info.st_nlink != overlay["regular_file_nlink"]
            ):
                raise AuthorityError(f"mpmath overlay file stat drift: {relative}")
            overlay_files.append(
                {
                    "path": relative,
                    "sha256": sha256_file(path),
                    "size": info.st_size,
                    "mode": stat.S_IMODE(info.st_mode),
                    "nlink": info.st_nlink,
                }
            )
        else:
            if stat.S_IMODE(info.st_mode) != overlay["directory_mode"]:
                raise AuthorityError(f"mpmath overlay dir mode drift: {relative}")
            overlay_directories.append(
                {
                    "path": relative,
                    "mode": stat.S_IMODE(info.st_mode),
                    "nlink": info.st_nlink,
                }
            )
    overlay_content = [
        {key: row[key] for key in ("path", "sha256", "size")} for row in overlay_files
    ]
    overlay_digests = {
        "canonical_content_inventory_sha256": sha256_bytes(
            canonical_object_bytes(overlay_content)
        ),
        "canonical_identity_inventory_sha256": sha256_bytes(
            canonical_object_bytes(overlay_files)
        ),
        "canonical_directory_inventory_sha256": sha256_bytes(
            canonical_object_bytes(overlay_directories)
        ),
        "canonical_tree_sha256": sha256_bytes(
            canonical_object_bytes(
                {"files": overlay_files, "directories": overlay_directories}
            )
        ),
    }
    if any(overlay[key] != value for key, value in overlay_digests.items()) or (
        len(overlay_files),
        len(overlay_directories),
        sum(row["size"] for row in overlay_files),
    ) != (
        overlay["file_count"],
        overlay["directory_count"],
        overlay["total_file_bytes"],
    ):
        raise AuthorityError("mpmath overlay inventory drift")
    pyc_count = 0
    for row in overlay_files:
        relative = row["path"]
        if not relative.endswith(".cpython-314.pyc"):
            continue
        pyc_count += 1
        pyc_path = overlay_root / relative
        raw = pyc_path.read_bytes()
        if len(raw) < 16 or raw[:4] != importlib.util.MAGIC_NUMBER:
            raise AuthorityError(f"mpmath pyc magic/length drift: {relative}")
        flags = int.from_bytes(raw[4:8], "little")
        source_name = pyc_path.name.removesuffix(".cpython-314.pyc") + ".py"
        source_path = pyc_path.parent.parent / source_name
        if flags != 0 or not source_path.is_file() or source_path.is_symlink():
            raise AuthorityError(f"mpmath pyc source/flags drift: {relative}")
        source_info = source_path.stat()
        if (
            int.from_bytes(raw[8:12], "little") != int(source_info.st_mtime)
            or int.from_bytes(raw[12:16], "little") != source_info.st_size
        ):
            raise AuthorityError(f"mpmath pyc header/source drift: {relative}")
    if pyc_count != 53:
        raise AuthorityError("mpmath pyc cardinality drift")
    record_path = overlay_root / "mpmath-1.4.1.dist-info/RECORD"
    record_rows = list(csv.reader(record_path.read_text(encoding="utf-8").splitlines()))
    if len(record_rows) != 102 or len({row[0] for row in record_rows}) != 102:
        raise AuthorityError("mpmath dist-info RECORD cardinality drift")
    overlay_file_by_path = {row["path"]: row for row in overlay_files}
    for record in record_rows:
        if len(record) != 3 or record[0] not in overlay_file_by_path:
            raise AuthorityError("mpmath dist-info RECORD path/schema drift")
        expected = overlay_file_by_path[record[0]]
        if record[0] == "mpmath-1.4.1.dist-info/RECORD":
            if record[1:] != ["", ""]:
                raise AuthorityError("mpmath RECORD self-row drift")
            continue
        digest = "sha256=" + base64.urlsafe_b64encode(
            bytes.fromhex(expected["sha256"])
        ).decode("ascii").rstrip("=")
        if record[1] != digest or record[2] != str(expected["size"]):
            raise AuthorityError(f"mpmath RECORD identity drift: {record[0]}")
    explicit_search_path = [str(overlay_root), str(repo_root / "src")]
    forbidden_candidate_state = []
    for candidate in overlay["forbidden_import_candidates"]:
        found = importlib.machinery.PathFinder.find_spec(
            candidate, explicit_search_path
        )
        forbidden_candidate_state.append([candidate, found is None])
        if found is not None:
            raise AuthorityError(f"forbidden mpmath backend candidate: {candidate}")

    metadata_path = (
        repo_root
        / "runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json"
    )
    metadata_identity = _regular_identity(
        metadata_path, expected_sha256=immutable["bhpt_snapshot"]["metadata_sha256"]
    )
    metadata = strict_load_json(metadata_path, canonical=False)
    source_root = repo_root / metadata["restoration"]["root"]
    if (
        source_root.is_symlink()
        or source_root.resolve(strict=True) != source_root.absolute()
    ):
        raise AuthorityError("BHPT snapshot root is missing or aliased")
    expected_content = metadata["source_content_records"]
    if type(expected_content) is not list or len(expected_content) != 25:
        raise AuthorityError("BHPT snapshot content inventory cardinality mismatch")
    actual_nodes = list(source_root.rglob("*"))
    if any(node.is_symlink() for node in actual_nodes):
        raise AuthorityError("BHPT snapshot contains a symlink")
    if any(not node.is_file() and not node.is_dir() for node in actual_nodes):
        raise AuthorityError("BHPT snapshot contains a special node")
    actual_file_paths = sorted(
        node.relative_to(source_root).as_posix()
        for node in actual_nodes
        if node.is_file()
    )
    if actual_file_paths != sorted(row["path"] for row in expected_content):
        raise AuthorityError("BHPT snapshot file closure mismatch")
    file_records: list[dict[str, Any]] = []
    by_path = {row["path"]: row for row in expected_content}
    for relative in actual_file_paths:
        expected = by_path[relative]
        identity = _regular_identity(
            source_root / relative, expected_sha256=expected["sha256"]
        )
        if (identity["size"], identity["mode"], identity["nlink"]) != (
            expected["size"],
            0o444,
            1,
        ):
            raise AuthorityError(f"BHPT snapshot source stat drift: {relative}")
        file_records.append(
            {key: identity[key] for key in ("path", "sha256", "size", "mode", "nlink")}
        )
        file_records[-1]["path"] = relative
    directory_paths = sorted(
        ["."]
        + [
            node.relative_to(source_root).as_posix()
            for node in actual_nodes
            if node.is_dir()
        ]
    )
    if directory_paths != [".", "Kernel", "Kernel/MST", "Tests", "Tests/Correctness"]:
        raise AuthorityError("BHPT snapshot directory closure mismatch")
    directory_records = []
    for relative in directory_paths:
        path = source_root if relative == "." else source_root / relative
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o555:
            raise AuthorityError(f"BHPT directory mode drift: {relative}")
        directory_records.append(
            {
                "path": relative,
                "mode": stat.S_IMODE(info.st_mode),
                "nlink": info.st_nlink,
                "device": info.st_dev,
                "inode": info.st_ino,
            }
        )
    content_projection = [
        {"path": row["path"], "sha256": row["sha256"], "size": row["size"]}
        for row in file_records
    ]
    identity_projection = file_records
    content_sha = sha256_bytes(canonical_object_bytes(content_projection))
    identity_sha = sha256_bytes(canonical_object_bytes(identity_projection))
    if content_sha != immutable["bhpt_snapshot"]["content_inventory_sha256"]:
        raise AuthorityError("BHPT content projection digest drift")
    if identity_sha != immutable["bhpt_snapshot"]["identity_inventory_sha256"]:
        raise AuthorityError("BHPT identity projection digest drift")
    records.append(metadata_identity)

    threat_records = []
    for row in immutable["threat_model_only"]:
        if (
            type(row) is not list
            or len(row) != 6
            or row[4] is not False
            or row[5] != "THREAT_MODEL_ONLY"
        ):
            raise AuthorityError("malformed threat-only authority row")
        threat_id, path_or_null, kind, digest, _promotable, _use = row
        H(digest)
        if path_or_null is not None:
            path = repo_root / path_or_null
            identity = _regular_identity(path)
            if kind == "TREE_IDENTITY_DIGEST":
                if digest not in path.read_text(encoding="utf-8"):
                    raise AuthorityError(
                        f"threat tree identity not bound by archive: {threat_id}"
                    )
            elif identity["sha256"] != digest:
                raise AuthorityError(
                    f"threat-only artifact identity drift: {threat_id}"
                )
            threat_records.append(identity)
    ledger_payload = {
        "repo_records": records,
        "runtime_records": [python_identity, wolfram_identity],
        "bhpt_metadata": metadata_identity,
        "bhpt_files": file_records,
        "bhpt_directories": directory_records,
        "bhpt_content_inventory_sha256": content_sha,
        "bhpt_identity_inventory_sha256": identity_sha,
        "threat_records": threat_records,
        "science_helper_records": helper_records,
        "project_import_records": project_import_records,
        "denied_science_control": denied_identity,
        "mpmath_overlay": {
            "root": str(overlay_root),
            "file_count": len(overlay_files),
            "directory_count": len(overlay_directories),
            "total_file_bytes": sum(row["size"] for row in overlay_files),
            "pyc_count": pyc_count,
            "dist_info_record_count": len(record_rows),
            "forbidden_import_candidates_absent": forbidden_candidate_state,
            **overlay_digests,
        },
    }
    return {
        "schema": "phase6_v3_1_z_package_input_ledger_v1",
        "record_count": len(records),
        "bhpt_file_count": len(file_records),
        "bhpt_directory_count": len(directory_records),
        "threat_record_count": len(threat_records),
        "science_helper_record_count": len(helper_records),
        "project_import_record_count": len(project_import_records),
        "ledger_sha256": sha256_bytes(canonical_object_bytes(ledger_payload)),
        "payload": ledger_payload,
    }


def artifact_hash(
    schema_id: str, revision: int, tagged_payload: Sequence[Sequence[Any]]
) -> str:
    prefix = b"SCHWO-V31Z\0ARTIFACT\0" + schema_id.encode("ascii") + b"\0"
    return sha256_bytes(prefix + enc(schema_id, revision, tagged_payload))


def derived_hash(label: str, tagged_items: Sequence[Sequence[Any]]) -> str:
    if type(label) is not str or not re.fullmatch(r"[A-Za-z0-9_.-]+", label):
        raise AuthorityError("derived-hash label is not a closed ASCII literal")
    prefix = b"SCHWO-V31Z\0DERIVED\0" + label.encode("ascii") + b"\0"
    return sha256_bytes(prefix + tagged_array_bytes(tagged_items))


def strict_load_json(path: Path, *, canonical: bool = True) -> Any:
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=_strict_pairs)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AuthorityError(f"invalid JSON {path}: {exc}") from exc
    if canonical and raw != canonical_object_bytes(value):
        raise AuthorityError(f"noncanonical JSON bytes: {path}")
    return value


def _require_exact_keys(value: Mapping[str, Any], keys: set[str], context: str) -> None:
    actual = set(value)
    if actual != keys:
        raise AuthorityError(
            f"{context} key mismatch: missing={sorted(keys - actual)} "
            f"extra={sorted(actual - keys)}"
        )


def _require_plain_int(value: Any, context: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise AuthorityError(f"{context} must be an integer >= {minimum}")
    return value


def _require_id(value: Any, context: str) -> str:
    if type(value) is not str or not re.fullmatch(r"[A-Za-z0-9_.:-]+", value):
        raise AuthorityError(f"invalid authority identifier for {context}: {value!r}")
    return value


def _index_registry(spec: Mapping[str, Any], name: str) -> dict[str, dict[str, Any]]:
    rows = spec[name]
    if type(rows) is not list:
        raise AuthorityError(f"{name} must be an ordered array")
    fields = REGISTRY_ROW_FIELDS[name]
    id_field = fields[0]
    index: dict[str, dict[str, Any]] = {}
    for ordinal, row in enumerate(rows):
        if type(row) is not list or len(row) != len(fields):
            raise AuthorityError(
                f"{name}[{ordinal}] must be an exact {len(fields)}-field ordered row"
            )
        mapped = dict(zip(fields, row, strict=True))
        row_id = _require_id(mapped[id_field], f"{name}[{ordinal}].{id_field}")
        if row_id in index:
            raise AuthorityError(f"duplicate {name} ID: {row_id}")
        index[row_id] = mapped
    return index


def _topological_digest_nodes(
    nodes: list[dict[str, Any]],
) -> tuple[list[str], list[tuple[str, str]]]:
    index: dict[str, dict[str, Any]] = {}
    edges: list[tuple[str, str]] = []
    for ordinal, node in enumerate(nodes):
        _require_exact_keys(
            node,
            {"digest_node_id", "domain_label", "input_node_ids", "input_type_ids"},
            f"digest_nodes[{ordinal}]",
        )
        node_id = _require_id(node["digest_node_id"], "digest node")
        if node_id in index:
            raise AuthorityError(f"duplicate digest node: {node_id}")
        if (
            type(node["input_node_ids"]) is not list
            or type(node["input_type_ids"]) is not list
        ):
            raise AuthorityError(f"digest node {node_id} inputs must be arrays")
        if len(node["input_node_ids"]) != len(node["input_type_ids"]):
            raise AuthorityError(f"digest node {node_id} input/type arity mismatch")
        index[node_id] = node
    missing_required = set(REQUIRED_DIGEST_NODE_IDS) - set(index)
    if missing_required:
        raise AuthorityError(
            f"missing required digest nodes: {sorted(missing_required)}"
        )
    indegree = {node_id: 0 for node_id in index}
    children = {node_id: [] for node_id in index}
    for node_id, node in index.items():
        for dependency in node["input_node_ids"]:
            if dependency.startswith("INPUT:"):
                continue
            if dependency not in index:
                raise AuthorityError(
                    f"unknown digest dependency {dependency} in {node_id}"
                )
            if dependency == node_id:
                raise AuthorityError(f"self-referential digest node: {node_id}")
            edges.append((dependency, node_id))
            children[dependency].append(node_id)
            indegree[node_id] += 1
    ready = [node_id for node_id in index if indegree[node_id] == 0]
    ordered: list[str] = []
    while ready:
        node_id = ready.pop(0)
        ordered.append(node_id)
        for child in children[node_id]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    if len(ordered) != len(index):
        raise AuthorityError("digest DAG contains a cycle")
    return ordered, edges


def _expected_call_plans() -> list[dict[str, Any]]:
    anchors = EXPECTED_ROUTE_C_ANCHORS
    compatibility_calls = [
        {
            "call_kind": "COMPATIBILITY_118_CASES",
            "call_ordinal": 0,
            "fixture_count": 118,
            "science_calls": 0,
        }
    ]
    first_anchor = anchors[0]
    micro_calls = [
        {
            "anchor_ordinal": first_anchor[0],
            "call_kind": "SOURCE_LOAD_MICRO",
            "call_ordinal": 0,
            "ell": first_anchor[2],
            "kM": first_anchor[1],
            "node": "P1",
            "parity": first_anchor[3],
            "pre_public_api_exit": True,
        }
    ]
    sentinel_calls: list[dict[str, Any]] = []
    for anchor_ordinal, km, ell, parity in anchors:
        sentinel_calls.append(
            {
                "anchor_ordinal": anchor_ordinal,
                "call_kind": "ANCHOR_P1",
                "call_ordinal": len(sentinel_calls),
                "ell": ell,
                "kM": km,
                "node": "P1",
                "parity": parity,
            }
        )
    boundary_nodes = tuple(node for node in EXPECTED_ROUTE_C_NODES if node != "P1")
    for anchor in (anchors[3], anchors[22]):
        anchor_ordinal, km, ell, parity = anchor
        for node in boundary_nodes:
            sentinel_calls.append(
                {
                    "anchor_ordinal": anchor_ordinal,
                    "call_kind": "BOUNDARY_LIFECYCLE",
                    "call_ordinal": len(sentinel_calls),
                    "ell": ell,
                    "kM": km,
                    "node": node,
                    "parity": parity,
                }
            )
    official_calls: list[dict[str, Any]] = []
    for anchor_ordinal, km, ell, parity in anchors:
        for node_ordinal, node in enumerate(EXPECTED_ROUTE_C_NODES):
            call_ordinal = 7 * anchor_ordinal + node_ordinal
            if call_ordinal != len(official_calls):
                raise AuthorityError("internal official call-plan ordinal drift")
            official_calls.append(
                {
                    "anchor_ordinal": anchor_ordinal,
                    "call_kind": "OFFICIAL_ANCHOR_NODE",
                    "call_ordinal": call_ordinal,
                    "ell": ell,
                    "kM": km,
                    "node": node,
                    "parity": parity,
                }
            )
    return [
        {"calls": compatibility_calls, "operation": "compatibility"},
        {"calls": micro_calls, "operation": "source_load_micro"},
        {"calls": sentinel_calls, "operation": "full_sentinel"},
        {"calls": official_calls, "operation": "official"},
    ]


def _resource_projection(spec: Mapping[str, Any]) -> dict[str, Any]:
    limits = spec["resource_limits"]
    maximum_by_schema = dict(RESOURCE_ARTIFACT_MAX_ENCODED_BYTES)
    rows: list[dict[str, Any]] = []
    expected_projection_by_operation = dict(EXPECTED_PROJECTED_ROOT_BYTES)
    for operation in spec["operations"]:
        operation_id = operation["operation"]
        calls = operation["expected_calls"]
        predicates = operation["expected_predicates"]
        frames = operation["expected_child_frames"]
        output_counts = [
            ["parent_event", predicates],
            ["prefix_checkpoint", predicates],
            ["final_stage_checkpoint", 18 * calls],
            ["stage_open_authority", 17 * calls],
            ["stage0_seed", calls],
            ["child_exit_authority", calls],
            ["lifecycle_receipt", calls],
            ["p17_closure", calls],
            ["terminal_manifest", calls],
            ["operation_terminal_manifest", 1],
            ["root_terminal_checkpoint", 1],
        ]
        output_schema_bytes = sum(
            maximum_by_schema[schema_id] * count for schema_id, count in output_counts
        )
        terms = {
            "ack_bytes": limits["ack_max_bytes"] * frames,
            "fixed_authority_bytes": limits["fixed_authority_bytes_per_call"] * calls
            + limits["fixed_authority_bytes_per_operation"],
            "frame_bytes": limits["frame_max_bytes"] * frames,
            "output_schema_bytes": output_schema_bytes,
            "raw_stderr_bytes": limits["raw_stderr_limit_bytes_per_call"] * calls,
            "raw_stdout_bytes": limits["raw_stdout_limit_bytes_per_call"] * calls,
        }
        projected = sum(terms.values())
        if projected != expected_projection_by_operation[operation_id]:
            raise AuthorityError(
                f"resource projection arithmetic drift: {operation_id}"
            )
        whole_root_cap = (
            limits["compatibility_whole_root_bytes_max"]
            if operation_id == "compatibility"
            else limits["micro_whole_root_bytes_max"]
            if operation_id == "source_load_micro"
            else None
        )
        if whole_root_cap is not None and projected > whole_root_cap:
            raise AuthorityError(
                f"resource projection exceeds whole-root cap: {operation_id}"
            )
        rows.append(
            {
                "declared_acks": frames,
                "declared_calls": calls,
                "declared_child_frames": frames,
                "declared_output_record_counts": output_counts,
                "operation": operation_id,
                "projected_root_bytes": projected,
                "projection_terms": terms,
                "whole_root_bytes_max_or_null": whole_root_cap,
            }
        )
    if [[row["operation"], row["projected_root_bytes"]] for row in rows] != limits[
        "projected_root_bytes"
    ]:
        raise AuthorityError("resource projection literal table drift")
    return {
        "schema": "phase6_v3_1_z_resource_projection_v1",
        "gate_id": GATE_ID,
        "formula": limits["projection_formula"],
        "frame_max_bytes": limits["frame_max_bytes"],
        "ack_max_bytes": limits["ack_max_bytes"],
        "raw_stdout_limit_bytes_per_call": limits["raw_stdout_limit_bytes_per_call"],
        "raw_stderr_limit_bytes_per_call": limits["raw_stderr_limit_bytes_per_call"],
        "artifact_max_encoded_record_bytes": limits[
            "artifact_max_encoded_record_bytes"
        ],
        "fixed_authority_bytes_per_call": limits["fixed_authority_bytes_per_call"],
        "fixed_authority_bytes_per_operation": limits[
            "fixed_authority_bytes_per_operation"
        ],
        "operations": rows,
        "free_space_rule": limits["free_space_rule"],
    }


def _validate_execution_contract(spec: Mapping[str, Any]) -> None:
    expected_stages = [
        {
            "actor_profiles": {
                "compatibility": compatibility,
                "production": production,
            },
            "stage_id": stage_id,
            "stage_ordinal": ordinal,
        }
        for ordinal, (stage_id, compatibility, production) in enumerate(
            EXPECTED_STAGE_ROWS
        )
    ]
    if spec["stages"] != expected_stages:
        raise AuthorityError("stage ID/actor-profile contract drift")

    expected_operations = [
        {
            "expected_calls": calls,
            "expected_child_frames": frames,
            "expected_predicates": predicates,
            "expected_stage_predicate_counts": list(stage_counts),
            "operation": operation,
            "operation_code": code,
            "profile_kind": profile,
            "science_capable": science_capable,
        }
        for (
            operation,
            code,
            profile,
            science_capable,
            calls,
            predicates,
            frames,
            stage_counts,
        ) in EXPECTED_OPERATION_ROWS
    ]
    if spec["operations"] != expected_operations:
        raise AuthorityError("operation profile/count contract drift")
    expected_call_plans = _expected_call_plans()
    if spec["call_plans"] != expected_call_plans:
        raise AuthorityError("call-plan content/order/type contract drift")
    if spec["state_machine"] != [list(row) for row in EXPECTED_STATE_MACHINE]:
        raise AuthorityError("finite-state-machine edge contract drift")
    if spec["resource_limits"] != EXPECTED_RESOURCE_LIMITS:
        raise AuthorityError("resource-limit literal contract drift")
    _resource_projection(spec)

    total_calls = 0
    total_predicates = 0
    total_frames = 0
    total_finals = 0
    total_opens = 0
    for operation in expected_operations:
        profile = (
            "compatibility"
            if operation["operation"] == "compatibility"
            else "production"
        )
        per_call_frames = 0
        for stage, predicate_count in zip(
            expected_stages,
            operation["expected_stage_predicate_counts"],
            strict=True,
        ):
            actor = stage["actor_profiles"][profile]
            if actor == "CHILD_PREDICATES":
                per_call_frames += predicate_count
            elif actor in {
                "CHILD_CONTROL_BARRIER_THEN_PARENT_FIXTURES",
                "LOGICAL_PREDICATE_BARRIER_THEN_PARENT_OBSERVATIONS",
            }:
                per_call_frames += 1
            elif actor not in {"PARENT_ONLY_PRELAUNCH", "PARENT_ONLY_POSTREAP"}:
                raise AuthorityError(f"unknown stage actor profile: {actor}")
        calls = operation["expected_calls"]
        independently_derived_predicates = calls * sum(
            operation["expected_stage_predicate_counts"]
        )
        independently_derived_frames = calls * per_call_frames
        if independently_derived_predicates != operation["expected_predicates"]:
            raise AuthorityError(
                f"independent predicate-count mismatch: {operation['operation']}"
            )
        if independently_derived_frames != operation["expected_child_frames"]:
            raise AuthorityError(
                f"independent child-frame mismatch: {operation['operation']}"
            )
        total_calls += calls
        total_predicates += independently_derived_predicates
        total_frames += independently_derived_frames
        total_finals += 18 * calls
        total_opens += 17 * calls
    if (total_calls, total_predicates, total_frames, total_finals, total_opens) != (
        198,
        80_724,
        51_893,
        3_564,
        3_366,
    ):
        raise AuthorityError("global operation/frame cardinality drift")

    science_graph = spec["immutable_inputs"]["science_graph"]
    _require_exact_keys(
        science_graph,
        {
            "certificate_ids",
            "ell_max_by_frequency",
            "exact_frequencies",
            "exact_modes",
            "exact_pairs",
            "gamma_routes",
            "route_a",
            "route_a_records",
            "route_b",
            "route_b_modes",
            "route_b_records",
            "route_c",
            "route_u_selector",
            "sentinel",
            "thresholds",
        },
        "science graph",
    )
    route_a = science_graph["route_a"]
    _require_exact_keys(
        route_a,
        {
            "applicability",
            "axes",
            "baseline",
            "baseline_memberships",
            "candidate_nodes_per_mode_before_deduplication",
            "deduplicated_baseline_repetitions",
            "ladder_records_per_mode",
            "ladder_records_total",
            "mode_count",
            "ordered_mode_inventory_sha256",
            "protected_public_calls_total",
            "required_radius",
            "solver_call",
            "terminal_mode_records",
            "transport",
        },
        "Route-A contract",
    )
    if (
        route_a["applicability"] != "ALL_496_ORDERED_MODES"
        or route_a["candidate_nodes_per_mode_before_deduplication"] != 22
        or route_a["deduplicated_baseline_repetitions"] != 2
        or route_a["ladder_records_per_mode"] != 20
        or route_a["mode_count"] != 496
        or route_a["ladder_records_total"] != 496 * 20
        or route_a["protected_public_calls_total"] != 9_920
        or route_a["terminal_mode_records"] != 496
        or route_a["ordered_mode_inventory_sha256"]
        != "e4d09740c032c3c48ae43be56c1dd11512527b6266f5974f444302bb4afc45d8"
        or route_a["baseline"] != ["1e-10", 1, 160, "1e-10", "1e-12"]
        or route_a["baseline_memberships"] != ["outer_jost", "rin", "tolerance"]
        or route_a["solver_call"] != "solve_scaled_tortoise_radial_at_radius"
        or route_a["transport"]
        != {
            "auxiliary_exponent_domain": [0, 1, 2],
            "auxiliary_rule": ("min n: k*(2^n*r_match)>=4*sqrt(ell*(ell+1))"),
            "integrator": "DOP853",
            "maximum_rstar_segment": "4",
            "pseudoinverse_or_fallback": False,
            "two_by_two_exact_solve": True,
        }
    ):
        raise AuthorityError("Route-A method/ladder/dedupe contract drift")
    axes = route_a["axes"]
    if (
        axes["rin"]["epsilons"] != ["1e-8", "1e-10", "1e-12"]
        or axes["outer_jost"]["outer_multipliers"] != [1, 2, 4, 8]
        or axes["outer_jost"]["jost_orders"] != [80, 120, 160, 200]
        or axes["tolerance"]["pairs"]
        != [
            ["1e-9", "1e-11"],
            ["1e-10", "1e-12"],
            ["3e-11", "3e-13"],
        ]
    ):
        raise AuthorityError("Route-A axis contract drift")
    route_b = science_graph["route_b"]
    _require_exact_keys(
        route_b,
        {
            "arbitrary_exponent_decimal",
            "evanescent_selector",
            "independent_odd_even",
            "key_count",
            "low_selector",
            "node_records_total",
            "ordered_key_inventory_sha256",
            "precision_dps",
            "precision_records",
            "protected_route_a_import_or_call",
            "records_per_nonturning_key",
            "records_per_turning_key",
            "selector_strata_counts",
            "selector_union_deduplicated",
            "turning_extra_nodes",
            "turning_extra_records",
            "turning_selector",
        },
        "Route-B contract",
    )
    if (
        route_b["selector_strata_counts"]
        != [["LOW", 40], ["TURNING", 38], ["EVANESCENT", 24]]
        or route_b["key_count"] != 40 + 38 + 24
        or route_b["precision_dps"] != [80, 120, 180]
        or route_b["precision_records"] != 102 * 3
        or route_b["turning_extra_records"] != 38 * 4
        or route_b["node_records_total"] != 306 + 152
        or route_b["records_per_nonturning_key"] != 3
        or route_b["records_per_turning_key"] != 7
        or route_b["ordered_key_inventory_sha256"]
        != "25c4b2831924bd550a44e59df35b1d2b2687b66e0e1e2b96fb3ef88086667bf3"
        or route_b["protected_route_a_import_or_call"] is not False
        or route_b["arbitrary_exponent_decimal"] is not True
        or route_b["independent_odd_even"] is not True
    ):
        raise AuthorityError("Route-B selector/precision/record contract drift")
    if (
        science_graph["exact_modes"],
        science_graph["exact_pairs"],
        science_graph["route_a_records"],
        science_graph["route_b_modes"],
        science_graph["route_b_records"],
    ) != (496, 248, 9_920, 102, 458):
        raise AuthorityError("science graph global cardinality drift")
    route_c = science_graph["route_c"]
    _require_exact_keys(
        route_c,
        {
            "anchor_count",
            "anchors",
            "api_calls",
            "boundary_calls",
            "frequency_representation",
            "geometry",
            "independent_solutions",
            "method",
            "mst_calls",
            "node_order",
            "node_precision_semantics",
            "overlap_calls",
            "ordered_anchor_inventory_sha256",
            "precision_digits",
            "selected_node",
            "spin",
        },
        "Route-C contract",
    )
    expected_route_c = {
        "anchor_count": 23,
        "anchors": [list(row) for row in EXPECTED_ROUTE_C_ANCHORS],
        "api_calls": 161,
        "boundary_calls": 322,
        "frequency_representation": "EXACT_RATIONAL",
        "geometry": {
            "frequency_fraction_map": [
                ["0.1", 1, 10],
                ["0.5", 1, 2],
                ["1", 1, 1],
                ["2", 2, 1],
                ["4", 4, 1],
            ],
            "node_geometry": [
                [
                    "P0",
                    10,
                    1,
                    "rin10_m1",
                    "a8601cd1b377bf4741035a03bec98590ebffbec0004a63af498a260f1d05c5fc",
                ],
                [
                    "P1",
                    10,
                    1,
                    "rin10_m1",
                    "a8601cd1b377bf4741035a03bec98590ebffbec0004a63af498a260f1d05c5fc",
                ],
                [
                    "I0",
                    8,
                    1,
                    "rin8_m1",
                    "ec110e7612a14fce135be77a649324a98498da04b18785502e969ec437622380",
                ],
                [
                    "I2",
                    12,
                    1,
                    "rin12_m1",
                    "574f64024363e59b2fea678f33ed3b373e73374b33efb318fe781aa5b6607958",
                ],
                [
                    "O2",
                    10,
                    2,
                    "rin10_m2",
                    "42369d4584fc079224d5ae9bd6e7565aafeb0a52d0d2a0f06c1666d54dbee008",
                ],
                [
                    "O4",
                    10,
                    4,
                    "rin10_m4",
                    "b5c7b2e496daac3f7d1edf48843b41e7633800329d528065c0f87a94db641bbf",
                ],
                [
                    "O8",
                    10,
                    8,
                    "rin10_m8",
                    "8bdf36d3bba5dc2ffa6e4949dffcd15d42a90acba9c0f9cf431fa8c30e71ffd5",
                ],
            ],
            "outer_radius_formula": ("outer_multiplier*max(300,8*sqrt(ell*(ell+1))/k)"),
            "overlap_multipliers": ["0.80", "0.88", "0.96"],
        },
        "independent_solutions": ["In", "Up"],
        "method": "BHPT ReggeWheeler NumericalIntegration independent In/Up",
        "mst_calls": 0,
        "node_order": list(EXPECTED_ROUTE_C_NODES),
        "node_precision_semantics": [
            list(row) for row in EXPECTED_ROUTE_C_NODE_PRECISION
        ],
        "overlap_calls": 483,
        "ordered_anchor_inventory_sha256": (
            "5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76"
        ),
        "precision_digits": [90, 120],
        "selected_node": "P1",
        "spin": 2,
    }
    if route_c != expected_route_c:
        raise AuthorityError("Route-C method/node/precision contract drift")
    if science_graph["sentinel"] != {
        "boundary_calls": 70,
        "calls": 35,
        "overlap_calls": 105,
    }:
        raise AuthorityError("sentinel Route-C call cardinality drift")
    expected_route_u = {
        "applicability": {
            "direct_gamma_equal_1e-8": "NON_U",
            "direct_gamma_ge_1e-8": "FLOAT64_ABSOLUTE_GAMMA_ROUTE_MAX_2E-8",
            "direct_gamma_gt_0_lt_1e-8": "ROUTE_U_LOG_COMPARISON_MAX_2E-4",
        },
        "forbidden_selector_operands": [
            "Gamma_S",
            "S",
            "mismatch",
            "predecessor_route_map",
            "regime_label",
            "Route_B_record",
            "Route_C_record",
            "threshold_result",
        ],
        "fixed_318_or_954_forbidden": True,
        "gamma_s_formula": "-expm1(2*0.5*log(Re(S)^2+Im(S)^2))",
        "ladder_records_expression": "N_U",
        "ordered_mode_inventory_sha256": (
            "e4d09740c032c3c48ae43be56c1dd11512527b6266f5974f444302bb4afc45d8"
        ),
        "parent_owned_admission": {
            "adjacent_log_gamma_absolute_max": "2e-5",
            "adjacent_s_symmetric_relative_max": "5e-8",
            "decision_owner": "PARENT_AUTHORITY",
            "forbidden_helper_decision_function": "validate_oracle_ladder",
        },
        "precision_records_expression": "3*N_U",
        "precision_schedule": {
            "guard_digits_minimum": 30,
            "node_formula": ["p0", "p0+40", "p0+100"],
            "p0_formula": "20*ceil(max(80,30-exponent10)/20)",
        },
        "predicate": "direct log_Gamma_flux < log(1e-8)",
        "runtime_N_U_range": [0, 496],
        "selector_entries": 496,
        "selector_id": "Z.SELECTOR.ROUTE_U_FRESH_DIRECT_LOG_GAMMA",
    }
    if science_graph["route_u_selector"] != expected_route_u:
        raise AuthorityError("Route-U selector/precision/admission contract drift")


def _expected_authority_progression() -> dict[str, Any]:
    review_rows = [
        (
            "package_review",
            "docs/handoffs/archive/T7_2026-08-14_v3_1_z_generated_machine_authority_package_review.md",
            "ADVANCE",
            "NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-Z GENERATED MACHINE-AUTHORITY PACKAGE READY FOR T6",
        ),
        (
            "implementation_review",
            "docs/handoffs/archive/T7_2026-08-14_v3_1_z_generated_machine_authority_implementation_review.md",
            "ADVANCE",
            "NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-Z IMPLEMENTATION READY FOR COMPATIBILITY DISPATCH",
        ),
        (
            "wolfram_compatibility_review",
            "docs/handoffs/archive/T7_2026-08-14_v3_1_z_wolfram_compatibility_review.md",
            "ADVANCE",
            "NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-Z WOLFRAM COMPATIBILITY PASSED",
        ),
        (
            "source_load_micro_review",
            "docs/handoffs/archive/T7_2026-08-14_v3_1_z_source_load_micro_review.md",
            "ADVANCE",
            "NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-Z SOURCE-LOAD MICRO PASSED",
        ),
        (
            "full_sentinel_review",
            "docs/handoffs/archive/T7_2026-08-14_v3_1_z_full_sentinel_review.md",
            "ADVANCE",
            "NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-Z FULL SENTINEL PASSED",
        ),
        (
            "scientific_review",
            "docs/handoffs/archive/T7_2026-08-14_v3_1_z_scientific_review.md",
            None,
            None,
            None,
        ),
    ]
    dispatch_rows = [
        (
            "implementation",
            "docs/handoffs/archive/T0_2026-08-14_v3_1_z_implementation_dispatch_attempt_0001.json",
            "package_review",
            "T6_IMPLEMENTATION",
            None,
        ),
        (
            "wolfram_compatibility",
            "docs/handoffs/archive/T0_2026-08-14_v3_1_z_wolfram_compatibility_dispatch_attempt_0001.json",
            "implementation_review",
            "WOLFRAM_COMPATIBILITY",
            "wolfram_compatibility",
        ),
        (
            "source_load_micro",
            "docs/handoffs/archive/T0_2026-08-14_v3_1_z_source_load_micro_dispatch_attempt_0001.json",
            "wolfram_compatibility_review",
            "SOURCE_LOAD_MICRO",
            "source_load_micro",
        ),
        (
            "full_sentinel",
            "docs/handoffs/archive/T0_2026-08-14_v3_1_z_full_sentinel_dispatch_attempt_0001.json",
            "source_load_micro_review",
            "FULL_SENTINEL",
            "full_sentinel",
        ),
        (
            "official",
            "docs/handoffs/archive/T0_2026-08-14_v3_1_z_official_dispatch_attempt_0001.json",
            "full_sentinel_review",
            "OFFICIAL",
            "official",
        ),
    ]
    prompt_rows = [
        (
            "T6_IMPLEMENTATION",
            "docs/prompts/phase6_t6_v3_1_z_generated_machine_authority_implementation.md",
            "T6_ZERO_SCIENCE_IMPLEMENTER",
        ),
        (
            "T7_PACKAGE_REVIEW",
            "docs/prompts/phase6_t7_v3_1_z_generated_machine_authority_package_review.md",
            "T7_SOURCE_DISTINCT_PACKAGE_REVIEWER",
        ),
        (
            "T7_IMPLEMENTATION_REVIEW",
            "docs/prompts/phase6_t7_v3_1_z_generated_machine_authority_implementation_review.md",
            "T7_IMPLEMENTATION_REVIEWER",
        ),
        (
            "T7_WOLFRAM_COMPATIBILITY_REVIEW",
            "docs/prompts/phase6_t7_v3_1_z_wolfram_compatibility_review.md",
            "T7_COMPATIBILITY_REVIEWER",
        ),
        (
            "T7_SOURCE_LOAD_MICRO_REVIEW",
            "docs/prompts/phase6_t7_v3_1_z_source_load_micro_review.md",
            "T7_MICRO_REVIEWER",
        ),
        (
            "T7_FULL_SENTINEL_REVIEW",
            "docs/prompts/phase6_t7_v3_1_z_full_sentinel_review.md",
            "T7_SENTINEL_REVIEWER",
        ),
        (
            "T7_SCIENCE_REVIEW",
            "docs/prompts/phase6_t7_v3_1_z_science_review.md",
            "T7_SCIENCE_REVIEWER",
        ),
    ]
    namespace_rows = [
        (
            "wolfram_compatibility",
            "compatibility",
            r"^v3_1_z_wolfram_compatibility_v1_[0-9]{8}T[0-9]{6}Z_py314$",
        ),
        (
            "source_load_micro",
            "source_load_micro",
            r"^v3_1_z_source_load_micro_v1_[0-9]{8}T[0-9]{6}Z_py314$",
        ),
        (
            "full_sentinel",
            "full_sentinel",
            r"^v3_1_z_full_sentinel_v1_[0-9]{8}T[0-9]{6}Z_py314$",
        ),
        (
            "official",
            "official",
            r"^v3_1_z_official_v1_[0-9]{8}T[0-9]{6}Z_py314$",
        ),
    ]
    return {
        "bounded_repair_cycles": 0,
        "dispatches": [
            {
                "consumer": consumer,
                "one_use": True,
                "path": path,
                "prior_review_role": prior_review,
                "role": role,
                "root_namespace_or_null": root_namespace,
                "sha256_source": "RUNTIME_REHASH_AFTER_O_EXCL_PUBLICATION",
            }
            for role, path, prior_review, consumer, root_namespace in dispatch_rows
        ],
        "future_paths_must_be_absent": True,
        "future_prompts": [
            {"path": path, "prompt_id": prompt_id, "role": role}
            for prompt_id, path, role in prompt_rows
        ],
        "graph_edges": [
            ["PACKAGE_CANDIDATE", "PACKAGE_REVIEW", "NO_DISPATCH"],
            ["PACKAGE_REVIEW", "IMPLEMENTATION", "IMPLEMENTATION_DISPATCH"],
            ["IMPLEMENTATION", "IMPLEMENTATION_REVIEW", "NO_DISPATCH"],
            [
                "IMPLEMENTATION_REVIEW",
                "WOLFRAM_COMPATIBILITY",
                "WOLFRAM_COMPATIBILITY_DISPATCH",
            ],
            [
                "WOLFRAM_COMPATIBILITY",
                "WOLFRAM_COMPATIBILITY_REVIEW",
                "NO_DISPATCH",
            ],
            [
                "WOLFRAM_COMPATIBILITY_REVIEW",
                "SOURCE_LOAD_MICRO",
                "SOURCE_LOAD_MICRO_DISPATCH",
            ],
            ["SOURCE_LOAD_MICRO", "SOURCE_LOAD_MICRO_REVIEW", "NO_DISPATCH"],
            [
                "SOURCE_LOAD_MICRO_REVIEW",
                "FULL_SENTINEL",
                "FULL_SENTINEL_DISPATCH",
            ],
            ["FULL_SENTINEL", "FULL_SENTINEL_REVIEW", "NO_DISPATCH"],
            [
                "FULL_SENTINEL_REVIEW",
                "OFFICIAL",
                "OFFICIAL_DISPATCH",
            ],
            ["OFFICIAL", "SCIENTIFIC_REVIEW", "NO_DISPATCH"],
        ],
        "noncircular_binding": {
            "future_review_sha256_source": (
                "ONE_USE_DOWNSTREAM_DISPATCH_RUNTIME_REHASH"
            ),
            "package_excludes_prompt_sha256": True,
            "prompt_binding_direction": "PROMPT_TO_FINALIZED_PACKAGE",
            "prompt_self_sha256_embedded": False,
        },
        "review_archives": [
            {
                "advance_decision": advance,
                "claim_status": claim,
                "gate_label": label,
                "path": path,
                "role": role,
                "sha256_source": "RUNTIME_REHASH_AFTER_O_EXCL_PUBLICATION",
            }
            for role, path, advance, claim, label in review_rows
        ],
        "root_namespaces": [
            {
                "basename_regex": regex,
                "direct_child": True,
                "no_alias": True,
                "operation": operation,
                "predicate_operation": predicate_operation,
                "utc_parse_roundtrip": True,
            }
            for operation, predicate_operation, regex in namespace_rows
        ],
        "root_parent": EXPECTED_ROOT_PARENT,
        "system_interruption_policy": "ESCALATE_NO_RESUME",
    }


def _validate_authority_progression(spec: Mapping[str, Any]) -> None:
    progression = spec["authority_progression"]
    if progression != _expected_authority_progression():
        raise AuthorityError("future authority progression literal contract drift")
    _require_exact_keys(
        progression,
        {
            "review_archives",
            "dispatches",
            "root_parent",
            "root_namespaces",
            "future_prompts",
            "graph_edges",
            "noncircular_binding",
            "bounded_repair_cycles",
            "system_interruption_policy",
            "future_paths_must_be_absent",
        },
        "authority_progression",
    )
    if progression["bounded_repair_cycles"] != 0:
        raise AuthorityError("V3.1-Z v1 permits zero bounded repairs")
    if progression["system_interruption_policy"] != "ESCALATE_NO_RESUME":
        raise AuthorityError("V3.1-Z v1 must fail closed on interruption")
    if progression["future_paths_must_be_absent"] is not True:
        raise AuthorityError("future authority paths must be absent at package freeze")
    if progression["root_parent"] != EXPECTED_ROOT_PARENT:
        raise AuthorityError("future executable-root parent drift")

    expected_review_roles = [
        "package_review",
        "implementation_review",
        "wolfram_compatibility_review",
        "source_load_micro_review",
        "full_sentinel_review",
        "scientific_review",
    ]
    expected_dispatch_roles = [
        "implementation",
        "wolfram_compatibility",
        "source_load_micro",
        "full_sentinel",
        "official",
    ]
    expected_prompt_ids = [
        "T6_IMPLEMENTATION",
        "T7_PACKAGE_REVIEW",
        "T7_IMPLEMENTATION_REVIEW",
        "T7_WOLFRAM_COMPATIBILITY_REVIEW",
        "T7_SOURCE_LOAD_MICRO_REVIEW",
        "T7_FULL_SENTINEL_REVIEW",
        "T7_SCIENCE_REVIEW",
    ]
    if [
        row.get("role") for row in progression["review_archives"]
    ] != expected_review_roles:
        raise AuthorityError("future review role/order drift")
    if [
        row.get("role") for row in progression["dispatches"]
    ] != expected_dispatch_roles:
        raise AuthorityError("future dispatch role/order drift")
    if [
        row.get("prompt_id") for row in progression["future_prompts"]
    ] != expected_prompt_ids:
        raise AuthorityError("future prompt ID/order drift")

    all_paths: list[str] = []
    for key in ("review_archives", "dispatches", "future_prompts"):
        rows = progression[key]
        if type(rows) is not list:
            raise AuthorityError(f"authority_progression.{key} must be an array")
        for row in rows:
            if type(row) is not dict or type(row.get("path")) is not str:
                raise AuthorityError(f"invalid {key} row")
            expected_keys = (
                {
                    "role",
                    "path",
                    "sha256_source",
                    "advance_decision",
                    "claim_status",
                    "gate_label",
                }
                if key == "review_archives"
                else {
                    "role",
                    "path",
                    "sha256_source",
                    "prior_review_role",
                    "consumer",
                    "root_namespace_or_null",
                    "one_use",
                }
                if key == "dispatches"
                else {"prompt_id", "path", "role"}
            )
            _require_exact_keys(row, expected_keys, f"authority_progression.{key}")
            pure = PurePosixPath(row["path"])
            if pure.is_absolute() or ".." in pure.parts or str(pure) != row["path"]:
                raise AuthorityError(
                    f"noncanonical future authority path: {row['path']}"
                )
            all_paths.append(row["path"])
            if "sha256" in row:
                raise AuthorityError(
                    f"future authority digest prefilled in {row['path']}"
                )
            if key in {"review_archives", "dispatches"} and row["sha256_source"] != (
                "RUNTIME_REHASH_AFTER_O_EXCL_PUBLICATION"
            ):
                raise AuthorityError(f"future digest policy drift: {row['path']}")
            if key == "dispatches" and row["one_use"] is not True:
                raise AuthorityError(f"future dispatch is not one-use: {row['path']}")
    if len(all_paths) != len(set(all_paths)):
        raise AuthorityError("future authority paths collide")

    namespaces = progression["root_namespaces"]
    if [row.get("operation") for row in namespaces] != [
        "wolfram_compatibility",
        "source_load_micro",
        "full_sentinel",
        "official",
    ]:
        raise AuthorityError("root namespace operation/order drift")
    predicate_operations = {row["operation"] for row in spec["operations"]}
    for row in namespaces:
        _require_exact_keys(
            row,
            {
                "operation",
                "predicate_operation",
                "basename_regex",
                "utc_parse_roundtrip",
                "direct_child",
                "no_alias",
            },
            "root namespace",
        )
        if row["predicate_operation"] not in predicate_operations:
            raise AuthorityError("root namespace has unknown predicate operation")
        if not all(
            row[key] is True
            for key in ("utc_parse_roundtrip", "direct_child", "no_alias")
        ):
            raise AuthorityError("root namespace safety flag drift")
        re.compile(row["basename_regex"])
        if not row["basename_regex"].startswith("^v3_1_z_") or not row[
            "basename_regex"
        ].endswith("$"):
            raise AuthorityError("root namespace regex is not an exact V3.1-Z basename")
        canonical_sample = re.sub(
            r"\[0-9\]\{8\}T\[0-9\]\{6\}Z",
            "20260814T000000Z",
            row["basename_regex"][1:-1],
        )
        if re.fullmatch(row["basename_regex"], canonical_sample) is None:
            raise AuthorityError("root namespace rejects its canonical sample")
        timestamp = re.search(r"([0-9]{8}T[0-9]{6}Z)", canonical_sample)
        if timestamp is None:
            raise AuthorityError("root namespace sample lacks a UTC timestamp")
        parsed = time.strptime(timestamp.group(1), "%Y%m%dT%H%M%SZ")
        if time.strftime("%Y%m%dT%H%M%SZ", parsed) != timestamp.group(1):
            raise AuthorityError("root namespace UTC timestamp does not round-trip")

    expected_binding = {
        "future_review_sha256_source": "ONE_USE_DOWNSTREAM_DISPATCH_RUNTIME_REHASH",
        "package_excludes_prompt_sha256": True,
        "prompt_binding_direction": "PROMPT_TO_FINALIZED_PACKAGE",
        "prompt_self_sha256_embedded": False,
    }
    if progression["noncircular_binding"] != expected_binding:
        raise AuthorityError("package/prompt noncircular binding drift")
    edges = progression["graph_edges"]
    if (
        type(edges) is not list
        or len(edges) != 11
        or any(type(edge) is not list or len(edge) != 3 for edge in edges)
    ):
        raise AuthorityError("future authority graph edge inventory mismatch")


def _validate_future_absence(spec: Mapping[str, Any], repo_root: Path) -> None:
    progression = spec["authority_progression"]
    repo_root = repo_root.resolve(strict=True)
    for key in ("review_archives", "dispatches"):
        for row in progression[key]:
            path = repo_root / row["path"]
            resolved_parent = path.parent.resolve(strict=True)
            if repo_root not in (resolved_parent, *resolved_parent.parents):
                raise AuthorityError(f"future authority escapes repository: {path}")
            if path.exists() or path.is_symlink():
                raise AuthorityError(f"future authority path is not absent: {path}")
    for relative in spec["generated_output_plan"]["future_t6_implementation_paths"]:
        path = repo_root / relative
        resolved_parent = path.parent.resolve(strict=True)
        if repo_root not in (resolved_parent, *resolved_parent.parents):
            raise AuthorityError(
                f"future implementation path escapes repository: {path}"
            )
        if path.exists() or path.is_symlink():
            raise AuthorityError(f"future T6 implementation path is not absent: {path}")
    root_parent = Path(progression["root_parent"])
    if (
        not root_parent.is_dir()
        or root_parent.is_symlink()
        or root_parent.resolve(strict=True) != root_parent.absolute()
    ):
        raise AuthorityError("future root parent missing or aliased")
    for entry in root_parent.iterdir():
        for namespace in progression["root_namespaces"]:
            if re.fullmatch(namespace["basename_regex"], entry.name):
                raise AuthorityError(
                    f"future V3.1-Z executable root already exists: {entry}"
                )


def _validate_tagged_literal(value: Any, context: str) -> None:
    if type(value) is not list or not value or type(value[0]) is not str:
        raise AuthorityError(f"{context} must be an explicitly tagged value")
    tag = value[0]
    if tag == "n":
        if value != ["n"]:
            raise AuthorityError(f"invalid null tag in {context}")
        return
    if tag == "b":
        if len(value) != 2 or type(value[1]) is not bool:
            raise AuthorityError(f"invalid boolean tag in {context}")
        return
    if tag == "i":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or not re.fullmatch(r"0|-?[1-9][0-9]*", value[1])
        ):
            raise AuthorityError(f"invalid integer tag in {context}")
        return
    if tag == "h":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", value[1])
        ):
            raise AuthorityError(f"invalid hash tag in {context}")
        return
    if tag == "d":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or not re.fullmatch(
                r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?e[+-][0-9]+", value[1]
            )
            or value[1].startswith("-0")
        ):
            raise AuthorityError(f"invalid canonical decimal tag in {context}")
        return
    if tag == "s":
        if len(value) != 2 or type(value[1]) is not str:
            raise AuthorityError(f"invalid string tag in {context}")
        return
    if tag == "a":
        if len(value) < 2 or type(value[1]) is not str:
            raise AuthorityError(f"invalid compound tag in {context}")
        for ordinal, item in enumerate(value[2:]):
            _validate_tagged_literal(item, f"{context}[{ordinal}]")
        return
    raise AuthorityError(f"unknown authority tag {tag!r} in {context}")


def _validate_ast(
    node: Any,
    context: str,
    *,
    selector: bool = False,
    allow_literal_table: bool = False,
) -> None:
    if type(node) is not list or not node or type(node[0]) is not str:
        raise AuthorityError(f"{context} must be a closed AST/list table")
    opcode = node[0]
    allowed = SELECTOR_CONSTRUCTORS if selector else AST_CONSTRUCTORS
    if opcode not in allowed:
        if allow_literal_table and opcode in {
            "TYPE_DECISION",
            "TAG_ENCODER",
            "DOMAIN_DECISION",
            "UTF8_NO_BOM",
            "SHA256",
            "LSTAT",
            "OPEN_RDONLY_NOFOLLOW",
            "DECLARATION_ORDER",
            "UNIQUE_DEVICE_INODE",
            "ONE_COMPACT_ARRAY_PER_LF",
            "POPEN_ONCE",
            "ARBITRARY_PRECISION_STRING_ONLY",
            "PROJECT_DECLARED_FIELD",
            "PROJECT_DECLARED_RAW_CHILD_FIELD",
            "OPERATOR",
            "SCIENCE_OPERATOR",
            "LITERAL_TRANSFORM",
            "COMPATIBILITY_OPERATION_TABLE",
        }:
            return
        raise AuthorityError(f"unknown AST/table opcode {opcode!r} in {context}")
    if opcode == "CONST":
        if len(node) != 2:
            raise AuthorityError(f"CONST arity mismatch in {context}")
        _validate_tagged_literal(node[1], f"{context}.CONST")
        return
    fixed_arity = {
        "AUTHORITY_REF": 1,
        "FIELD": 1 if selector else 2,
        "AXIS": 1,
        "INDEX": 2,
        "LENGTH": 1,
        "HASH": 1,
        "NOT": 1,
        "ABS": 1,
        "SQUARE": 1,
        "SQRT": 1,
        "LN": 1,
        "WRAP_TO_PI": 1,
        "EQ": 2,
        "LT": 2,
        "LE": 2,
        "SUBTRACT": 2,
        "DIVIDE": 2,
        "CATALOG": 1,
        "RANGE": 2,
        "ORDERED_PROJECT": 2,
    }
    if opcode in fixed_arity and len(node) != fixed_arity[opcode] + 1:
        raise AuthorityError(f"{opcode} arity mismatch in {context}")
    if (
        opcode in {"AND", "OR", "CONCAT", "ADD", "MULTIPLY", "MAX", "MIN"}
        and len(node) < 3
    ):
        raise AuthorityError(f"{opcode} requires at least two operands in {context}")
    for ordinal, child in enumerate(node[1:]):
        if type(child) is list:
            _validate_ast(child, f"{context}.{opcode}[{ordinal}]", selector=selector)
        elif type(child) not in {str, int}:
            raise AuthorityError(
                f"invalid AST operand in {context}.{opcode}[{ordinal}]"
            )


def _runtime_authority_input_index(
    spec: Mapping[str, Any],
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> dict[str, tuple[str, str, tuple[str, ...]]]:
    rows = spec["immutable_inputs"].get("runtime_authority_input_catalog")
    if type(rows) is not list:
        raise AuthorityError("runtime authority input catalog must be an ordered array")
    result: dict[str, tuple[str, str, tuple[str, ...]]] = {}
    evidence_ids = set(registries["evidence_input_registry"])
    value_schema_ids = set(registries["value_schema_registry"])
    allowed_sources = {
        "SOURCE_BOUND_EXPECTED",
        "P00_AUTHORITY",
        "DERIVED_EXPRESSION",
        "PARENT_OBSERVATION",
        "CHILD_OBSERVATION",
        "NESTED_AUTHORITY",
    }
    for ordinal, row in enumerate(rows):
        if type(row) is not list or len(row) not in {4, 9}:
            raise AuthorityError(
                f"runtime authority input row {ordinal} has invalid arity"
            )
        input_id, value_schema_id, source_kind, evidence_plan_ids = row[:4]
        input_id = _require_id(input_id, f"runtime authority input {ordinal}")
        is_artifact_source = input_id.startswith(ARTIFACT_SOURCE_AUTHORITY_PREFIX)
        if len(row) != (9 if is_artifact_source else 4):
            raise AuthorityError(
                f"runtime authority input metadata arity drift: {input_id}"
            )
        if input_id in result:
            raise AuthorityError(f"duplicate runtime authority input: {input_id}")
        if value_schema_id not in value_schema_ids:
            raise AuthorityError(f"unknown runtime input value schema: {input_id}")
        if source_kind not in allowed_sources:
            raise AuthorityError(f"unknown runtime input source kind: {input_id}")
        if type(evidence_plan_ids) is not list or any(
            evidence_id not in evidence_ids for evidence_id in evidence_plan_ids
        ):
            raise AuthorityError(f"unresolved runtime input evidence: {input_id}")
        if len(evidence_plan_ids) != len(set(evidence_plan_ids)):
            raise AuthorityError(f"duplicate runtime input evidence: {input_id}")
        result[input_id] = (
            value_schema_id,
            source_kind,
            tuple(evidence_plan_ids),
        )
    return result


def _artifact_source_authority_id(schema_id: str, field_name: str) -> str:
    return f"{ARTIFACT_SOURCE_AUTHORITY_PREFIX}{schema_id}:{field_name}"


def _artifact_source_evidence_plan_id(source_kind: str) -> str:
    try:
        return ARTIFACT_SOURCE_EVIDENCE_BY_KIND[source_kind]
    except KeyError as exc:
        raise AuthorityError(
            f"artifact source kind has no evidence authority: {source_kind}"
        ) from exc


def _artifact_source_descriptor(
    schema_id: str,
    field_name: str,
    value_schema_id: str,
    source_kind: str,
) -> tuple[str, tuple[str, ...], str]:
    if source_kind == "DERIVED_EXPRESSION":
        try:
            digest_node_id = ARTIFACT_DERIVATION_DIGEST_BY_SCHEMA[schema_id]
        except KeyError as exc:
            raise AuthorityError(
                f"artifact schema lacks a derivation digest: {schema_id}"
            ) from exc
        return (
            "DIGEST_DAG_DERIVATION",
            (f"DIGEST_NODE:{digest_node_id}",),
            "Z.OBS.PY_AUTHORITY_V1",
        )
    if source_kind == "PARENT_OBSERVATION":
        try:
            observer_id = ARTIFACT_PARENT_OBSERVER_BY_SCHEMA[schema_id]
        except KeyError as exc:
            raise AuthorityError(
                f"artifact schema lacks a parent observer: {schema_id}"
            ) from exc
        return (
            "PARENT_OBSERVATION_PROJECTION",
            (f"OBSERVER:{observer_id}",),
            observer_id,
        )
    if source_kind == "CHILD_OBSERVATION":
        return (
            "CHILD_OBSERVATION_PROJECTION",
            ("OBSERVER:Z.OBS.WL_CHILD_VALUE_V1",),
            "Z.OBS.WL_CHILD_VALUE_V1",
        )
    if source_kind == "NESTED_AUTHORITY":
        if value_schema_id == "Z.VALUE.ARRAY.RESOLVED_EVIDENCE":
            nested_schema_id = "ResolvedEvidence"
        elif value_schema_id.startswith("Z.VALUE.ARTIFACT."):
            nested_schema_id = value_schema_id.removeprefix("Z.VALUE.ARTIFACT.")
        else:
            raise AuthorityError(
                f"nested source lacks an artifact value schema: "
                f"{schema_id}.{field_name}"
            )
        return (
            "NESTED_AUTHORITY_PROJECTION",
            (f"SCHEMA_AUTHORITY:{nested_schema_id}",),
            "Z.OBS.PY_AUTHORITY_V1",
        )
    raise AuthorityError(
        f"unknown artifact source kind: {schema_id}.{field_name}:{source_kind}"
    )


def _validate_artifact_source_catalog(
    spec: Mapping[str, Any],
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> dict[str, tuple[str, str, tuple[str, ...]]]:
    rows = [
        row
        for row in spec["immutable_inputs"]["runtime_authority_input_catalog"]
        if row[0].startswith(ARTIFACT_SOURCE_AUTHORITY_PREFIX)
    ]
    expected_rows: list[list[Any]] = []
    expected_runtime_rows: dict[str, tuple[str, str, tuple[str, ...]]] = {}
    schema_ids = {schema["schema_id"] for schema in spec["artifact_schemas"]}
    digest_ids = {node["digest_node_id"] for node in spec["digest_nodes"]}
    observer_ids = set(registries["observer_registry"])
    evidence_ids = set(registries["evidence_input_registry"])
    internal_edges: dict[str, tuple[str, ...]] = {}
    for schema in spec["artifact_schemas"]:
        schema_id = schema["schema_id"]
        for field in schema["fields"]:
            field_name, value_schema_id, source_kind = field[:3]
            if source_kind == "LITERAL":
                continue
            source_id = _artifact_source_authority_id(schema_id, field_name)
            producer_kind, predecessors, observer_id = _artifact_source_descriptor(
                schema_id, field_name, value_schema_id, source_kind
            )
            evidence = (_artifact_source_evidence_plan_id(source_kind),)
            expected_rows.append(
                [
                    source_id,
                    value_schema_id,
                    source_kind,
                    list(evidence),
                    producer_kind,
                    list(predecessors),
                    observer_id,
                    schema_id,
                    field_name,
                ]
            )
            expected_runtime_rows[source_id] = (value_schema_id, source_kind, evidence)
            internal_edges[source_id] = tuple(
                predecessor
                for predecessor in predecessors
                if predecessor.startswith(ARTIFACT_SOURCE_AUTHORITY_PREFIX)
            )
    if rows != expected_rows:
        raise AuthorityError("artifact source authority catalog drift")
    for row in rows:
        for predecessor in row[5]:
            if predecessor.startswith("DIGEST_NODE:"):
                if predecessor.removeprefix("DIGEST_NODE:") not in digest_ids:
                    raise AuthorityError(
                        "artifact source has unknown digest predecessor"
                    )
            elif predecessor.startswith("OBSERVER:"):
                if predecessor.removeprefix("OBSERVER:") not in observer_ids:
                    raise AuthorityError(
                        "artifact source has unknown observer predecessor"
                    )
            elif predecessor.startswith("SCHEMA_AUTHORITY:"):
                if predecessor.removeprefix("SCHEMA_AUTHORITY:") not in schema_ids:
                    raise AuthorityError(
                        "artifact source has unknown schema predecessor"
                    )
            elif predecessor.startswith(ARTIFACT_SOURCE_AUTHORITY_PREFIX):
                if predecessor not in expected_runtime_rows:
                    raise AuthorityError(
                        "artifact source has unknown field predecessor"
                    )
            else:
                raise AuthorityError("artifact source has an untyped predecessor")
        if any(evidence_id not in evidence_ids for evidence_id in row[3]):
            raise AuthorityError("artifact source has unknown evidence")
        if row[6] not in observer_ids:
            raise AuthorityError("artifact source has unknown observer")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(source_id: str) -> None:
        if source_id in visiting:
            raise AuthorityError("artifact source dependency DAG contains a cycle")
        if source_id in visited:
            return
        visiting.add(source_id)
        for predecessor in internal_edges[source_id]:
            visit(predecessor)
        visiting.remove(source_id)
        visited.add(source_id)

    for source_id in internal_edges:
        visit(source_id)
    return expected_runtime_rows


def _ordered_ast_authority_refs(node: Any) -> list[str]:
    refs: list[str] = []

    def visit(current: Any) -> None:
        if type(current) is not list or not current:
            return
        if current[0] == "CONST":
            return
        if current[0] == "AUTHORITY_REF":
            if len(current) == 2 and type(current[1]) is str:
                refs.append(current[1])
            return
        for child in current[1:]:
            visit(child)

    visit(node)
    if len(refs) != len(set(refs)):
        raise AuthorityError("typed AST repeats an authority dependency")
    return refs


def _tagged_literal_value_schema(
    tagged: Any,
    context: str,
) -> str:
    _validate_tagged_literal(tagged, context)
    tag = tagged[0]
    if tag == "s":
        return "Z.VALUE.STRING"
    if tag == "i":
        return "Z.VALUE.NONNEG_INT" if int(tagged[1]) >= 0 else "Z.VALUE.INT"
    if tag == "b":
        return "Z.VALUE.BOOL"
    if tag == "n":
        return "Z.VALUE.NULL"
    if tag == "h":
        return "Z.VALUE.HASH256"
    if tag == "d":
        return "Z.VALUE.DECIMAL"
    if tag == "a":
        return f"Z.VALUE.ARTIFACT.{tagged[1]}"
    raise AuthorityError(f"unhandled tagged literal in {context}")


def _value_schema_assignable(
    actual: str,
    expected: str,
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> bool:
    if actual == expected:
        return True
    if actual == "Z.VALUE.NONNEG_INT" and expected == "Z.VALUE.INT":
        return True
    if expected == "Z.VALUE.TAGGED_VALUE":
        return True
    values = registries["value_schema_registry"]
    if actual in values and expected in values:
        actual_type = values[actual]["type_id"]
        expected_type = values[expected]["type_id"]
        if actual_type == "Z.TYPE.ARRAY" and expected_type == "Z.TYPE.ARRAY":
            return expected == "Z.VALUE.ARRAY"
    return False


def _validate_tagged_literal_against_schema(
    tagged: Any,
    value_schema_id: str,
    context: str,
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> None:
    schema = registries["value_schema_registry"][value_schema_id]
    _validate_tagged_literal(tagged, context)
    if tagged[0] == "n":
        if schema["nullable"] is not True:
            raise AuthorityError(f"null is forbidden by {value_schema_id} in {context}")
        return
    actual = _tagged_literal_value_schema(tagged, context)
    if not _value_schema_assignable(actual, value_schema_id, registries):
        raise AuthorityError(
            f"typed AST result mismatch in {context}: {actual} != {value_schema_id}"
        )
    raw_value = tagged[1] if len(tagged) == 2 else tagged
    if tagged[0] == "i":
        raw_value = int(tagged[1])
    minimum = schema["minimum_or_null"]
    maximum = schema["maximum_or_null"]
    if minimum is not None and raw_value < minimum:
        raise AuthorityError(f"literal below schema minimum in {context}")
    if maximum is not None and raw_value > maximum:
        raise AuthorityError(f"literal above schema maximum in {context}")
    enum_values = schema["enum_values_or_null"]
    if enum_values is not None and raw_value not in enum_values:
        raise AuthorityError(f"literal outside schema enum in {context}")


def _infer_typed_ast_schema(
    node: Any,
    context: str,
    runtime_inputs: Mapping[str, tuple[str, str, tuple[str, ...]]],
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> str:
    _validate_ast(node, context)
    opcode = node[0]
    if opcode == "CONST":
        return _tagged_literal_value_schema(node[1], f"{context}.CONST")
    if opcode == "AUTHORITY_REF":
        reference = node[1]
        if reference in runtime_inputs:
            return runtime_inputs[reference][0]
        if reference in registries["catalog_registry"]:
            return "Z.VALUE.ARRAY"
        raise AuthorityError(
            f"unknown typed authority reference {reference} in {context}"
        )
    if opcode == "LENGTH":
        operand = _infer_typed_ast_schema(
            node[1], f"{context}.LENGTH", runtime_inputs, registries
        )
        if not _value_schema_assignable(operand, "Z.VALUE.ARRAY", registries):
            raise AuthorityError(f"LENGTH operand is not an array in {context}")
        return "Z.VALUE.NONNEG_INT"
    if opcode == "HASH":
        _infer_typed_ast_schema(node[1], f"{context}.HASH", runtime_inputs, registries)
        return "Z.VALUE.HASH256"
    if opcode in {"EQ", "LT", "LE", "AND", "OR", "NOT"}:
        for ordinal, child in enumerate(node[1:]):
            _infer_typed_ast_schema(
                child, f"{context}.{opcode}[{ordinal}]", runtime_inputs, registries
            )
        return "Z.VALUE.BOOL"
    if opcode in {
        "ABS",
        "ADD",
        "SUBTRACT",
        "MULTIPLY",
        "DIVIDE",
        "SQUARE",
        "SQRT",
        "LN",
        "MAX",
        "MIN",
        "WRAP_TO_PI",
    }:
        operand_schemas = [
            _infer_typed_ast_schema(
                child, f"{context}.{opcode}[{ordinal}]", runtime_inputs, registries
            )
            for ordinal, child in enumerate(node[1:])
        ]
        if not all(
            registries["value_schema_registry"][item]["type_id"]
            in {"Z.TYPE.INT", "Z.TYPE.NONNEG_INT", "Z.TYPE.DECIMAL"}
            for item in operand_schemas
        ):
            raise AuthorityError(f"nonnumeric operand in {context}")
        return (
            "Z.VALUE.DECIMAL"
            if any(item == "Z.VALUE.DECIMAL" for item in operand_schemas)
            else "Z.VALUE.INT"
        )
    if opcode == "CONCAT":
        operands = [
            _infer_typed_ast_schema(
                child, f"{context}.CONCAT[{ordinal}]", runtime_inputs, registries
            )
            for ordinal, child in enumerate(node[1:])
        ]
        if all(item == "Z.VALUE.STRING" for item in operands):
            return "Z.VALUE.STRING"
        if all(
            _value_schema_assignable(item, "Z.VALUE.ARRAY", registries)
            for item in operands
        ):
            return "Z.VALUE.ARRAY"
        raise AuthorityError(f"CONCAT operand type mismatch in {context}")
    raise AuthorityError(
        f"typed result inference is not defined for {opcode} in {context}"
    )


def _validate_typed_expression_semantics(
    spec: Mapping[str, Any],
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> None:
    runtime_inputs = _runtime_authority_input_index(spec, registries)
    for expression_id, row in registries["expected_expression_registry"].items():
        inferred = _infer_typed_ast_schema(
            row["typed_ast"], f"expression {expression_id}", runtime_inputs, registries
        )
        if not _value_schema_assignable(
            inferred, row["result_value_schema_id"], registries
        ):
            raise AuthorityError(f"expression result type mismatch: {expression_id}")
        observed_dependencies = _ordered_ast_authority_refs(row["typed_ast"])
        if observed_dependencies != row["ordered_dependency_ids"]:
            raise AuthorityError(
                f"expression dependency inventory/order mismatch: {expression_id}"
            )


def _validate_value_schema_semantics(
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> None:
    values = registries["value_schema_registry"]
    types = registries["type_registry"]
    null_rules = registries["null_rule_registry"]
    for value_schema_id, row in values.items():
        if row["type_id"] not in types:
            raise AuthorityError(f"unknown value-schema type: {value_schema_id}")
        if type(row["nullable"]) is not bool:
            raise AuthorityError(
                f"value-schema nullable is not boolean: {value_schema_id}"
            )
        null_rule_id = row["null_rule_id"]
        if null_rule_id not in null_rules:
            raise AuthorityError(f"unknown value-schema null rule: {value_schema_id}")
        if row["nullable"] != (null_rule_id == "Z.NULL.IS_NULL"):
            raise AuthorityError(
                f"value-schema nullability/rule drift: {value_schema_id}"
            )
        exact_length = row["exact_length_or_null"]
        if exact_length is not None:
            _require_plain_int(exact_length, f"{value_schema_id}.exact_length")
        minimum = row["minimum_or_null"]
        maximum = row["maximum_or_null"]
        if minimum is not None and type(minimum) not in {int, str}:
            raise AuthorityError(f"invalid schema minimum: {value_schema_id}")
        if maximum is not None and type(maximum) not in {int, str}:
            raise AuthorityError(f"invalid schema maximum: {value_schema_id}")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise AuthorityError(f"inverted schema bounds: {value_schema_id}")
        if row["type_id"] == "Z.TYPE.NONNEG_INT" and minimum != 0:
            raise AuthorityError(
                f"nonnegative schema lacks exact zero floor: {value_schema_id}"
            )
        enum_values = row["enum_values_or_null"]
        if enum_values is not None:
            if type(enum_values) is not list or len(enum_values) != len(
                {json.dumps(item, sort_keys=True) for item in enum_values}
            ):
                raise AuthorityError(
                    f"invalid/duplicate schema enum: {value_schema_id}"
                )
        element = row["element_schema_id_or_null"]
        members = row["field_schema_ids_or_null"]
        if element is not None and element not in values:
            raise AuthorityError(f"unknown element schema: {value_schema_id}")
        if members is not None:
            if type(members) is not list or any(item not in values for item in members):
                raise AuthorityError(f"unknown field schema: {value_schema_id}")
            if exact_length != len(members):
                raise AuthorityError(f"compound schema arity drift: {value_schema_id}")
            if element is not None:
                raise AuthorityError(
                    f"compound schema has two element authorities: {value_schema_id}"
                )
        if (element is not None or members is not None) and row[
            "type_id"
        ] != "Z.TYPE.ARRAY":
            raise AuthorityError(
                f"non-array schema has element/member rows: {value_schema_id}"
            )


def _validate_artifact_field_name_types(
    spec: Mapping[str, Any],
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> None:
    values = registries["value_schema_registry"]
    nullable_scalar_ids = {
        "Z.VALUE.OPTIONAL_HASH256",
        "Z.VALUE.OPTIONAL_INT",
        "Z.VALUE.OPTIONAL_STRING",
    }
    exact_overrides = {
        (
            "parent_event",
            "ordered_resolved_evidence",
        ): "Z.VALUE.ARRAY.RESOLVED_EVIDENCE",
        ("StreamIdentity", "within_frozen_limit"): "Z.VALUE.BOOL",
        ("ResolvedEvidence", "kind"): "Z.VALUE.STRING",
        ("SourceLedger", "start_end_equal_or_null"): "Z.VALUE.OPTIONAL_BOOL",
    }
    for schema in spec["artifact_schemas"]:
        schema_id = schema["schema_id"]
        for field in schema["fields"]:
            name, value_schema_id = field[:2]
            expected = exact_overrides.get((schema_id, name))
            if expected is not None and value_schema_id != expected:
                raise AuthorityError(
                    f"artifact field exact type drift: {schema_id}.{name}"
                )
            if name.endswith("_or_null") and value_schema_id not in (
                nullable_scalar_ids | {"Z.VALUE.OPTIONAL_BOOL"}
            ):
                raise AuthorityError(
                    f"nullable artifact field uses nonnullable schema: "
                    f"{schema_id}.{name}"
                )
            if (
                "sha256" in name
                and not name.endswith("sha256s")
                and values[value_schema_id]["type_id"] != "Z.TYPE.HASH256"
            ):
                raise AuthorityError(
                    f"hash-named artifact field uses non-hash schema: "
                    f"{schema_id}.{name}"
                )


def _predicate_definition_projection(definition: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        definition["name"],
        definition["field_id"],
        definition["value_type_id"],
        definition["nullable"],
        definition["null_rule_id"],
        definition["comparison_id"],
        definition["expected_value_schema_id"],
        definition["expected_kind"],
        definition["expected_literal_or_null"],
        definition["expected_expression_id_or_null"],
        tuple(definition["evidence_plan_ids"]),
    )


def _validate_terminal_predicate_contract(spec: Mapping[str, Any]) -> None:
    families = {row["family_id"]: row for row in spec["predicate_families"]}
    p00 = families.get("Z.FAMILY.P00")
    p17 = families.get("Z.FAMILY.P17")
    if p00 is None or p17 is None:
        raise AuthorityError("missing P00/P17 predicate family")
    common_operations = [
        "compatibility",
        "source_load_micro",
        "full_sentinel",
        "official",
    ]
    for row, stage, expected in (
        (p00, 0, EXPECTED_P00_PREDICATES),
        (p17, 17, EXPECTED_P17_PREDICATES),
    ):
        if (
            row["operations"] != common_operations
            or row["stage_ordinal"] != stage
            or row["expansion_mode"] != "SIMPLE"
            or row["owner"] != "PARENT_OBSERVED"
            or row["executor_id"] != "Z.EXEC.PARENT_AUTHORITY_V1"
            or row["science_capable"] is not False
            or row["record_ordinals"] != []
            or row["compatibility_cases"] != []
        ):
            raise AuthorityError(f"P{stage:02d} family contract drift")
        observed = tuple(
            _predicate_definition_projection(definition)
            for definition in row["predicate_definitions"]
        )
        if observed != expected:
            raise AuthorityError(f"P{stage:02d} predicate semantic contract drift")


def _validate_semantic_section_commitments(spec: Mapping[str, Any]) -> None:
    for section, expected in EXPECTED_SEMANTIC_SECTION_SHA256.items():
        observed = sha256_bytes(
            b"SCHWO-V31Z\0SPEC-SECTION\0"
            + section.encode("ascii")
            + b"\0"
            + canonical_object_bytes(spec[section])
        )
        if observed != expected:
            raise AuthorityError(f"semantic section commitment drift: {section}")


def _validate_registry_semantics(
    spec: Mapping[str, Any], registries: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> None:
    if any(
        row["algorithm_kind"] not in ALGORITHM_KINDS
        for row in registries["algorithm_registry"].values()
    ):
        raise AuthorityError("algorithm registry contains an unapproved algorithm kind")
    if any(
        row["policy_kind"] not in POLICY_KINDS
        for row in registries["policy_registry"].values()
    ):
        raise AuthorityError("policy registry contains an unapproved policy kind")
    for row_id, row in registries["algorithm_registry"].items():
        if type(row["science_capable"]) is not bool:
            raise AuthorityError(f"algorithm science flag is not boolean: {row_id}")
        table = row["closed_typed_ast_or_literal_table"]
        _validate_ast(table, f"algorithm {row_id}", allow_literal_table=True)
    for row_id, row in registries["expected_expression_registry"].items():
        _validate_ast(row["typed_ast"], f"expression {row_id}")
        if type(row["ordered_dependency_ids"]) is not list or any(
            type(item) is not str for item in row["ordered_dependency_ids"]
        ):
            raise AuthorityError(f"invalid dependency list in expression {row_id}")
    for row_id, row in registries["selector_registry"].items():
        _validate_ast(
            row["closed_typed_selector_ast"], f"selector {row_id}", selector=True
        )
    for row_id, row in registries["json_shape_registry"].items():
        if row["shape_kind"] not in {
            "STRING",
            "INTEGER",
            "BOOLEAN",
            "NULL",
            "ARRAY",
            "OBJECT",
        }:
            raise AuthorityError(f"unknown JSON shape kind in {row_id}")
        if row["shape_kind"] == "OBJECT" and (
            row["additional_members_allowed"] is not False
            or row["duplicate_members_allowed"] is not False
        ):
            raise AuthorityError(
                "authority objects cannot admit extra/duplicate members"
            )
    for matrix_id, matrix in registries["null_matrix_registry"].items():
        count = _require_plain_int(
            matrix["operand_count"], f"{matrix_id}.operand_count"
        )
        expected = 2**count
        if matrix["required_bitmap_count"] != expected:
            raise AuthorityError(f"null matrix cardinality mismatch: {matrix_id}")
        rules = matrix["ordered_null_rule_ids"]
        if type(rules) is not list or len(rules) != expected:
            raise AuthorityError(f"null matrix rule inventory mismatch: {matrix_id}")
        observed = []
        for ordinal, rule_id in enumerate(rules):
            if rule_id not in registries["null_rule_registry"]:
                raise AuthorityError(f"unknown null rule {rule_id} in {matrix_id}")
            rule = registries["null_rule_registry"][rule_id]
            if rule["null_matrix_id"] != matrix_id or rule["row_ordinal"] != ordinal:
                raise AuthorityError(
                    f"null-rule backreference/order mismatch: {rule_id}"
                )
            observed.append(rule["ordered_operand_null_bitmap"])
        expected_bits = [
            [bool((ordinal >> shift) & 1) for shift in reversed(range(count))]
            for ordinal in range(expected)
        ]
        if (
            observed != expected_bits
            or matrix["bitmap_order"] != "LEXICOGRAPHIC_FALSE_BEFORE_TRUE"
        ):
            raise AuthorityError(
                f"null matrix is not exhaustive/canonical: {matrix_id}"
            )
        comparison_id = matrix["comparison_id"]
        if comparison_id == "VALUE_SCHEMA":
            if matrix_id != "Z.NULL.MATRIX.VALUE":
                raise AuthorityError(
                    f"unapproved value-schema null matrix: {matrix_id}"
                )
        else:
            if comparison_id not in registries["comparison_registry"]:
                raise AuthorityError(f"null matrix has unknown comparison: {matrix_id}")
            comparison = registries["comparison_registry"][comparison_id]
            if comparison["null_matrix_id"] != matrix_id:
                raise AuthorityError(
                    f"null-matrix/comparison backreference mismatch: {matrix_id}"
                )
    for ordinal, row in enumerate(spec["conformance_vector_plans"]):
        if type(row) is not list or len(row) != len(CONFORMANCE_PLAN_FIELDS):
            raise AuthorityError(f"conformance_vector_plans[{ordinal}] shape mismatch")
    for ordinal, row in enumerate(spec["mutation_plans"]):
        if type(row) is not list or len(row) != len(MUTATION_PLAN_FIELDS):
            raise AuthorityError(f"mutation_plans[{ordinal}] shape mismatch")


def _compatibility_case_family(case_id: str) -> str:
    match = re.fullmatch(r"Z-COMP-([A-Z-]+)\.(.+)", case_id)
    if match is None or match.group(1) not in COMPATIBILITY_OPERATION_BY_CASE_FAMILY:
        raise AuthorityError(f"unknown compatibility case family: {case_id}")
    return match.group(1)


def _compatibility_fixture_authority(payload: Sequence[Any]) -> str:
    if type(payload) is not list or len(payload) != len(
        COMPATIBILITY_FIXTURE_PAYLOAD_FIELDS
    ):
        raise AuthorityError("compatibility fixture payload field-count mismatch")
    output = payload[15]
    return artifact_hash(
        "compatibility-fixture-authority-v2",
        1,
        [
            I(payload[2]),
            S(payload[3]),
            S(payload[4]),
            S(payload[5]),
            I(payload[6]),
            S(payload[7]),
            S(payload[8]),
            S(payload[9]),
            S(payload[10]),
            S(payload[11]),
            S(payload[12]),
            H(payload[13]),
            S(payload[14]),
            N() if output is None else output,
            S(payload[16]),
            N() if payload[17] is None else S(payload[17]),
            N() if payload[18] is None else S(payload[18]),
            I(payload[19]),
        ],
    )


def _bootstrap_fixture_authority(payload: Sequence[Any]) -> str:
    if type(payload) is not list or len(payload) != len(
        BOOTSTRAP_FIXTURE_PAYLOAD_FIELDS
    ):
        raise AuthorityError("bootstrap fixture payload field-count mismatch")
    return artifact_hash(
        "conformance-bootstrap-fixture-authority-v1",
        1,
        [
            I(payload[2]),
            S(payload[3]),
            S(payload[4]),
            S(payload[5]),
            S(payload[6]),
            H(payload[7]),
            S(payload[8]),
            payload[9],
            I(payload[10]),
        ],
    )


def _decode_literal_hex(raw_hex: Any, context: str) -> bytes:
    if (
        type(raw_hex) is not str
        or not raw_hex
        or len(raw_hex) % 2 != 0
        or re.fullmatch(r"[0-9a-f]+", raw_hex) is None
    ):
        raise AuthorityError(f"{context} is not nonempty canonical raw hex")
    raw = bytes.fromhex(raw_hex)
    if not raw or raw.hex() != raw_hex:
        raise AuthorityError(f"{context} raw-byte round trip failed")
    return raw


def _zero_science_counters(value: Any) -> bool:
    return (
        type(value) is list
        and len(value) == 19
        and value[:2] == ["a", "ScienceCounters"]
        and all(item == ["i", "0"] for item in value[2:])
    )


def _validate_fixture_conformance_closure(
    spec: Mapping[str, Any],
    registries: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> None:
    """Close literal fixture -> constructor -> vector authority before mkdir.

    The spec is the sole declarative source, but the compiler independently
    decodes every raw fixture, recomputes its raw digest, typed fixture
    authority, encoded vector bytes, and vector digest.  Empty/label-only
    inputs and any algorithm/operation/fixture/vector drift fail here, before
    an output directory can be created.
    """

    algorithm = registries["algorithm_registry"].get(COMPATIBILITY_FIXTURE_ALGORITHM_ID)
    expected_algorithm = {
        "algorithm_id": COMPATIBILITY_FIXTURE_ALGORITHM_ID,
        "algorithm_kind": "PURE_TYPED_AST",
        "ordered_input_value_schema_ids": ["Z.VALUE.STRING"],
        "output_value_schema_id": "Z.VALUE.TAGGED_VALUE",
        "closed_typed_ast_or_literal_table": [
            "COMPATIBILITY_OPERATION_TABLE",
            1,
            *EXPECTED_COMPATIBILITY_OPERATION_TABLE,
        ],
        "null_rule_id": "Z.NULL.NEVER",
        "ordered_success_reason_codes": ["Z.REASON.VALID"],
        "ordered_failure_reason_codes": [
            "Z.REASON.INVALID",
            "Z.REASON.TYPE_MISMATCH",
            "Z.REASON.HASH_MISMATCH",
            "Z.REASON.ORDER_MISMATCH",
            "Z.REASON.POLICY_VIOLATION",
            "Z.REASON.PROCESS_FAILURE",
        ],
        "science_capable": False,
    }
    if algorithm != expected_algorithm:
        raise AuthorityError("compatibility fixture algorithm/table drift")

    case_keys = {
        "case_id",
        "executor_id",
        "expected_disposition",
        "fixture_constructor_id",
        "input_fixture_id",
        "observer_id",
        "order",
        "owner",
        "science_call_count",
        "stage_ordinal",
        "subject_predicate_id",
    }
    cases: list[Mapping[str, Any]] = []
    for family in spec["predicate_families"]:
        for case in family.get("compatibility_cases", []):
            _require_exact_keys(case, case_keys, "compatibility case")
            cases.append(case)
    if len(cases) != 118:
        raise AuthorityError("compatibility fixture cardinality is not exactly 118")
    local_orders: dict[int, list[int]] = {}
    for case in cases:
        if (
            type(case["stage_ordinal"]) is not int
            or not 2 <= case["stage_ordinal"] <= 14
        ):
            raise AuthorityError(f"invalid compatibility stage: {case['case_id']}")
        if type(case["order"]) is not int or case["science_call_count"] != 0:
            raise AuthorityError(
                f"compatibility order/science drift: {case['case_id']}"
            )
        local_orders.setdefault(case["stage_ordinal"], []).append(case["order"])
    if any(values != list(range(len(values))) for values in local_orders.values()):
        raise AuthorityError("compatibility stage-local case order is noncontiguous")

    fixture_rows = spec["fixture_constructor_registry"]
    if type(fixture_rows) is not list or len(fixture_rows) != 159:
        raise AuthorityError("fixture registry must contain exact 118+41 rows")
    fixture_by_id = registries["fixture_constructor_registry"]
    expected_fixture_ids: list[str] = []
    vectors = spec["conformance_vector_registry"]
    plans = spec["conformance_vector_plans"]
    if len(vectors) != 159 or len(plans) != 159:
        raise AuthorityError("conformance registry/plan cardinality drift")
    vector_by_id = {row[0]: row for row in vectors}
    plan_by_id = {row[0]: row for row in plans}
    reason_rows = registries["reason_code_registry"]

    for case_ordinal, case in enumerate(cases):
        constructor_id = f"Z.FIXTURE.COMPAT.{case_ordinal:03d}"
        if case["fixture_constructor_id"] != constructor_id:
            raise AuthorityError(
                f"compatibility constructor ID/order drift: {case_ordinal}"
            )
        expected_fixture_ids.append(constructor_id)
        constructor = fixture_by_id.get(constructor_id)
        if constructor is None:
            raise AuthorityError(f"missing compatibility constructor: {constructor_id}")
        if (
            constructor["constructor_kind"] != "EXACT_RAW_INPUT_EXPECTED_OUTPUT"
            or constructor["ordered_input_schema_ids"] != ["Z.VALUE.STRING"]
            or constructor["output_schema_id"] != "Z.VALUE.TAGGED_VALUE"
            or constructor["algorithm_id"] != COMPATIBILITY_FIXTURE_ALGORITHM_ID
        ):
            raise AuthorityError(
                f"compatibility constructor contract drift: {constructor_id}"
            )
        payload = constructor["literal_parameters"]
        if type(payload) is not list or len(payload) != len(
            COMPATIBILITY_FIXTURE_PAYLOAD_FIELDS
        ):
            raise AuthorityError(f"compatibility payload shape drift: {constructor_id}")
        mapped = dict(zip(COMPATIBILITY_FIXTURE_PAYLOAD_FIELDS, payload, strict=True))
        expected_operation = COMPATIBILITY_OPERATION_BY_CASE_FAMILY[
            _compatibility_case_family(case["case_id"])
        ]
        exact_case_projection = {
            "payload_schema": "compatibility-fixture-v2",
            "payload_revision": 1,
            "case_ordinal": case_ordinal,
            "case_id": case["case_id"],
            "input_fixture_id": case["input_fixture_id"],
            "subject_predicate_id": case["subject_predicate_id"],
            "stage_ordinal": case["stage_ordinal"],
            "owner": case["owner"],
            "observer_id": case["observer_id"],
            "executor_id": case["executor_id"],
            "operation_id": expected_operation,
            "algorithm_id": COMPATIBILITY_FIXTURE_ALGORITHM_ID,
            "case_expected_disposition": case["expected_disposition"],
            "science_call_count": 0,
        }
        for field, expected in exact_case_projection.items():
            if mapped[field] != expected:
                raise AuthorityError(
                    f"compatibility payload/case mismatch: {constructor_id}.{field}"
                )
        raw = _decode_literal_hex(mapped["raw_input_hex"], constructor_id)
        if len(raw) > 1_048_576:
            raise AuthorityError(
                f"compatibility raw input exceeds exact cap: {constructor_id}"
            )
        observed_raw_sha = sha256_bytes(raw)
        if mapped["raw_input_sha256"] != observed_raw_sha:
            raise AuthorityError(
                f"compatibility raw input digest mismatch: {constructor_id}"
            )
        output = mapped["expected_tagged_value_or_null"]
        if mapped["expected_kind"] == "TYPED_VALUE":
            if output is None or case["expected_disposition"] == "REJECT":
                raise AuthorityError(
                    f"positive compatibility fixture union drift: {constructor_id}"
                )
            _validate_tagged_value(output, f"{constructor_id}.expected_output")
            if (
                mapped["reject_reason_or_null"] is not None
                or mapped["earliest_rejection_state_or_null"] is not None
            ):
                raise AuthorityError(
                    f"positive compatibility rejection fields set: {constructor_id}"
                )
            vector_result = output
        elif mapped["expected_kind"] == "REJECT":
            reason_id = mapped["reject_reason_or_null"]
            if (
                output is not None
                or case["expected_disposition"] != "REJECT"
                or reason_id not in reason_rows
                or mapped["earliest_rejection_state_or_null"]
                != reason_rows[reason_id]["earliest_rejection_state"]
            ):
                raise AuthorityError(
                    f"negative compatibility fixture union drift: {constructor_id}"
                )
            vector_result = A(
                "compatibility-rejection-v1",
                S(reason_id),
                S(mapped["earliest_rejection_state_or_null"]),
            )
        else:
            raise AuthorityError(
                f"unknown compatibility expected kind: {constructor_id}"
            )
        fixture_authority = _compatibility_fixture_authority(payload)
        if constructor["expected_output_authority_sha256"] != fixture_authority:
            raise AuthorityError(
                f"compatibility fixture authority mismatch: {constructor_id}"
            )

        vector_id = f"Z.VECTOR.COMPAT.{case_ordinal:03d}"
        vector = vector_by_id.get(vector_id)
        if vector is None or vector[3] != "COMPATIBILITY_CASE":
            raise AuthorityError(f"missing compatibility vector: {vector_id}")
        if vector[4] != [constructor_id] or vector[5] != "compatibility":
            raise AuthorityError(
                f"compatibility vector fixture binding drift: {vector_id}"
            )
        expected_typed_inputs = [
            H(fixture_authority),
            H(observed_raw_sha),
            S(expected_operation),
        ]
        expected_vector_raw = enc(
            "compatibility-case-vector-v2",
            1,
            [*expected_typed_inputs, vector_result],
        )
        if (
            vector[6] != expected_typed_inputs
            or vector[7] != expected_vector_raw.hex()
            or vector[8] != sha256_bytes(expected_vector_raw)
            or vector[9:12] != ["ACCEPT_AND_ADVANCE", "Z.REASON.VALID", "VALIDATED"]
            or not _zero_science_counters(vector[12])
        ):
            raise AuthorityError(f"compatibility vector byte/digest drift: {vector_id}")
        plan = plan_by_id.get(vector[1])
        if plan is None or plan[4] != constructor_id:
            raise AuthorityError(
                f"compatibility plan fixture binding drift: {vector_id}"
            )

    noncompat_vectors = [row for row in vectors if row[3] != "COMPATIBILITY_CASE"]
    if len(noncompat_vectors) != 41:
        raise AuthorityError("bootstrap vector cardinality is not exactly 41")
    for vector in noncompat_vectors:
        vector_ordinal = vector[2]
        constructor_id = f"Z.FIXTURE.BOOTSTRAP.{vector_ordinal:03d}"
        expected_fixture_ids.append(constructor_id)
        constructor = fixture_by_id.get(constructor_id)
        if constructor is None:
            raise AuthorityError(f"missing bootstrap constructor: {constructor_id}")
        if (
            constructor["constructor_kind"] != "EXACT_RAW_INPUT_EXPECTED_HASH"
            or constructor["ordered_input_schema_ids"] != ["Z.VALUE.STRING"]
            or constructor["output_schema_id"] != "Z.VALUE.HASH256"
            or constructor["algorithm_id"] != "Z.ALG.SHA256"
        ):
            raise AuthorityError(
                f"bootstrap constructor contract drift: {constructor_id}"
            )
        payload = constructor["literal_parameters"]
        if type(payload) is not list or len(payload) != len(
            BOOTSTRAP_FIXTURE_PAYLOAD_FIELDS
        ):
            raise AuthorityError(f"bootstrap payload shape drift: {constructor_id}")
        mapped = dict(zip(BOOTSTRAP_FIXTURE_PAYLOAD_FIELDS, payload, strict=True))
        expected_projection = {
            "payload_schema": "conformance-bootstrap-fixture-v1",
            "payload_revision": 1,
            "vector_ordinal": vector_ordinal,
            "vector_id": vector[0],
            "scope_id": vector[3],
            "operation_or_schema_id": vector[5],
            "expected_kind": "HASH256",
            "science_call_count": 0,
        }
        for field, expected in expected_projection.items():
            if mapped[field] != expected:
                raise AuthorityError(
                    f"bootstrap payload/vector mismatch: {constructor_id}.{field}"
                )
        raw = _decode_literal_hex(mapped["raw_input_hex"], constructor_id)
        observed_raw_sha = sha256_bytes(raw)
        if (
            mapped["raw_input_sha256"] != observed_raw_sha
            or mapped["expected_tagged_value"] != H(observed_raw_sha)
            or vector[7] != raw.hex()
            or vector[8] != observed_raw_sha
            or vector[4] != [constructor_id]
            or not _zero_science_counters(vector[12])
        ):
            raise AuthorityError(f"bootstrap raw/vector digest drift: {constructor_id}")
        fixture_authority = _bootstrap_fixture_authority(payload)
        if constructor["expected_output_authority_sha256"] != fixture_authority:
            raise AuthorityError(
                f"bootstrap fixture authority mismatch: {constructor_id}"
            )
        plan = plan_by_id.get(vector[1])
        if plan is None or plan[4] != constructor_id:
            raise AuthorityError(
                f"bootstrap plan fixture binding drift: {constructor_id}"
            )

    if [row[0] for row in fixture_rows] != expected_fixture_ids:
        raise AuthorityError(
            "fixture registry has missing/extra/reordered constructors"
        )
    if any(type(row[4]) is not list or len(row[4]) != 1 for row in vectors):
        raise AuthorityError(
            "every conformance vector must bind exactly one initial fixture"
        )


def _validate_artifact_catalog(
    spec: Mapping[str, Any], registries: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> None:
    schemas = spec["artifact_schemas"]
    expected_order = [*PRIMARY_SCHEMA_IDS, *NESTED_SCHEMA_IDS]
    if (
        type(schemas) is not list
        or [row.get("schema_id") for row in schemas if type(row) is dict]
        != expected_order
    ):
        raise AuthorityError("artifact schema ID/order inventory mismatch")
    value_schema_ids = set(registries["value_schema_registry"])
    digest_ids = {row["digest_node_id"] for row in spec["digest_nodes"]}
    runtime_inputs = {
        row[0]
        for row in spec["immutable_inputs"].get("runtime_authority_input_catalog", [])
        if type(row) is list and row
    }
    runtime_input_rows = _runtime_authority_input_index(spec, registries)
    expected_artifact_source_rows = _validate_artifact_source_catalog(spec, registries)
    for schema in schemas:
        _require_exact_keys(
            schema,
            {"schema_id", "schema_revision", "scope", "fields"},
            f"artifact schema {schema.get('schema_id')}",
        )
        schema_id = schema["schema_id"]
        if schema["schema_revision"] != 1:
            raise AuthorityError(f"artifact schema revision drift: {schema_id}")
        if schema["scope"] != EXPECTED_ARTIFACT_SCOPES[schema_id]:
            raise AuthorityError(f"artifact schema scope drift: {schema_id}")
        expected_fields = (
            (*SESSION_PREFIX, *PRIMARY_SCHEMA_SUFFIXES[schema_id])
            if schema_id in PRIMARY_SCHEMA_IDS[:11]
            else (*OPERATION_ROOT_PREFIX, *PRIMARY_SCHEMA_SUFFIXES[schema_id])
            if schema_id in PRIMARY_SCHEMA_IDS[11:]
            else NESTED_SCHEMA_FIELDS[schema_id]
        )
        fields = schema["fields"]
        if type(fields) is not list or len(fields) != len(expected_fields):
            raise AuthorityError(f"artifact field count mismatch: {schema_id}")
        if [row[0] if type(row) is list and row else None for row in fields] != list(
            expected_fields
        ):
            raise AuthorityError(f"artifact field order mismatch: {schema_id}")
        for field_ordinal, field in enumerate(fields):
            if type(field) is not list or len(field) != len(ARTIFACT_FIELD_FIELDS):
                raise AuthorityError(
                    f"artifact field descriptor mismatch: {schema_id}[{field_ordinal}]"
                )
            mapped = dict(zip(ARTIFACT_FIELD_FIELDS, field, strict=True))
            if mapped["value_schema_id"] not in value_schema_ids:
                raise AuthorityError(
                    f"unknown field value schema in {schema_id}.{mapped['name']}"
                )
            if mapped["value_source_kind"] not in {
                "LITERAL",
                "DERIVED_EXPRESSION",
                "PARENT_OBSERVATION",
                "CHILD_OBSERVATION",
                "NESTED_AUTHORITY",
            }:
                raise AuthorityError(
                    f"unknown field source kind in {schema_id}.{mapped['name']}"
                )
            _validate_ast(
                mapped["value_rule"], f"{schema_id}.{mapped['name']}.value_rule"
            )
            dependencies = mapped["ordered_digest_dependency_ids"]
            if type(dependencies) is not list or any(
                type(item) is not str for item in dependencies
            ):
                raise AuthorityError(
                    f"invalid field dependencies in {schema_id}.{mapped['name']}"
                )
            for dependency in dependencies:
                if dependency not in runtime_inputs and dependency not in digest_ids:
                    raise AuthorityError(
                        f"unresolved field dependency {dependency} in {schema_id}.{mapped['name']}"
                    )
            rule = mapped["value_rule"]
            if mapped["value_source_kind"] == "LITERAL":
                if rule[0] != "CONST" or dependencies:
                    raise AuthorityError(
                        f"literal field rule/dependency drift: {schema_id}.{mapped['name']}"
                    )
                _validate_tagged_literal_against_schema(
                    rule[1],
                    mapped["value_schema_id"],
                    f"{schema_id}.{mapped['name']}",
                    registries,
                )
            else:
                if rule[0] != "AUTHORITY_REF" or len(rule) != 2:
                    raise AuthorityError(
                        f"nonliteral field lacks one typed authority ref: {schema_id}.{mapped['name']}"
                    )
                reference = rule[1]
                if reference.startswith(ARTIFACT_SELF_REFERENCE_PREFIX):
                    raise AuthorityError(
                        f"same-field artifact authority is forbidden: "
                        f"{schema_id}.{mapped['name']}"
                    )
                expected_reference = _artifact_source_authority_id(
                    schema_id, mapped["name"]
                )
                if reference != expected_reference:
                    raise AuthorityError(
                        f"artifact source authority ID drift: "
                        f"{schema_id}.{mapped['name']}"
                    )
                if dependencies != [reference]:
                    raise AuthorityError(
                        f"field dependency does not match authority ref: {schema_id}.{mapped['name']}"
                    )
                if reference not in runtime_input_rows:
                    raise AuthorityError(
                        f"field authority ref is not source-bound: {schema_id}.{mapped['name']}"
                    )
                input_schema_id, input_source_kind, _evidence = runtime_input_rows[
                    reference
                ]
                if input_schema_id != mapped["value_schema_id"]:
                    raise AuthorityError(
                        f"field authority type mismatch: {schema_id}.{mapped['name']}"
                    )
                if input_source_kind != mapped["value_source_kind"]:
                    raise AuthorityError(
                        f"field authority source mismatch: {schema_id}.{mapped['name']}"
                    )
                expected_evidence = (
                    _artifact_source_evidence_plan_id(input_source_kind),
                )
                if _evidence != expected_evidence:
                    raise AuthorityError(
                        f"artifact source evidence mismatch: "
                        f"{schema_id}.{mapped['name']}"
                    )
                expected_artifact_source_rows[reference] = (
                    mapped["value_schema_id"],
                    mapped["value_source_kind"],
                    expected_evidence,
                )
    observed_artifact_source_rows = {
        input_id: row
        for input_id, row in runtime_input_rows.items()
        if input_id.startswith(ARTIFACT_SOURCE_AUTHORITY_PREFIX)
    }
    if observed_artifact_source_rows != expected_artifact_source_rows:
        raise AuthorityError("artifact source authority inventory is not exact")
    for schema in schemas:
        value_schema_id = f"Z.VALUE.ARTIFACT.{schema['schema_id']}"
        if value_schema_id not in registries["value_schema_registry"]:
            raise AuthorityError(
                f"missing compound value schema: {schema['schema_id']}"
            )
        value_schema = registries["value_schema_registry"][value_schema_id]
        expected_members = [field[1] for field in schema["fields"]]
        if (
            value_schema["exact_length_or_null"] != len(expected_members)
            or value_schema["field_schema_ids_or_null"] != expected_members
        ):
            raise AuthorityError(
                f"compound value-schema field projection drift: {schema['schema_id']}"
            )


def validate_spec(
    spec_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, dict[str, Any]]]]:
    spec = strict_load_json(spec_path)
    if type(spec) is not dict:
        raise AuthorityError("spec top level must be an object")
    if set(spec) != TOP_LEVEL_KEYS:
        raise AuthorityError(
            f"spec top-level mismatch: missing={sorted(TOP_LEVEL_KEYS - set(spec))} "
            f"extra={sorted(set(spec) - TOP_LEVEL_KEYS)}"
        )
    if spec["schema"] != SCHEMA or spec["gate_id"] != GATE_ID:
        raise AuthorityError("spec schema/gate mismatch")
    if spec["spec_revision"] != SPEC_REVISION:
        raise AuthorityError("spec revision mismatch")
    registries = {name: _index_registry(spec, name) for name in REGISTRY_ID_FIELDS}
    _validate_execution_contract(spec)
    _validate_registry_semantics(spec, registries)
    _validate_fixture_conformance_closure(spec, registries)
    _validate_value_schema_semantics(registries)
    _validate_typed_expression_semantics(spec, registries)
    _validate_artifact_field_name_types(spec, registries)
    _validate_artifact_catalog(spec, registries)
    _validate_terminal_predicate_contract(spec)
    _topological_digest_nodes(spec["digest_nodes"])
    _validate_authority_progression(spec)
    _validate_references(spec, registries)
    _validate_forbidden_semantics(spec)
    _validate_semantic_section_commitments(spec)
    return spec, registries


def _validate_references(
    spec: Mapping[str, Any], registries: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> None:
    globally_seen: dict[str, str] = {}
    for registry_name, registry in registries.items():
        for row_id in registry:
            prior = globally_seen.get(row_id)
            if prior is not None:
                raise AuthorityError(
                    f"authority ID {row_id} is multiply defined in {prior}/{registry_name}"
                )
            globally_seen[row_id] = registry_name
    runtime_inputs = {
        row[0]: row
        for row in spec["immutable_inputs"].get("runtime_authority_input_catalog", [])
        if type(row) is list and len(row) == 4
    }
    expression_ids = set(registries["expected_expression_registry"])
    value_ids = set(registries["value_schema_registry"])
    algorithm_ids = set(registries["algorithm_registry"])
    policy_ids = set(registries["policy_registry"])
    reason_ids = set(registries["reason_code_registry"])
    digest_ids = {row["digest_node_id"] for row in spec["digest_nodes"]}
    family_ids: set[str] = set()
    for family in spec["predicate_families"]:
        _require_exact_keys(
            family,
            {
                "family_id",
                "operations",
                "stage_ordinal",
                "expansion_mode",
                "owner",
                "observer_id",
                "executor_id",
                "science_capable",
                "record_ordinals",
                "predicate_definitions",
                "compatibility_cases",
            },
            "predicate family",
        )
        if family["family_id"] in family_ids:
            raise AuthorityError(f"duplicate predicate family: {family['family_id']}")
        family_ids.add(family["family_id"])
        if family["expansion_mode"] not in {
            "SIMPLE",
            "RECORD_MAJOR",
            "COMPATIBILITY_CASES",
        }:
            raise AuthorityError(
                f"unknown predicate expansion mode: {family['family_id']}"
            )
        if type(family["science_capable"]) is not bool:
            raise AuthorityError(
                f"family science flag is not boolean: {family['family_id']}"
            )
        for name, registry in (
            ("observer_id", "observer_registry"),
            ("executor_id", "executor_registry"),
        ):
            if family[name] not in registries[registry]:
                raise AuthorityError(f"family {family['family_id']} has unknown {name}")
        for definition in family.get("predicate_definitions", []):
            _require_exact_keys(
                definition,
                {
                    "name",
                    "field_id",
                    "value_type_id",
                    "nullable",
                    "null_rule_id",
                    "comparison_id",
                    "expected_value_schema_id",
                    "expected_kind",
                    "expected_literal_or_null",
                    "expected_expression_id_or_null",
                    "evidence_plan_ids",
                },
                f"predicate definition {family['family_id']}",
            )
            checks = (
                ("value_type_id", "type_registry"),
                ("null_rule_id", "null_rule_registry"),
                ("comparison_id", "comparison_registry"),
                ("expected_value_schema_id", "value_schema_registry"),
            )
            for field, registry in checks:
                if definition[field] not in registries[registry]:
                    raise AuthorityError(
                        f"predicate {family['family_id']}/{definition['name']} has unknown {field}"
                    )
            expression_id = definition.get("expected_expression_id_or_null")
            if (
                expression_id is not None
                and expression_id not in registries["expected_expression_registry"]
            ):
                raise AuthorityError(f"unknown expected expression: {expression_id}")
            for evidence_id in definition["evidence_plan_ids"]:
                if evidence_id not in registries["evidence_input_registry"]:
                    raise AuthorityError(f"unknown evidence plan: {evidence_id}")
            if definition["expected_kind"] == "LITERAL":
                if expression_id is not None:
                    raise AuthorityError("literal predicate cannot carry an expression")
            elif definition["expected_kind"] == "DERIVED":
                if (
                    expression_id is None
                    or definition["expected_literal_or_null"] is not None
                ):
                    raise AuthorityError(
                        "derived predicate literal/expression XOR violated"
                    )
            else:
                raise AuthorityError("unknown predicate expected-kind")
        for case in family.get("compatibility_cases", []):
            if (
                case["fixture_constructor_id"]
                not in registries["fixture_constructor_registry"]
            ):
                raise AuthorityError(
                    f"unknown compatibility fixture: {case['fixture_constructor_id']}"
                )
            if case["observer_id"] not in registries["observer_registry"]:
                raise AuthorityError(
                    f"unknown compatibility observer: {case['observer_id']}"
                )
            if case["executor_id"] not in registries["executor_registry"]:
                raise AuthorityError(
                    f"unknown compatibility executor: {case['executor_id']}"
                )
    for row in registries["evidence_input_registry"].values():
        if row["path_expression_id"] not in registries["path_expression_registry"]:
            raise AuthorityError(
                f"unknown path expression in {row['evidence_plan_id']}"
            )
        if row["identity_policy_id"] not in registries["identity_policy_registry"]:
            raise AuthorityError(
                f"unknown identity policy in {row['evidence_plan_id']}"
            )
        if row["required_digest_node_id"] not in digest_ids:
            raise AuthorityError(f"unknown digest node in {row['evidence_plan_id']}")
    for row in registries["type_registry"].values():
        if row["json_shape_id"] not in registries["json_shape_registry"]:
            raise AuthorityError(f"unresolved JSON shape in {row['type_id']}")
        for field in (
            "python_type_predicate_id",
            "wolfram_head_predicate_id",
            "canonicalizer_id",
        ):
            if row[field] not in algorithm_ids:
                raise AuthorityError(
                    f"unresolved algorithm {row[field]} in {row['type_id']}"
                )
        if row["domain_expression_id"] not in expression_ids:
            raise AuthorityError(f"unresolved domain expression in {row['type_id']}")
        if type(row["ordered_mutation_operator_ids"]) is not list or any(
            item not in registries["mutation_operator_registry"]
            for item in row["ordered_mutation_operator_ids"]
        ):
            raise AuthorityError(f"unresolved mutation operator in {row['type_id']}")
    for row in registries["json_shape_registry"].values():
        policy_id = row["number_token_policy_id_or_null"]
        if policy_id is not None and policy_id not in policy_ids:
            raise AuthorityError(
                f"unresolved number-token policy in {row['json_shape_id']}"
            )
    for row in registries["value_schema_registry"].values():
        if row["type_id"] not in registries["type_registry"]:
            raise AuthorityError(f"unresolved type in {row['value_schema_id']}")
        if row["null_rule_id"] not in registries["null_rule_registry"]:
            raise AuthorityError(f"unresolved null rule in {row['value_schema_id']}")
        for optional in ("element_schema_id_or_null",):
            if row[optional] is not None and row[optional] not in value_ids:
                raise AuthorityError(
                    f"unresolved value schema in {row['value_schema_id']}"
                )
        if row["field_schema_ids_or_null"] is not None and any(
            item not in value_ids for item in row["field_schema_ids_or_null"]
        ):
            raise AuthorityError(
                f"unresolved member schema in {row['value_schema_id']}"
            )
    for row in registries["algorithm_registry"].values():
        if any(item not in value_ids for item in row["ordered_input_value_schema_ids"]):
            raise AuthorityError(f"unresolved algorithm input in {row['algorithm_id']}")
        if row["output_value_schema_id"] not in value_ids:
            raise AuthorityError(
                f"unresolved algorithm output in {row['algorithm_id']}"
            )
        if row["null_rule_id"] not in registries["null_rule_registry"]:
            raise AuthorityError(
                f"unresolved algorithm null rule in {row['algorithm_id']}"
            )
        if any(
            item not in reason_ids
            for item in [
                *row["ordered_success_reason_codes"],
                *row["ordered_failure_reason_codes"],
            ]
        ):
            raise AuthorityError(
                f"unresolved algorithm reason in {row['algorithm_id']}"
            )
    for row in registries["policy_registry"].values():
        if any(item not in value_ids for item in row["ordered_input_schema_ids"]):
            raise AuthorityError(f"unresolved policy input in {row['policy_id']}")
        if (
            row["literal_payload_schema_id"] not in value_ids
            or row["output_schema_id"] not in value_ids
        ):
            raise AuthorityError(f"unresolved policy schema in {row['policy_id']}")
        expression = row["decision_expression_id_or_null"]
        if expression is not None and expression not in expression_ids:
            raise AuthorityError(f"unresolved policy expression in {row['policy_id']}")
        if any(item not in reason_ids for item in row["ordered_failure_reason_codes"]):
            raise AuthorityError(f"unresolved policy reason in {row['policy_id']}")
    for row in registries["observer_registry"].values():
        if (
            row["observation_algorithm_id"] not in algorithm_ids
            or row["output_value_schema_id"] not in value_ids
        ):
            raise AuthorityError(
                f"unresolved observer behavior in {row['observer_id']}"
            )
        if any(
            item not in registries["evidence_input_registry"]
            for item in row["ordered_default_evidence_plan_ids"]
        ):
            raise AuthorityError(
                f"unresolved observer evidence in {row['observer_id']}"
            )
    for row in registries["executor_registry"].values():
        for field in (
            "runtime_identity_id",
            "entrypoint_id",
            "argv_template_id",
            "cwd_policy_id",
            "environment_policy_id",
            "callgraph_allowlist_id",
            "stdout_protocol_id",
        ):
            if row[field] not in policy_ids:
                raise AuthorityError(
                    f"unresolved executor policy in {row['executor_id']}.{field}"
                )
    for row in registries["comparison_registry"].values():
        for field in (
            "left_value_schema_id",
            "right_value_schema_id",
            "result_schema_id",
        ):
            if row[field] not in value_ids:
                raise AuthorityError(
                    f"unresolved comparison schema in {row['comparison_id']}"
                )
        if (
            row["operator_id"] not in algorithm_ids
            or row["null_matrix_id"] not in registries["null_matrix_registry"]
        ):
            raise AuthorityError(
                f"unresolved comparison behavior in {row['comparison_id']}"
            )
        if (
            row["tolerance_authority_id_or_null"] is not None
            and row["tolerance_authority_id_or_null"] not in policy_ids
        ):
            raise AuthorityError(
                f"unresolved comparison tolerance in {row['comparison_id']}"
            )
        if any(
            row[field] not in reason_ids
            for field in (
                "pass_reason_code",
                "fail_reason_code",
                "indeterminate_reason_code",
            )
        ):
            raise AuthorityError(
                f"unresolved comparison outcome in {row['comparison_id']}"
            )
    for row in registries["expected_expression_registry"].values():
        if row["result_value_schema_id"] not in value_ids:
            raise AuthorityError(
                f"unresolved expression result in {row['expression_id']}"
            )
        for dependency in row["ordered_dependency_ids"]:
            if (
                dependency not in runtime_inputs
                and dependency not in registries["catalog_registry"]
            ):
                raise AuthorityError(f"unresolved expression dependency {dependency}")
    for row in registries["identity_policy_registry"].values():
        if (
            row["alias_policy_id"] not in policy_ids
            or row["start_end_policy_id"] not in policy_ids
        ):
            raise AuthorityError(
                f"unresolved identity policy in {row['identity_policy_id']}"
            )
    for row in registries["path_expression_registry"].values():
        if (
            row["base_authority_id"] not in policy_ids
            or row["normalization_policy_id"] not in policy_ids
            or row["namespace_regex_id"] not in policy_ids
        ):
            raise AuthorityError(
                f"unresolved path policy in {row['path_expression_id']}"
            )
    for row in registries["fixture_constructor_registry"].values():
        if (
            row["algorithm_id"] not in algorithm_ids
            or row["output_schema_id"] not in value_ids
        ):
            raise AuthorityError(
                f"unresolved fixture behavior in {row['constructor_id']}"
            )
    for row in registries["selector_registry"].values():
        if (
            row["input_catalog_id"] not in registries["catalog_registry"]
            or row["ordered_result_policy_id"] not in policy_ids
            or row["expected_cardinality_expression_id"] not in expression_ids
        ):
            raise AuthorityError(
                f"unresolved selector behavior in {row['selector_id']}"
            )
    for row in registries["catalog_registry"].values():
        if (
            row["row_value_schema_id"] not in value_ids
            or row["expected_row_count_expression_id"] not in expression_ids
            or row["ordered_row_digest_node_id"] not in digest_ids
        ):
            raise AuthorityError(f"unresolved catalog behavior in {row['catalog_id']}")
    for row in registries["mutation_operator_registry"].values():
        if (
            row["parameter_schema_id"] not in value_ids
            or row["exact_transform_algorithm_id"] not in algorithm_ids
            or row["default_reason_code"] not in reason_ids
        ):
            raise AuthorityError(
                f"unresolved mutation behavior in {row['operator_id']}"
            )
        if registries["algorithm_registry"][row["exact_transform_algorithm_id"]][
            "algorithm_kind"
        ] not in {"MUTATION_BYTE_TRANSFORM", "MUTATION_TYPED_ROW_TRANSFORM"}:
            raise AuthorityError(
                f"mutation operator has wrong algorithm kind: {row['operator_id']}"
            )


def _validate_forbidden_semantics(spec: Mapping[str, Any]) -> None:
    text = json.dumps(spec, ensure_ascii=False, sort_keys=True)
    forbidden_patterns = (
        r"\bcallback\b",
        r"\beval\(",
        r"\bexec\(",
        r"\bimportlib\b",
        r"\blatest\b",
        r"current_handoff",
        r"T[047]_current",
        r"\*\*",
    )
    for pattern in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AuthorityError(f"forbidden semantic indirection in spec: {pattern}")


def _registry_evidence_row(row: Mapping[str, Any]) -> list[Any]:
    return [
        row["evidence_plan_id"],
        row["role"],
        row["kind"],
        row["path_expression_id"],
        row["identity_policy_id"],
        row["required_digest_node_id"],
    ]


CALL_PLAN_FIELD_ORDER: Final = {
    "compatibility": (
        "call_kind",
        "call_ordinal",
        "fixture_count",
        "science_calls",
    ),
    "source_load_micro": (
        "call_kind",
        "call_ordinal",
        "anchor_ordinal",
        "kM",
        "ell",
        "parity",
        "node",
        "pre_public_api_exit",
    ),
    "full_sentinel": (
        "call_kind",
        "call_ordinal",
        "anchor_ordinal",
        "kM",
        "ell",
        "parity",
        "node",
    ),
    "official": (
        "call_kind",
        "call_ordinal",
        "anchor_ordinal",
        "kM",
        "ell",
        "parity",
        "node",
    ),
}


def _tag_closed_scalar(value: Any, context: str) -> list[Any]:
    if type(value) is str:
        return S(value)
    if type(value) is int:
        return I(value)
    if type(value) is bool:
        return B(value)
    if value is None:
        return N()
    raise AuthorityError(f"non-scalar value in {context}")


def _tag_call_plan_entry(operation: str, call: Mapping[str, Any]) -> list[Any]:
    expected_fields = CALL_PLAN_FIELD_ORDER[operation]
    _require_exact_keys(call, set(expected_fields), f"{operation} call-plan entry")
    return A(
        f"call-plan-entry-{operation}-v1",
        *(
            A("call-plan-field-v1", S(field), _tag_closed_scalar(call[field], field))
            for field in expected_fields
        ),
    )


def _family_instances(
    family: Mapping[str, Any], stage_ordinal: int
) -> Iterator[dict[str, Any]]:
    mode = family["expansion_mode"]
    if mode == "SIMPLE":
        for definition in family["predicate_definitions"]:
            yield {
                "definition": definition,
                "record_ordinal": None,
                "axes": [["predicate_name", definition["name"]]],
            }
    elif mode == "RECORD_MAJOR":
        for record_ordinal in family["record_ordinals"]:
            for definition in family["predicate_definitions"]:
                yield {
                    "definition": definition,
                    "record_ordinal": record_ordinal,
                    "axes": [
                        ["record_ordinal", record_ordinal],
                        ["predicate_name", definition["name"]],
                    ],
                }
    elif mode == "COMPATIBILITY_CASES":
        for case in family["compatibility_cases"]:
            if case["stage_ordinal"] != stage_ordinal:
                continue
            definition = {
                "name": case["case_id"],
                "field_id": case["subject_predicate_id"],
                "value_type_id": "Z.TYPE.BOOL",
                "nullable": False,
                "null_rule_id": "Z.NULL.NEVER",
                "comparison_id": "Z.CMP.EXACT_BOOL",
                "expected_value_schema_id": "Z.VALUE.BOOL",
                "expected_kind": "LITERAL",
                "expected_literal_or_null": True,
                "expected_expression_id_or_null": None,
                "evidence_plan_ids": ["Z.EVID.COMPAT_FIXTURE"],
            }
            yield {
                "definition": definition,
                "record_ordinal": None,
                "owner": case["owner"],
                "observer_id": case["observer_id"],
                "executor_id": case["executor_id"],
                "axes": [
                    ["case_id", case["case_id"]],
                    ["fixture_constructor_id", case["fixture_constructor_id"]],
                    ["input_fixture_id", case["input_fixture_id"]],
                    ["expected_disposition", case["expected_disposition"]],
                ],
            }
    else:
        raise AuthorityError(f"unknown expansion mode: {mode}")


def expand_predicates(
    spec: Mapping[str, Any], registries: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> tuple[list[list[Any]], dict[str, Any]]:
    stage_ids = {row["stage_ordinal"]: row["stage_id"] for row in spec["stages"]}
    plan_by_operation = {row["operation"]: row for row in spec["call_plans"]}
    families = spec["predicate_families"]
    rows: list[list[Any]] = []
    operation_metrics: dict[str, Any] = {}
    global_ordinal = 0
    seen_ids: set[str] = set()
    for operation in spec["operations"]:
        operation_id = operation["operation"]
        operation_code = operation["operation_code"]
        operation_ordinal = 0
        stage_totals = [0] * 18
        call_metrics: list[dict[str, Any]] = []
        for call in plan_by_operation[operation_id]["calls"]:
            call_ordinal = call["call_ordinal"]
            call_key_digest = derived_hash(
                "call-plan-entry-v1",
                [
                    S(operation_id),
                    I(call_ordinal),
                    _tag_call_plan_entry(operation_id, call),
                ],
            )
            call_start = len(rows)
            for stage_ordinal in range(18):
                stage_instance = 0
                for family in families:
                    if operation_id not in family["operations"]:
                        continue
                    if (
                        family["expansion_mode"] != "COMPATIBILITY_CASES"
                        and family["stage_ordinal"] != stage_ordinal
                    ):
                        continue
                    for instance in _family_instances(family, stage_ordinal):
                        definition = instance["definition"]
                        record_ordinal = instance["record_ordinal"]
                        token = re.sub(
                            r"[^A-Za-z0-9_]+", "_", definition["name"]
                        ).strip("_")
                        if record_ordinal is not None:
                            token = f"R{record_ordinal:02d}.{token}"
                        predicate_id = f"Z.{operation_code}.C{call_ordinal:04d}.P{stage_ordinal:02d}.{token}"
                        if predicate_id in seen_ids:
                            raise AuthorityError(
                                f"predicate ID collision: {predicate_id}"
                            )
                        seen_ids.add(predicate_id)
                        expression_id = definition["expected_expression_id_or_null"]
                        expected_expression = (
                            None
                            if expression_id is None
                            else registries["expected_expression_registry"][
                                expression_id
                            ]["typed_ast"]
                        )
                        evidence = [
                            _registry_evidence_row(
                                registries["evidence_input_registry"][evidence_id]
                            )
                            for evidence_id in definition["evidence_plan_ids"]
                        ]
                        row = [
                            predicate_id,
                            1,
                            operation_id,
                            call_ordinal,
                            call_key_digest,
                            instance["axes"],
                            record_ordinal,
                            stage_ordinal,
                            stage_ids[stage_ordinal],
                            stage_instance,
                            operation_ordinal,
                            global_ordinal,
                            instance.get("owner", family["owner"]),
                            instance.get("observer_id", family["observer_id"]),
                            instance.get("executor_id", family["executor_id"]),
                            definition["field_id"],
                            definition["value_type_id"],
                            definition["nullable"],
                            definition["null_rule_id"],
                            definition["comparison_id"],
                            definition["expected_value_schema_id"],
                            definition["expected_kind"],
                            definition["expected_literal_or_null"],
                            expected_expression,
                            evidence,
                            family["science_capable"],
                        ]
                        if len(row) != len(PREDICATE_ROW_FIELDS):
                            raise AuthorityError(
                                "internal predicate row field-count mismatch"
                            )
                        rows.append(row)
                        stage_instance += 1
                        operation_ordinal += 1
                        global_ordinal += 1
                stage_totals[stage_ordinal] += stage_instance
            call_metrics.append(
                {
                    "call_ordinal": call_ordinal,
                    "call_key_digest": call_key_digest,
                    "first_global_ordinal": rows[call_start][11],
                    "last_global_ordinal": rows[-1][11],
                    "predicate_count": len(rows) - call_start,
                }
            )
        expected_stage = operation["expected_stage_predicate_counts"]
        per_call_stage = [
            value // operation["expected_calls"] for value in stage_totals
        ]
        if per_call_stage != expected_stage:
            raise AuthorityError(
                f"stage cardinality mismatch for {operation_id}: {per_call_stage} != {expected_stage}"
            )
        expected_predicates = operation["expected_predicates"]
        if operation_ordinal != expected_predicates:
            raise AuthorityError(
                f"predicate cardinality mismatch for {operation_id}: {operation_ordinal} != {expected_predicates}"
            )
        operation_metrics[operation_id] = {
            "calls": operation["expected_calls"],
            "predicates": operation_ordinal,
            "child_frames": operation["expected_child_frames"],
            "acks": operation["expected_child_frames"],
            "prefixes": operation_ordinal,
            "stage_finals": 18 * operation["expected_calls"],
            "stage_opens": 17 * operation["expected_calls"],
            "stage0_seeds": operation["expected_calls"],
            "child_exits": operation["expected_calls"],
            "lifecycle_receipts": operation["expected_calls"],
            "p17_closures": operation["expected_calls"],
            "stage_predicate_counts_per_call": expected_stage,
            "calls_inventory": call_metrics,
        }
    if len(rows) != 80_724:
        raise AuthorityError(f"global predicate count mismatch: {len(rows)}")
    return rows, operation_metrics


def _artifact_schema_catalog(spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "phase6_v3_1_z_generated_schema_catalog_v1",
        "gate_id": GATE_ID,
        "predicate_row_fields": list(PREDICATE_ROW_FIELDS),
        "primary_schema_ids": list(PRIMARY_SCHEMA_IDS),
        "nested_and_supporting_schema_ids": list(NESTED_SCHEMA_IDS),
        "artifact_schemas": spec["artifact_schemas"],
        "registries": {
            name: spec[name]
            for name in REGISTRY_ID_FIELDS
            if name not in {"conformance_vector_registry", "mutation_operator_registry"}
        },
        "reference_closure": {
            "all_references_resolved": True,
            "unresolved_reference_count": 0,
            "hidden_callback_count": 0,
            "runtime_semantic_lookup_permitted": False,
        },
    }


def _shard_rows(
    rows: Sequence[Sequence[Any]], collection: str
) -> Iterator[tuple[str, int, int, list[Sequence[Any]]]]:
    for shard_index, first in enumerate(range(0, len(rows), MAX_SHARD_ROWS)):
        last = min(first + MAX_SHARD_ROWS, len(rows)) - 1
        name = (
            f"{collection}/{collection}_{shard_index:04d}_{first:09d}_{last:09d}.jsonl"
        )
        yield name, first, last, list(rows[first : last + 1])


def _jsonl_bytes(rows: Iterable[Sequence[Any]]) -> bytes:
    return b"".join(
        row if type(row) is bytes else compact_array_bytes(row) for row in rows
    )


def _tag_tree(schema_id: str, value: Any) -> list[Any]:
    """Type a closed JSON tree without inferring HASH from lexical content."""
    if value is None:
        return N()
    if type(value) is bool:
        return B(value)
    if type(value) is int:
        return I(value)
    if type(value) is str:
        return S(value)
    if type(value) is list:
        if (
            value
            and type(value[0]) is str
            and value[0] in {"s", "i", "b", "n", "h", "d", "a"}
        ):
            _validate_tagged_value(value, schema_id)
            return list(value)
        return A(
            schema_id, *(_tag_tree(f"{schema_id}-member-v1", item) for item in value)
        )
    if type(value) is dict:
        return A(
            schema_id,
            *(
                A(
                    "named-member-v1",
                    S(key),
                    _tag_tree(f"{schema_id}-{key}-v1", value[key]),
                )
                for key in sorted(value)
            ),
        )
    raise AuthorityError(
        f"unsupported closed tree value in {schema_id}: {type(value).__name__}"
    )


def _predicate_payload_tags(row: Sequence[Any]) -> list[list[Any]]:
    if len(row) != len(PREDICATE_ROW_FIELDS):
        raise AuthorityError("predicate payload field count drift")
    tags: list[list[Any]] = []
    string_fields = {0, 2, 8, 12, 13, 14, 15, 16, 18, 19, 20, 21}
    integer_fields = {1, 3, 7, 9, 10, 11}
    for ordinal, value in enumerate(row):
        if ordinal in string_fields:
            tags.append(S(value))
        elif ordinal in integer_fields:
            tags.append(I(value))
        elif ordinal == 4:
            tags.append(H(value))
        elif ordinal == 5:
            tags.append(_tag_tree("axis-bindings-v1", value))
        elif ordinal == 6:
            tags.append(N() if value is None else I(value))
        elif ordinal in {17, 25}:
            tags.append(B(value))
        elif ordinal in {22, 23}:
            tags.append(N() if value is None else _tag_tree("expected-value-v1", value))
        elif ordinal == 24:
            tags.append(_tag_tree("ordered-evidence-plan-v1", value))
        else:
            raise AuthorityError(f"untyped predicate field ordinal: {ordinal}")
    return tags


def encode_predicate_row(row: Sequence[Any]) -> bytes:
    return enc("predicate-instance-v1", 1, _predicate_payload_tags(row))


def _conformance_payload_tags(row: Sequence[Any]) -> list[list[Any]]:
    if len(row) != len(REGISTRY_ROW_FIELDS["conformance_vector_registry"]):
        raise AuthorityError("conformance vector field count drift")
    return [
        S(row[0]),
        S(row[1]),
        I(row[2]),
        S(row[3]),
        _tag_tree("initial-authority-fixture-ids-v1", row[4]),
        S(row[5]),
        _tag_tree("typed-input-values-v1", row[6]),
        S(row[7]),
        H(row[8]),
        S(row[9]),
        S(row[10]),
        S(row[11]),
        _tag_tree("expected-science-counters-v1", row[12]),
    ]


def encode_conformance_row(row: Sequence[Any]) -> bytes:
    return enc("conformance-vector-v1", 1, _conformance_payload_tags(row))


MUTATION_RECIPE_FIELDS: Final = (
    "mutation_id",
    "target_vector_id",
    "target_schema_or_edge_id",
    "target_field_or_edge",
    "operator_id",
    "mutation_parameters",
    "mutated_bytes_sha256",
    "expected_disposition",
    "reason_code",
    "earliest_rejection_state",
    "rehash_descendants",
)


def encode_mutation_recipe(row: Sequence[Any]) -> bytes:
    if len(row) != len(MUTATION_RECIPE_FIELDS):
        raise AuthorityError("mutation recipe field count drift")
    return enc(
        "mutation-recipe-v1",
        1,
        [
            S(row[0]),
            S(row[1]),
            S(row[2]),
            S(row[3]),
            S(row[4]),
            _tag_tree("mutation-parameters-v1", row[5]),
            H(row[6]),
            S(row[7]),
            S(row[8]),
            S(row[9]),
            B(row[10]),
        ],
    )


def build_conformance_vectors(spec: Mapping[str, Any]) -> list[list[Any]]:
    vectors = spec["conformance_vector_registry"]
    if type(vectors) is not list or not vectors:
        raise AuthorityError("conformance vector registry must be nonempty")
    expected_ids: set[str] = set()
    result: list[list[Any]] = []
    for ordinal, row in enumerate(vectors):
        if type(row) is not list or len(row) != len(
            REGISTRY_ROW_FIELDS["conformance_vector_registry"]
        ):
            raise AuthorityError(f"conformance vector row shape mismatch at {ordinal}")
        if row[2] != ordinal:
            raise AuthorityError(
                f"noncontiguous conformance vector ordinal at {ordinal}"
            )
        if row[0] in expected_ids:
            raise AuthorityError(f"duplicate conformance vector ID: {row[0]}")
        expected_ids.add(row[0])
        try:
            raw = bytes.fromhex(row[7])
        except (TypeError, ValueError) as exc:
            raise AuthorityError(f"invalid literal vector bytes at {ordinal}") from exc
        if sha256_bytes(raw) != row[8]:
            raise AuthorityError(f"literal conformance digest mismatch at {ordinal}")
        if row[9] not in {
            "ACCEPT_AND_ADVANCE",
            "REJECT_BEFORE_STATE_CHANGE",
            "ACCEPT_OBSERVATION_THEN_TERMINAL_FAIL",
        }:
            raise AuthorityError(f"invalid conformance disposition at {ordinal}")
        result.append(list(row))
    plan_ids = [row[0] for row in spec["conformance_vector_plans"]]
    if len(plan_ids) != len(set(plan_ids)) or {row[1] for row in vectors} != set(
        plan_ids
    ):
        raise AuthorityError("conformance vector/plan inventory mismatch")
    return result


SCHEMA_FIELD_OPERATORS: Final = (
    "Z.MUT.DELETE_FIELD_OR_POSITION",
    "Z.MUT.INSERT_UNKNOWN_FIELD_OR_POSITION",
    "Z.MUT.REPLACE_TAG",
    "Z.MUT.REPLACE_VALUE",
    "Z.MUT.TOGGLE_NULL",
    "Z.MUT.REPLACE_ENUM_WITH_LITERAL",
    "Z.MUT.REPLACE_INTEGER_WITH_BOUNDARY",
    "Z.MUT.REPLACE_HASH",
    "Z.MUT.REPLACE_DECIMAL",
    "Z.MUT.SWAP_ADJACENT_POSITIONS",
)
SCHEMA_LEVEL_OPERATORS: Final = (
    "Z.MUT.DUPLICATE_JSON_MEMBER",
    "Z.MUT.DELETE_ROW",
    "Z.MUT.DUPLICATE_ROW",
    "Z.MUT.MOVE_ROW",
    "Z.MUT.TRUNCATE_BYTES",
    "Z.MUT.APPEND_BYTES",
    "Z.MUT.APPEND_EXTRA_LF",
    "Z.MUT.PAD_TO_OVERSIZE",
)
PREDICATE_MUTATION_FIELDS: Final = PREDICATE_ROW_FIELDS
EDGE_OPERATORS: Final = (
    "Z.MUT.DELETE_ROW",
    "Z.MUT.DUPLICATE_ROW",
    "Z.MUT.MOVE_ROW",
    "Z.MUT.REPLACE_EDGE_SOURCE",
    "Z.MUT.REPLAY_FROM_SESSION",
    "Z.MUT.RECOMPUTE_DECLARED_DESCENDANT_HASHES",
)
CRASH_BOUNDARIES: Final = (
    "FRAME_RECEIVE",
    "EVENT_WRITE",
    "EVENT_FSYNC",
    "PREFIX_WRITE",
    "PREFIX_FSYNC",
    "FINAL_WRITE",
    "FINAL_FSYNC",
    "OPEN_WRITE",
    "OPEN_FSYNC",
    "ACK_FILE_WRITE",
    "ACK_FILE_FSYNC",
    "ACK_SEND",
    "CHILD_EXIT_AUTHORITY",
    "CHILD_EOF",
    "LIFECYCLE_RECEIPT",
    "OPEN17",
    "P17_EVENT_0",
    "P17_EVENT_1",
    "P17_EVENT_2",
    "P17_EVENT_3",
    "P17_EVENT_4",
    "P17_EVENT_5",
    "P17_EVENT_6",
    "P17_EVENT_7",
    "P17_CLOSURE",
    "TERMINAL_MANIFEST",
    "TERMINAL_CHECKPOINT",
    "CALL_DIRECTORY_SEAL",
    "OPERATION_MANIFEST",
    "ROOT_CHECKPOINT",
)
FILESYSTEM_ATTACKS: Final = (
    "SYMLINK",
    "HARDLINK",
    "ALIAS",
    "WRONG_MODE",
    "WRONG_NLINK",
    "WRONG_INODE",
    "UNKNOWN_PATH",
    "POST_CLOSE_WRITE",
    "SAME_BYTES_NEW_INODE",
    "TORN_FILE",
)


def _mutate_array_bytes(
    source_raw: bytes, operator_id: str, position: int | None
) -> bytes:
    try:
        value = json.loads(source_raw)
    except json.JSONDecodeError as exc:
        raise AuthorityError("mutation source is not JSON") from exc
    if type(value) is not list:
        raise AuthorityError("mutation source is not an ordered array")
    index = 2 if position is None else position
    if operator_id == "Z.MUT.DELETE_FIELD_OR_POSITION":
        if not value:
            raise AuthorityError("cannot delete from empty mutation source")
        del value[min(index, len(value) - 1)]
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.INSERT_UNKNOWN_FIELD_OR_POSITION":
        value.insert(min(index, len(value)), ["s", "__unknown_member__"])
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.DUPLICATE_JSON_MEMBER":
        return b'{"duplicate":1,"duplicate":2}\n'
    if operator_id in {
        "Z.MUT.REPLACE_TAG",
        "Z.MUT.REPLACE_VALUE",
        "Z.MUT.TOGGLE_NULL",
        "Z.MUT.REPLACE_ENUM_WITH_LITERAL",
        "Z.MUT.REPLACE_INTEGER_WITH_BOUNDARY",
        "Z.MUT.REPLACE_HASH",
        "Z.MUT.REPLACE_DECIMAL",
    }:
        slot = min(index, len(value) - 1)
        current = value[slot]
        if operator_id == "Z.MUT.REPLACE_TAG":
            value[slot] = ["x", "invalid-tag"]
        elif operator_id == "Z.MUT.REPLACE_VALUE":
            value[slot] = ["s", "__mutated_value__"]
        elif operator_id == "Z.MUT.TOGGLE_NULL":
            value[slot] = ["s", "nonnull"] if current == ["n"] else ["n"]
        elif operator_id == "Z.MUT.REPLACE_ENUM_WITH_LITERAL":
            value[slot] = ["s", "__OUT_OF_ENUM__"]
        elif operator_id == "Z.MUT.REPLACE_INTEGER_WITH_BOUNDARY":
            value[slot] = ["i", "-1"]
        elif operator_id == "Z.MUT.REPLACE_HASH":
            value[slot] = ["h", "A" * 64]
        else:
            value[slot] = ["d", "NaN"]
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.SWAP_ADJACENT_POSITIONS":
        if len(value) < 2:
            raise AuthorityError("cannot swap a one-field mutation source")
        left = min(index, len(value) - 2)
        if value[left] == value[left + 1]:
            candidates = [
                ordinal
                for ordinal in range(2, len(value) - 1)
                if value[ordinal] != value[ordinal + 1]
            ]
            if not candidates:
                raise AuthorityError("no unequal adjacent positions are available")
            left = candidates[0]
        value[left], value[left + 1] = value[left + 1], value[left]
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.DELETE_ROW":
        del value[min(index, len(value) - 1)]
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.DUPLICATE_ROW":
        value.insert(min(index + 1, len(value)), value[min(index, len(value) - 1)])
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.MOVE_ROW":
        item = value.pop(min(index, len(value) - 1))
        value.insert(0 if index else len(value), item)
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.TRUNCATE_BYTES":
        return source_raw[:-1]
    if operator_id == "Z.MUT.APPEND_BYTES":
        return source_raw + b"X"
    if operator_id == "Z.MUT.APPEND_EXTRA_LF":
        return source_raw + b"\n"
    if operator_id == "Z.MUT.PAD_TO_OVERSIZE":
        return source_raw + b" " * max(1, 1_048_577 - len(source_raw))
    if operator_id == "Z.MUT.REPLACE_EDGE_SOURCE":
        value[2 if len(value) > 2 else 0] = ["s", "__wrong_edge_source__"]
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.REPLAY_FROM_SESSION":
        value.append(["h", "f" * 64])
        return compact_array_bytes(value)
    if operator_id == "Z.MUT.RECOMPUTE_DECLARED_DESCENDANT_HASHES":
        base = compact_array_bytes([*value, ["s", "__base_mutation__"]])
        return enc(
            "descendant-rehash-attack-v1",
            1,
            [H(sha256_bytes(base)), H(sha256_bytes(source_raw)), B(True)],
        )
    raise AuthorityError(f"unimplemented mutation operator: {operator_id}")


def _schema_bootstrap_vectors(spec: Mapping[str, Any]) -> dict[str, tuple[str, bytes]]:
    result: dict[str, tuple[str, bytes]] = {}
    for row in spec["conformance_vector_registry"]:
        if row[3] != "SCHEMA_BOOTSTRAP":
            continue
        result[row[5]] = (row[0], bytes.fromhex(row[7]))
    expected = {row["schema_id"] for row in spec["artifact_schemas"]}
    if set(result) != expected:
        raise AuthorityError("schema bootstrap vector inventory mismatch")
    return result


def _predicate_field_operator(field_name: str) -> str:
    if field_name == "call_key_digest":
        return "Z.MUT.REPLACE_HASH"
    if field_name in {
        "predicate_row_revision",
        "call_ordinal",
        "stage_ordinal",
        "stage_instance_ordinal",
        "operation_instance_ordinal",
        "global_instance_ordinal",
    }:
        return "Z.MUT.REPLACE_INTEGER_WITH_BOUNDARY"
    if field_name in {
        "record_ordinal_or_null",
        "expected_literal_or_null",
        "expected_expression_or_null",
    }:
        return "Z.MUT.TOGGLE_NULL"
    return "Z.MUT.REPLACE_VALUE"


MutationObligation = tuple[str, str, int, str, str, str, list[Any], str, bool, bytes]


def _coverage_obligations(
    spec: Mapping[str, Any],
    predicates: Sequence[Sequence[Any]],
    digest_edges: Sequence[tuple[str, str]],
) -> Iterator[MutationObligation]:
    """Yield the independently derived denominator without materializing it."""

    bootstraps = _schema_bootstrap_vectors(spec)
    for schema_ordinal, schema in enumerate(spec["artifact_schemas"]):
        vector_id, source = bootstraps[schema["schema_id"]]
        for field_ordinal, field in enumerate(schema["fields"]):
            for operator_id in SCHEMA_FIELD_OPERATORS:
                coverage_id = (
                    f"Z.COVERAGE.SCHEMA.{schema_ordinal:04d}.FIELD."
                    f"{field_ordinal:04d}.{operator_id}"
                )
                yield (
                    coverage_id,
                    "SCHEMA_FIELD",
                    schema_ordinal,
                    vector_id,
                    f"{schema['schema_id']}:{field[0]}",
                    operator_id,
                    [field_ordinal + 2],
                    "SCHEMA_DECODE",
                    False,
                    source,
                )
        for operator_id in SCHEMA_LEVEL_OPERATORS:
            coverage_id = f"Z.COVERAGE.SCHEMA.{schema_ordinal:04d}.LEVEL.{operator_id}"
            yield (
                coverage_id,
                "SCHEMA_LEVEL",
                schema_ordinal,
                vector_id,
                schema["schema_id"],
                operator_id,
                [],
                "SCHEMA_DECODE",
                False,
                source,
            )
    for predicate_ordinal, row in enumerate(predicates):
        if len(row) != len(PREDICATE_ROW_FIELDS):
            raise AuthorityError(
                f"predicate mutation width drift at {predicate_ordinal}"
            )
        source = encode_predicate_row(row)
        for field_index, field_name in enumerate(PREDICATE_MUTATION_FIELDS):
            operator_id = _predicate_field_operator(field_name)
            coverage_id = (
                f"Z.COVERAGE.PREDICATE.{predicate_ordinal:09d}."
                f"{field_index:02d}.{field_name}"
            )
            yield (
                coverage_id,
                "PREDICATE_FIELD",
                predicate_ordinal,
                row[0],
                field_name,
                operator_id,
                [field_index + 2],
                "PREDICATE_BIND",
                False,
                source,
            )
    for edge_ordinal, edge in enumerate(digest_edges):
        source = enc("digest-edge-v1", 1, [S(edge[0]), S(edge[1])])
        for operator_id in EDGE_OPERATORS:
            coverage_id = f"Z.COVERAGE.DIGEST_EDGE.{edge_ordinal:06d}.{operator_id}"
            yield (
                coverage_id,
                "DIGEST_EDGE",
                edge_ordinal,
                "Z.VECTOR.CHAIN.00",
                f"{edge[0]}->{edge[1]}",
                operator_id,
                [2],
                "DIGEST_DAG",
                operator_id == "Z.MUT.RECOMPUTE_DECLARED_DESCENDANT_HASHES",
                source,
            )
    for target_kind, rows, earliest in (
        ("FSM_EDGE", spec["state_machine"], "FSM_TRANSITION"),
        ("PATH_RULE", spec["path_grammar"], "PATH_ADMISSION"),
    ):
        for row_ordinal, row in enumerate(rows):
            source = enc(
                f"{target_kind.lower()}-v1",
                1,
                [_tag_tree(f"{target_kind.lower()}-row-v1", row)],
            )
            for operator_id in EDGE_OPERATORS:
                coverage_id = (
                    f"Z.COVERAGE.{target_kind}.{row_ordinal:06d}.{operator_id}"
                )
                yield (
                    coverage_id,
                    target_kind,
                    row_ordinal,
                    "Z.VECTOR.CHAIN.01",
                    row[0] if type(row) is list else str(row_ordinal),
                    operator_id,
                    [2],
                    earliest,
                    operator_id == "Z.MUT.RECOMPUTE_DECLARED_DESCENDANT_HASHES",
                    source,
                )
    for boundary_ordinal, boundary in enumerate(CRASH_BOUNDARIES):
        source = enc("crash-boundary-v1", 1, [S(boundary), S("UNMUTATED")])
        for side in ("BEFORE", "AFTER"):
            coverage_id = f"Z.COVERAGE.CRASH.{boundary_ordinal:03d}.{side}"
            yield (
                coverage_id,
                "CRASH_BOUNDARY",
                boundary_ordinal,
                "Z.VECTOR.CHAIN.02",
                boundary,
                "Z.MUT.REPLACE_VALUE",
                [3, side],
                "FAILURE_TERMINALIZATION",
                True,
                source,
            )
    for attack_ordinal, attack in enumerate(FILESYSTEM_ATTACKS):
        source = enc(
            "filesystem-identity-v1",
            1,
            [S("regular"), I(0o444), I(1), H("0" * 64)],
        )
        coverage_id = f"Z.COVERAGE.FILESYSTEM.{attack_ordinal:03d}.{attack}"
        yield (
            coverage_id,
            "FILESYSTEM",
            attack_ordinal,
            "Z.VECTOR.CHAIN.03",
            attack,
            "Z.MUT.REPLACE_VALUE",
            [2, attack],
            "FILESYSTEM_ADMISSION",
            True,
            source,
        )


def _mutation_obligation_count(
    spec: Mapping[str, Any],
    predicates: Sequence[Sequence[Any]],
    digest_edges: Sequence[tuple[str, str]],
) -> int:
    schema_count = sum(
        len(schema["fields"]) * len(SCHEMA_FIELD_OPERATORS)
        + len(SCHEMA_LEVEL_OPERATORS)
        for schema in spec["artifact_schemas"]
    )
    return (
        schema_count
        + len(predicates) * len(PREDICATE_ROW_FIELDS)
        + len(digest_edges) * len(EDGE_OPERATORS)
        + (len(spec["state_machine"]) + len(spec["path_grammar"])) * len(EDGE_OPERATORS)
        + len(CRASH_BOUNDARIES) * 2
        + len(FILESYSTEM_ATTACKS)
    )


def _iter_mutation_recipes(
    spec: Mapping[str, Any],
    predicates: Sequence[Sequence[Any]],
    digest_edges: Sequence[tuple[str, str]],
) -> Iterator[tuple[str, list[Any]]]:
    operators = {
        row[0]: dict(
            zip(REGISTRY_ROW_FIELDS["mutation_operator_registry"], row, strict=True)
        )
        for row in spec["mutation_operator_registry"]
    }
    for coverage_ordinal, obligation in enumerate(
        _coverage_obligations(spec, predicates, digest_edges)
    ):
        (
            coverage_id,
            target_kind,
            target_ordinal,
            target_vector_id,
            target_field_or_edge,
            operator_id,
            parameters,
            earliest_state,
            rehash_descendants,
            source_raw,
        ) = obligation
        if operator_id not in operators:
            raise AuthorityError(
                f"coverage obligation uses undeclared operator {operator_id}"
            )
        position = parameters[0] if parameters and type(parameters[0]) is int else None
        if target_kind == "CRASH_BOUNDARY":
            mutated_raw = enc(
                "crash-boundary-v1",
                1,
                [S(target_field_or_edge), S(parameters[1])],
            )
        elif target_kind == "FILESYSTEM":
            mutated_raw = enc(
                "filesystem-identity-attack-v1",
                1,
                [S(target_field_or_edge), H(sha256_bytes(source_raw))],
            )
        else:
            mutated_raw = _mutate_array_bytes(source_raw, operator_id, position)
        if mutated_raw == source_raw:
            raise AuthorityError(f"no-op mutation for {coverage_id}")
        operator = operators[operator_id]
        recipe = [
            f"Z.MUTATION.{coverage_ordinal:09d}",
            target_vector_id,
            f"{target_kind}:{target_ordinal:09d}",
            target_field_or_edge,
            operator_id,
            parameters,
            sha256_bytes(mutated_raw),
            operator["default_disposition"],
            operator["default_reason_code"],
            operator["earliest_rejection_state"],
            rehash_descendants,
        ]
        yield coverage_id, recipe


class _StreamingDerivedHash:
    """Incrementally reproduce DER over one canonical tagged JSON array."""

    def __init__(self, label: str) -> None:
        if type(label) is not str or re.fullmatch(r"[A-Za-z0-9_.-]+", label) is None:
            raise AuthorityError("streaming DER label is not a closed ASCII literal")
        self._digest = hashlib.sha256()
        self._digest.update(b"SCHWO-V31Z\0DERIVED\0" + label.encode("ascii") + b"\0[")
        self._first = True
        self._finished = False

    def add(self, value: Sequence[Any]) -> None:
        if self._finished:
            raise AuthorityError("streaming DER already finalized")
        tagged = list(value)
        _validate_tagged_value(tagged, "streaming DER item")
        if not self._first:
            self._digest.update(b",")
        self._digest.update(
            json.dumps(
                tagged,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        self._first = False

    def finish(self) -> str:
        if self._finished:
            raise AuthorityError("streaming DER finalized twice")
        self._digest.update(b"]\n")
        self._finished = True
        return self._digest.hexdigest()


def _assert_streaming_derived_hash_equivalence() -> None:
    items = [S("codec"), H("a" * 64), I(1), B(True), N(), D("1.0e+0")]
    streaming = _StreamingDerivedHash("streaming-der-kat-v1")
    for item in items:
        streaming.add(item)
    if streaming.finish() != derived_hash("streaming-der-kat-v1", items):
        raise AuthorityError("streaming DER differs from canonical DER")


def _stream_mutation_recipe_shards(
    spec: Mapping[str, Any],
    predicates: Sequence[Sequence[Any]],
    digest_edges: Sequence[tuple[str, str]],
    shard_sink: Callable[[str, bytes], None],
) -> tuple[list[list[Any]], dict[str, Any], int]:
    _assert_streaming_derived_hash_equivalence()
    universe_digest = _StreamingDerivedHash("coverage-universe-v1")
    recipe_digest = _StreamingDerivedHash("ordered-mutation-recipes-v1")
    shards: list[list[Any]] = []
    buffer = bytearray()
    shard_first = 0
    count = 0
    first_id: str | None = None
    last_id: str | None = None

    def flush() -> None:
        nonlocal buffer, shard_first
        if not buffer:
            return
        last = count - 1
        shard_index = len(shards)
        rel = (
            f"mutation_oracle/mutation_oracle_{shard_index:04d}_"
            f"{shard_first:09d}_{last:09d}.jsonl"
        )
        raw = bytes(buffer)
        shard_sink(rel, raw)
        shards.append(
            [rel, shard_first, last, last - shard_first + 1, sha256_bytes(raw)]
        )
        buffer = bytearray()
        shard_first = count

    for coverage_id, recipe in _iter_mutation_recipes(spec, predicates, digest_edges):
        if recipe[0] != f"Z.MUTATION.{count:09d}":
            raise AuthorityError(f"mutation recipe ordinal drift at {count}")
        if first_id is None:
            first_id = coverage_id
        last_id = coverage_id
        universe_digest.add(S(coverage_id))
        recipe_raw = encode_mutation_recipe(recipe)
        recipe_digest.add(H(sha256_bytes(recipe_raw)))
        buffer.extend(recipe_raw)
        count += 1
        if count - shard_first == MAX_SHARD_ROWS:
            flush()
    flush()

    expected_count = _mutation_obligation_count(spec, predicates, digest_edges)
    if count != expected_count or first_id is None or last_id is None:
        raise AuthorityError(
            f"streamed mutation cardinality mismatch: {count} != {expected_count}"
        )
    index = {
        "schema": "phase6_v3_1_z_mutation_expansion_index_v1",
        "gate_id": GATE_ID,
        "sampling": False,
        "coverage_obligation_count": count,
        "covered_unique_count": count,
        "missing_count": 0,
        "extra_count": 0,
        "recipe_count": count,
        "coverage_universe_sha256": universe_digest.finish(),
        "ordered_recipe_sha256": recipe_digest.finish(),
        "coverage_first_id": first_id,
        "coverage_last_id": last_id,
        "coverage_ordinals_contiguous": True,
        "coverage_source": (
            "INDEPENDENT_SCHEMA_ALL26_PREDICATE_DAG_FSM_PATH_"
            "LIFECYCLE_TERMINAL_EXPANSION"
        ),
        "shards": shards,
    }
    return shards, index, count


def _generated_python_validator(
    spec_sha: str, generator_sha: str, catalog_sha: str
) -> bytes:
    template = r'''# Generated by phase6_v3_1_z_generate_machine_authority.py; do not edit.
"""Source-distinct, zero-science GMA-Z1 tagged-wire validator."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

SPEC_SHA256 = __SPEC_SHA256__
GENERATOR_SHA256 = __GENERATOR_SHA256__
SCHEMA_CATALOG_SHA256 = __CATALOG_SHA256__
PREDICATE_ROW_FIELD_COUNT = 26
CONFORMANCE_ROW_FIELD_COUNT = 13
MUTATION_ROW_FIELD_COUNT = 11
SCHEMA_FIELD_COUNTS = {
    "child_observation_frame": 26,
    "parent_event": 31,
    "prefix_checkpoint": 19,
    "final_stage_checkpoint": 24,
    "ack": 21,
    "stage_open_authority": 29,
    "stage0_seed": 27,
    "child_exit_authority": 18,
    "lifecycle_receipt": 43,
    "p17_closure": 21,
    "terminal_manifest": 40,
    "operation_terminal_manifest": 32,
    "root_terminal_checkpoint": 16,
    "FileIdentity": 11,
    "DirectoryIdentity": 10,
    "RootIdentity": 11,
    "StreamIdentity": 9,
    "ProcessClosure": 16,
    "CallDirectorySealCloseout": 14,
    "WriterHeldClosure": 11,
    "WriterReleaseCloseout": 16,
    "ResolvedEvidence": 10,
    "ScienceCounters": 17,
    "FailureClosure": 17,
    "DispatchConsumption": 18,
    "RunContract": 14,
    "SourceLedger": 13,
    "FailureTerminationAuthority": 10,
    "PreRootControlFailure": 23,
    "TerminalCheckpoint": 9,
}
if len(SCHEMA_FIELD_COUNTS) != 30:
    raise RuntimeError("generated schema cardinality drift")

_INTEGER_RE = re.compile(r"0|-?[1-9][0-9]*")
_HASH_RE = re.compile(r"[0-9a-f]{64}")
_DECIMAL_RE = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?e[+-](?:0|[1-9][0-9]*)"
)


class ValidationError(ValueError):
    """Fail-closed wire/schema violation."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValidationError(f"duplicate JSON member: {key}")
        out[key] = value
    return out


def _bare_number(_token: str) -> Any:
    raise ValidationError("bare JSON number is forbidden in a tagged record")


def S(value: str) -> list[Any]:
    if type(value) is not str:
        raise ValidationError("S requires a string")
    return ["s", value]


def I(value: int) -> list[Any]:  # noqa: E743 - tagged-integer constructor
    if type(value) is not int:
        raise ValidationError("I requires a plain integer")
    return ["i", str(value)]


def B(value: bool) -> list[Any]:
    if type(value) is not bool:
        raise ValidationError("B requires a boolean")
    return ["b", value]


def N() -> list[Any]:
    return ["n"]


def H(value: str) -> list[Any]:
    if type(value) is not str or _HASH_RE.fullmatch(value) is None:
        raise ValidationError("H requires 64 lowercase hexadecimal characters")
    return ["h", value]


def D(value: str) -> list[Any]:
    if (
        type(value) is not str
        or _DECIMAL_RE.fullmatch(value) is None
        or value.startswith("-0")
    ):
        raise ValidationError("D requires a canonical decimal string")
    return ["d", value]


def A(schema_id: str, *members: list[Any]) -> list[Any]:
    if type(schema_id) is not str or not schema_id:
        raise ValidationError("A requires a nonempty schema identifier")
    for member in members:
        validate_tagged_value(member)
    return ["a", schema_id, *members]


def validate_tagged_value(value: Any) -> None:
    if type(value) is not list or not value or type(value[0]) is not str:
        raise ValidationError("value is not explicitly tagged")
    tag = value[0]
    if tag == "s":
        if len(value) != 2 or type(value[1]) is not str:
            raise ValidationError("invalid S value")
        return
    if tag == "i":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or _INTEGER_RE.fullmatch(value[1]) is None
        ):
            raise ValidationError("invalid I value")
        return
    if tag == "b":
        if len(value) != 2 or type(value[1]) is not bool:
            raise ValidationError("invalid B value")
        return
    if tag == "n":
        if value != ["n"]:
            raise ValidationError("invalid N value")
        return
    if tag == "h":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or _HASH_RE.fullmatch(value[1]) is None
        ):
            raise ValidationError("invalid H value")
        return
    if tag == "d":
        if (
            len(value) != 2
            or type(value[1]) is not str
            or _DECIMAL_RE.fullmatch(value[1]) is None
            or value[1].startswith("-0")
        ):
            raise ValidationError("invalid D value")
        return
    if tag == "a":
        if len(value) < 2 or type(value[1]) is not str or not value[1]:
            raise ValidationError("invalid A header")
        for member in value[2:]:
            validate_tagged_value(member)
        return
    raise ValidationError(f"unknown tagged-value discriminator: {tag!r}")


def canonical_array_bytes(value: list[Any]) -> bytes:
    if type(value) is not list:
        raise ValidationError("canonical wire value must be an array")
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def tagged_array_bytes(values: list[list[Any]]) -> bytes:
    if type(values) is not list:
        raise ValidationError("tagged payload must be an ordered array")
    for value in values:
        validate_tagged_value(value)
    return canonical_array_bytes(values)


def enc(schema_id: str, revision: int, payload: list[list[Any]]) -> bytes:
    if type(schema_id) is not str or not schema_id or type(revision) is not int:
        raise ValidationError("invalid ENC header")
    return tagged_array_bytes([S(schema_id), I(revision), *payload])


def artifact_hash(
    schema_id: str,
    revision: int,
    payload: list[list[Any]],
) -> str:
    prefix = b"SCHWO-V31Z\0ARTIFACT\0" + schema_id.encode("ascii") + b"\0"
    return hashlib.sha256(prefix + enc(schema_id, revision, payload)).hexdigest()


def derived_hash(label: str, items: list[list[Any]]) -> str:
    if type(label) is not str or re.fullmatch(r"[A-Za-z0-9_.-]+", label) is None:
        raise ValidationError("invalid DER label")
    prefix = b"SCHWO-V31Z\0DERIVED\0" + label.encode("ascii") + b"\0"
    return hashlib.sha256(prefix + tagged_array_bytes(items)).hexdigest()


def strict_decode_line(raw: bytes) -> list[Any]:
    if type(raw) is not bytes or not raw or not raw.endswith(b"\n"):
        raise ValidationError("record requires exactly one terminal LF")
    if b"\n" in raw[:-1] or b"\r" in raw:
        raise ValidationError("record contains an embedded or noncanonical line ending")
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_pairs,
            parse_int=_bare_number,
            parse_float=_bare_number,
            parse_constant=_bare_number,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationError(f"invalid tagged JSON record: {exc}") from exc
    if type(value) is not list or canonical_array_bytes(value) != raw:
        raise ValidationError("record is not one canonical ordered array")
    for member in value:
        validate_tagged_value(member)
    return value


def strict_decode_jsonl(raw: bytes) -> list[list[Any]]:
    if type(raw) is not bytes or not raw or not raw.endswith(b"\n"):
        raise ValidationError("JSONL requires a nonempty LF-terminated stream")
    lines = raw.splitlines(keepends=True)
    if not lines or any(line == b"\n" or not line.endswith(b"\n") for line in lines):
        raise ValidationError("JSONL contains an empty or torn record")
    return [strict_decode_line(line) for line in lines]


def validate_record(value: Any, schema_id: str, field_count: int) -> None:
    if (
        type(value) is not list
        or len(value) != field_count + 2
        or value[:2] != [S(schema_id), I(1)]
    ):
        raise ValidationError(
            f"{schema_id} requires exactly {field_count} ordered fields"
        )
    for member in value[2:]:
        validate_tagged_value(member)


def validate_artifact_line(raw: bytes) -> list[Any]:
    value = strict_decode_line(raw)
    if len(value) < 2 or value[0][0:1] != ["s"]:
        raise ValidationError("artifact schema tag is absent")
    schema_id = value[0][1]
    if schema_id not in SCHEMA_FIELD_COUNTS:
        raise ValidationError(f"unknown generated artifact schema: {schema_id}")
    validate_record(value, schema_id, SCHEMA_FIELD_COUNTS[schema_id])
    return value


def validate_predicate_line(raw: bytes) -> list[Any]:
    value = strict_decode_line(raw)
    validate_record(value, "predicate-instance-v1", PREDICATE_ROW_FIELD_COUNT)
    payload = value[2:]
    for position in (1, 3, 7, 9, 10, 11):
        if payload[position][0] != "i":
            raise ValidationError("predicate ordinal/revision is not I-tagged")
    for position in (17, 25):
        if payload[position][0] != "b":
            raise ValidationError("predicate flag is not B-tagged")
    kind = payload[21]
    if kind not in (S("LITERAL"), S("DERIVED")):
        raise ValidationError("predicate value source is invalid")
    literal_is_null = payload[22] == N()
    expression_is_null = payload[23] == N()
    if kind == S("LITERAL"):
        if literal_is_null or not expression_is_null:
            raise ValidationError("literal/expression XOR violation")
    elif not literal_is_null or expression_is_null:
        raise ValidationError("literal/expression XOR violation")
    return value


def validate_conformance_line(raw: bytes) -> list[Any]:
    value = strict_decode_line(raw)
    validate_record(value, "conformance-vector-v1", CONFORMANCE_ROW_FIELD_COUNT)
    return value


def validate_mutation_line(raw: bytes) -> list[Any]:
    value = strict_decode_line(raw)
    validate_record(value, "mutation-recipe-v1", MUTATION_ROW_FIELD_COUNT)
    return value


def _codec_self_test() -> bool:
    s64 = S("a" * 64)
    h64 = H("a" * 64)
    if s64 == h64 or tagged_array_bytes([s64]) == tagged_array_bytes([h64]):
        raise RuntimeError("S64/H64 tag separation failed")
    if I(1) == B(True) or N() != ["n"] or D("1.250e-3") != ["d", "1.250e-3"]:
        raise RuntimeError("scalar codec separation failed")
    payload = [s64, h64, I(1), B(True), N(), D("1.250e-3")]
    expected_enc = (
        b'[["s","codec-kat-record-v1"],["i","1"],'
        b'["s","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],'
        b'["h","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],'
        b'["i","1"],["b",true],["n"],["d","1.250e-3"]]\n'
    )
    if enc("codec-kat-record-v1", 1, payload) != expected_enc:
        raise RuntimeError("ENC known-answer mismatch")
    if artifact_hash("codec-kat-record-v1", 1, payload) != (
        "133bb6414dbde7a83b21611471e8a4cfdf4928bec9a840518ac149995d2557e0"
    ):
        raise RuntimeError("ART known-answer mismatch")
    if derived_hash("codec-kat-v1", payload) != (
        "a6615e407c818a5773a4c3d5afd82cd4caffc5d77ea467e43ec0d66707d0d27c"
    ):
        raise RuntimeError("DER known-answer mismatch")
    for invalid in (
        ["i", "01"],
        ["i", 1],
        ["b", 1],
        ["n", None],
        ["h", "A" * 64],
        ["d", "NaN"],
        ["d", "-0e+0"],
    ):
        try:
            validate_tagged_value(invalid)
        except ValidationError:
            continue
        raise RuntimeError(f"invalid tagged KAT accepted: {invalid!r}")
    return True


CODEC_KAT_OK = _codec_self_test()
'''
    source = (
        template.replace("__SPEC_SHA256__", repr(spec_sha))
        .replace("__GENERATOR_SHA256__", repr(generator_sha))
        .replace("__CATALOG_SHA256__", repr(catalog_sha))
    )
    return source.encode("utf-8")


def _generated_wolfram_validator(
    spec_sha: str, generator_sha: str, catalog_sha: str
) -> bytes:
    template = r"""(* Generated source-distinct, zero-science GMA-Z1 tagged-wire validator. *)
ZSpecSHA256 = "__SPEC_SHA256__";
ZGeneratorSHA256 = "__GENERATOR_SHA256__";
ZSchemaCatalogSHA256 = "__CATALOG_SHA256__";
ZPredicateRowFieldCount = 26;
ZConformanceRowFieldCount = 13;
ZMutationRowFieldCount = 11;
ZSchemaFieldCounts = <|
  "child_observation_frame" -> 26, "parent_event" -> 31,
  "prefix_checkpoint" -> 19, "final_stage_checkpoint" -> 24,
  "ack" -> 21, "stage_open_authority" -> 29, "stage0_seed" -> 27,
  "child_exit_authority" -> 18, "lifecycle_receipt" -> 43,
  "p17_closure" -> 21, "terminal_manifest" -> 40,
  "operation_terminal_manifest" -> 32, "root_terminal_checkpoint" -> 16,
  "FileIdentity" -> 11, "DirectoryIdentity" -> 10,
  "RootIdentity" -> 11, "StreamIdentity" -> 9, "ProcessClosure" -> 16,
  "CallDirectorySealCloseout" -> 14, "WriterHeldClosure" -> 11,
  "WriterReleaseCloseout" -> 16, "ResolvedEvidence" -> 10,
  "ScienceCounters" -> 17, "FailureClosure" -> 17,
  "DispatchConsumption" -> 18, "RunContract" -> 14,
  "SourceLedger" -> 13, "FailureTerminationAuthority" -> 10,
  "PreRootControlFailure" -> 23, "TerminalCheckpoint" -> 9
|>;
If[Length[ZSchemaFieldCounts] =!= 30, ZSchemaFieldCounts = $Failed];

ZCanonicalIntegerStringQ[value_] := TrueQ[
  StringQ[value] && StringMatchQ[value, RegularExpression["0|-?[1-9][0-9]*"]]
];
ZCanonicalHashStringQ[value_] := TrueQ[
  StringQ[value] && StringMatchQ[value, RegularExpression["[0-9a-f]{64}"]]
];
ZCanonicalDecimalStringQ[value_] := TrueQ[
  StringQ[value] &&
  StringMatchQ[value, RegularExpression["-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?e[+-](?:0|[1-9][0-9]*)"]] &&
  !StringStartsQ[value, "-0"]
];

ZS[value_] /; StringQ[value] := {"s", value};
ZS[___] := $Failed;
ZI[value_] /; IntegerQ[value] := {"i", ToString[value, InputForm]};
ZI[___] := $Failed;
ZB[value_] /; BooleanQ[value] := {"b", value};
ZB[___] := $Failed;
ZN[] := {"n"};
ZH[value_] /; ZCanonicalHashStringQ[value] := {"h", value};
ZH[___] := $Failed;
ZD[value_] /; ZCanonicalDecimalStringQ[value] := {"d", value};
ZD[___] := $Failed;
ZA[schema_String, members___] /; And @@ (ZTaggedValueQ /@ {members}) :=
  Join[{"a", schema}, {members}];
ZA[___] := $Failed;

ZTaggedValueQ[value_] := Which[
  MatchQ[value, {"s", _String}], True,
  MatchQ[value, {"i", _String}], ZCanonicalIntegerStringQ[value[[2]]],
  MatchQ[value, {"b", True | False}], True,
  SameQ[value, {"n"}], True,
  MatchQ[value, {"h", _String}], ZCanonicalHashStringQ[value[[2]]],
  MatchQ[value, {"d", _String}], ZCanonicalDecimalStringQ[value[[2]]],
  ListQ[value] && Length[value] >= 2 && value[[1]] === "a" && StringQ[value[[2]]],
    And @@ (ZTaggedValueQ /@ Drop[value, 2]),
  True, False
];

ZCanonicalArrayString[value_List] :=
  ExportString[value, "RawJSON", "Compact" -> True] <> "\n";
ZCanonicalArrayBytes[value_List] :=
  ByteArray[ToCharacterCode[ZCanonicalArrayString[value], "UTF-8"]];
ZTaggedArrayBytes[values_List] /; And @@ (ZTaggedValueQ /@ values) :=
  ZCanonicalArrayBytes[values];
ZTaggedArrayBytes[___] := $Failed;
ZEnc[schema_String, revision_Integer, payload_List] /;
    And @@ (ZTaggedValueQ /@ payload) :=
  ZTaggedArrayBytes[Join[{ZS[schema], ZI[revision]}, payload]];
ZEnc[___] := $Failed;

ZArtifactHash[schema_String, revision_Integer, payload_List] := Module[
  {encoded = ZEnc[schema, revision, payload], prefix},
  If[encoded === $Failed, Return[$Failed]];
  prefix = Join[
    ToCharacterCode["SCHWO-V31Z", "UTF-8"], {0},
    ToCharacterCode["ARTIFACT", "UTF-8"], {0},
    ToCharacterCode[schema, "ASCII"], {0}
  ];
  Hash[ByteArray[Join[prefix, Normal[encoded]]], "SHA256", "HexString"]
];
ZDerivedHash[label_String, items_List] /;
    StringMatchQ[label, RegularExpression["[A-Za-z0-9_.-]+"]] := Module[
  {encoded = ZTaggedArrayBytes[items], prefix},
  If[encoded === $Failed, Return[$Failed]];
  prefix = Join[
    ToCharacterCode["SCHWO-V31Z", "UTF-8"], {0},
    ToCharacterCode["DERIVED", "UTF-8"], {0},
    ToCharacterCode[label, "ASCII"], {0}
  ];
  Hash[ByteArray[Join[prefix, Normal[encoded]]], "SHA256", "HexString"]
];
ZDerivedHash[___] := $Failed;

ZStrictRawJSONLine[raw_List] := Module[{text, value},
  If[
    raw === {} || Last[raw] =!= 10 || Count[raw, 10] =!= 1 ||
    MemberQ[raw, 13] || !And @@ (IntegerQ[#] && 0 <= # <= 255 & /@ raw),
    Return[$Failed]
  ];
  text = Quiet[Check[FromCharacterCode[raw, "UTF-8"], $Failed]];
  If[text === $Failed, Return[$Failed]];
  value = Quiet[Check[ImportString[text, "RawJSON"], $Failed]];
  If[value === $Failed || !ListQ[value], Return[$Failed]];
  If[ZCanonicalArrayBytes[value] =!= ByteArray[raw], Return[$Failed]];
  value
];
ZStrictRawJSONLine[___] := $Failed;
ZStrictJSONL[raw_List] := Module[{ends, starts, lines, values},
  If[raw === {} || Last[raw] =!= 10, Return[$Failed]];
  ends = Flatten[Position[raw, 10]];
  If[ends === {} || Last[ends] =!= Length[raw], Return[$Failed]];
  starts = Prepend[Most[ends] + 1, 1];
  lines = MapThread[Take[raw, {#1, #2}] &, {starts, ends}];
  If[AnyTrue[lines, Length[#] <= 1 &], Return[$Failed]];
  values = ZStrictRawJSONLine /@ lines;
  If[MemberQ[values, $Failed], $Failed, values]
];
ZStrictJSONL[___] := $Failed;

ZValidateRecord[value_, schema_String, count_Integer] := TrueQ[
  ListQ[value] && Length[value] === count + 2 &&
  Take[value, 2] === {ZS[schema], ZI[1]} &&
  And @@ (ZTaggedValueQ /@ Drop[value, 2])
];
ZValidateArtifactRecord[value_] := Module[{schema},
  If[!ListQ[value] || Length[value] < 2 || !MatchQ[value[[1]], {"s", _String}],
    Return[False]
  ];
  schema = value[[1, 2]];
  If[!KeyExistsQ[ZSchemaFieldCounts, schema], Return[False]];
  ZValidateRecord[value, schema, ZSchemaFieldCounts[schema]]
];
ZValidatePredicateRecord[value_] := Module[
  {payload, kind, literalIsNull, expressionIsNull},
  If[!ZValidateRecord[value, "predicate-instance-v1", ZPredicateRowFieldCount],
    Return[False]
  ];
  payload = Drop[value, 2];
  If[!And @@ (#[[1]] === "i" & /@ payload[[{2, 4, 8, 10, 11, 12}]]),
    Return[False]
  ];
  If[!And @@ (#[[1]] === "b" & /@ payload[[{18, 26}]]), Return[False]];
  kind = payload[[22]];
  If[!MemberQ[{ZS["LITERAL"], ZS["DERIVED"]}, kind], Return[False]];
  literalIsNull = payload[[23]] === ZN[];
  expressionIsNull = payload[[24]] === ZN[];
  If[kind === ZS["LITERAL"],
    TrueQ[!literalIsNull && expressionIsNull],
    TrueQ[literalIsNull && !expressionIsNull]
  ]
];
ZValidateConformanceRecord[value_] :=
  ZValidateRecord[value, "conformance-vector-v1", ZConformanceRowFieldCount];
ZValidateMutationRecord[value_] :=
  ZValidateRecord[value, "mutation-recipe-v1", ZMutationRowFieldCount];

ZCodecKATPayload = {
  ZS[StringRepeat["a", 64]], ZH[StringRepeat["a", 64]], ZI[1], ZB[True],
  ZN[], ZD["1.250e-3"]
};
ZCodecKATEncoded = ByteArray[ToCharacterCode[
  "[[\"s\",\"codec-kat-record-v1\"],[\"i\",\"1\"],[\"s\",\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"],[\"h\",\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"],[\"i\",\"1\"],[\"b\",true],[\"n\"],[\"d\",\"1.250e-3\"]]\n",
  "UTF-8"
]];
ZCodecKATQ = TrueQ[
  ZS[StringRepeat["a", 64]] =!= ZH[StringRepeat["a", 64]] &&
  ZTaggedArrayBytes[{ZS[StringRepeat["a", 64]]}] =!=
    ZTaggedArrayBytes[{ZH[StringRepeat["a", 64]]}] &&
  ZI[1] =!= ZB[True] && ZN[] === {"n"} &&
  ZD["1.250e-3"] === {"d", "1.250e-3"} &&
  ZEnc["codec-kat-record-v1", 1, ZCodecKATPayload] === ZCodecKATEncoded &&
  ZArtifactHash["codec-kat-record-v1", 1, ZCodecKATPayload] ===
    "133bb6414dbde7a83b21611471e8a4cfdf4928bec9a840518ac149995d2557e0" &&
  ZDerivedHash["codec-kat-v1", ZCodecKATPayload] ===
    "a6615e407c818a5773a4c3d5afd82cd4caffc5d77ea467e43ec0d66707d0d27c" &&
  !ZTaggedValueQ[{"i", "01"}] && !ZTaggedValueQ[{"i", 1}] &&
  !ZTaggedValueQ[{"b", 1}] && !ZTaggedValueQ[{"n", Null}] &&
  !ZTaggedValueQ[{"h", StringRepeat["A", 64]}] &&
  !ZTaggedValueQ[{"d", "NaN"}] && !ZTaggedValueQ[{"d", "-0e+0"}]
];
"""
    source = (
        template.replace("__SPEC_SHA256__", spec_sha)
        .replace("__GENERATOR_SHA256__", generator_sha)
        .replace("__CATALOG_SHA256__", catalog_sha)
    )
    return source.encode("utf-8")


def _compatibility_observer_plan(spec: Mapping[str, Any]) -> list[list[Any]]:
    """Return the exact input-only 118-case plan embedded in the observer.

    Expected values, comparison rules, dispositions, and rejection authorities
    deliberately remain parent-only and never enter the generated child source.
    """

    fixture_by_id = {
        row[0]: dict(
            zip(REGISTRY_ROW_FIELDS["fixture_constructor_registry"], row, strict=True)
        )
        for row in spec["fixture_constructor_registry"]
    }
    cases: list[Mapping[str, Any]] = []
    for family in spec["predicate_families"]:
        cases.extend(family.get("compatibility_cases", []))
    if len(cases) != 118:
        raise AuthorityError("compatibility observer requires exactly 118 fixtures")
    plan: list[list[Any]] = []
    stage_counts: dict[int, int] = {}
    for ordinal, case in enumerate(cases):
        constructor_id = f"Z.FIXTURE.COMPAT.{ordinal:03d}"
        constructor = fixture_by_id.get(constructor_id)
        if constructor is None or case["fixture_constructor_id"] != constructor_id:
            raise AuthorityError(f"compatibility observer fixture drift at {ordinal}")
        payload = constructor["literal_parameters"]
        mapped = dict(zip(COMPATIBILITY_FIXTURE_PAYLOAD_FIELDS, payload, strict=True))
        stage = case["stage_ordinal"]
        child = case["owner"] == "CHILD_OBSERVED_PARENT_VERIFIED"
        if child != (2 <= stage <= 7):
            raise AuthorityError(f"compatibility observer ownership drift at {ordinal}")
        raw = _decode_literal_hex(mapped["raw_input_hex"], constructor_id)
        if sha256_bytes(raw) != mapped["raw_input_sha256"]:
            raise AuthorityError(
                f"compatibility observer raw digest drift at {ordinal}"
            )
        plan.append(
            [
                ordinal,
                case["case_id"],
                constructor_id,
                case["subject_predicate_id"],
                stage,
                "CHILD" if child else "PARENT",
                mapped["operation_id"],
                mapped["raw_input_hex"],
                mapped["raw_input_sha256"],
            ]
        )
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    if stage_counts != {
        2: 9,
        3: 5,
        4: 6,
        5: 17,
        6: 10,
        7: 8,
        8: 11,
        9: 11,
        10: 7,
        11: 6,
        12: 4,
        13: 8,
        14: 16,
    }:
        raise AuthorityError("compatibility observer stage cardinality drift")
    if sum(row[5] == "CHILD" for row in plan) != 55:
        raise AuthorityError("compatibility observer child cardinality drift")
    if sum(row[5] == "PARENT" for row in plan) != 63:
        raise AuthorityError("compatibility observer parent cardinality drift")
    return plan


def _generated_compatibility_observer(
    spec: Mapping[str, Any], spec_sha: str, generator_sha: str
) -> bytes:
    plan_raw = compact_array_bytes(_compatibility_observer_plan(spec))
    plan_sha = sha256_bytes(plan_raw)
    template = r"""#!/usr/bin/env wolframscript
(* Generated structural RawJSON observer; zero-science and observation-only. *)
ZSpecSHA256 = "__SPEC_SHA256__";
ZGeneratorSHA256 = "__GENERATOR_SHA256__";
ZFixturePlanSHA256 = "__FIXTURE_PLAN_SHA256__";
ZFixturePlanHex = "__FIXTURE_PLAN_HEX__";
ZCallCount = 1;
ZPredicateCount = 151;
ZFrameCount = 82;

ZHexBytes[value_String] :=
  FromDigits[StringJoin[#], 16] & /@ Partition[Characters[value], 2];
ZByteHash[bytes_List] :=
  Hash[ByteArray[bytes], "SHA256", "HexString"];
ZJSONBytes[value_] :=
  ToCharacterCode[ExportString[value, "RawJSON", "Compact" -> True] <> "\n", "UTF-8"];
ZDecode[bytes_List] := Quiet[Check[ImportByteArray[ByteArray[bytes], "RawJSON"], $Failed]];
ZHeadName[value_] := ToString[Head[value], InputForm];

ZPlanRaw = ZHexBytes[ZFixturePlanHex];
If[ZByteHash[ZPlanRaw] =!= ZFixturePlanSHA256, Exit[63]];
ZPlan = ZDecode[ZPlanRaw];
If[ZPlan === $Failed || !ListQ[ZPlan] || Length[ZPlan] =!= 118, Exit[63]];
ZChildPlan = Select[ZPlan, #[[6]] === "CHILD" &];
ZParentPlan = Select[ZPlan, #[[6]] === "PARENT" &];
If[Length[ZChildPlan] =!= 55 || Length[ZParentPlan] =!= 63, Exit[63]];

ZEnvelope[fixture_List, bytes_List] := Module[{value = ZDecode[bytes]},
  If[
    value === $Failed || !ListQ[value] || Length[value] =!= 6 ||
    value[[1]] =!= "compatibility-operation-input-v1" || value[[2]] =!= 1 ||
    value[[3]] =!= fixture[[7]] || value[[4]] =!= fixture[[2]],
    $Failed,
    value[[6]]
  ]
];

ZObserveRaw[bytes_List] := Module[{value = ZDecode[bytes], canonical},
  If[value === $Failed, Return[{"RAW_DECODE", False, Null, False, bytes}]];
  canonical = ZJSONBytes[value];
  {"RAW_DECODE", True, ZHeadName[value], SameQ[canonical, bytes], value, bytes}
];

ZObserveProjection[fixture_List, bytes_List] := Module[
  {value = ZDecode[bytes], keys, records, projections, contexts},
  keys = {"context", "mode", "nlink", "path", "sha256", "size"};
  If[value === $Failed || !ListQ[value], Return[{"PROJECTION_INPUT", False, bytes}]];
  records = value;
  projections = Map[
    If[AssociationQ[#], Lookup[#, keys, Missing["FIELD"]], Missing["RECORD"]] &,
    records
  ];
  contexts = If[And @@ (AssociationQ /@ records), Lookup[records, "context", Missing["FIELD"]], {}];
  {
    "NAMED_PROJECTION", projections,
    And @@ (AssociationQ[#] && Sort[Keys[#]] === Sort[keys] & /@ records),
    DuplicateFreeQ[contexts], OrderedQ[contexts],
    ZByteHash[ZJSONBytes[projections]]
  }
];

ZObserveRelation[fixture_List, bytes_List] := Module[{args = ZEnvelope[fixture, bytes]},
  If[args === $Failed || !ListQ[args] || Length[args] =!= 2,
    Return[{"RELATION_INPUT", False, bytes}]
  ];
  If[MatchQ[args[[1]], {"held-symbol", _String}],
    {"EXACT_RELATION", "SYMBOLIC", ZHeadName[args[[1]]], ZHeadName[args[[2]]]},
    {"EXACT_RELATION", "CONCRETE", SameQ[args[[1]], args[[2]]],
      ZHeadName[args[[1]]], ZHeadName[args[[2]]]}
  ]
];

ZASCIIPathFacts[value_] := {
  StringQ[value],
  StringQ[value] && StringMatchQ[value, RegularExpression["[A-Za-z0-9_./-]+"]],
  StringQ[value] && !StringStartsQ[value, "/"] && !StringEndsQ[value, "/"],
  StringQ[value] && !StringContainsQ[value, "//"],
  StringQ[value] && FreeQ[StringSplit[value, "/"], "." | ".."],
  If[StringQ[value], ToCharacterCode[value, "UTF-8"], {}]
};

ZObserveUnicode[fixture_List, bytes_List] := Module[{args = ZEnvelope[fixture, bytes], mode},
  If[args === $Failed || !ListQ[args] || Length[args] =!= 2,
    Return[{"UNICODE_INPUT", False, bytes}]
  ];
  mode = args[[2]];
  Which[
    MemberQ[{"NFC", "NFD"}, mode],
      {"UNICODE_NORMALIZE", CharacterNormalize[args[[1]], mode],
        ToCharacterCode[args[[1]], "UTF-8"]},
    mode === "ASCII_PATH", {"UNICODE_ASCII_PATH", ZASCIIPathFacts[args[[1]]]},
    mode === "SYMBOL_OWNVALUE_DIAGNOSTIC",
      {"SYMBOL_DIAGNOSTIC", NameQ["System`" <> args[[1]]]},
    True,
      {"UNICODE_RAW_RELATION", SameQ[args[[1]], args[[2]]],
        ToCharacterCode[args[[1]], "UTF-8"],
        ToCharacterCode[args[[2]], "UTF-8"]}
  ]
];

ZObservePath[fixture_List, bytes_List] := Module[{args = ZEnvelope[fixture, bytes]},
  If[args === $Failed || !ListQ[args] || Length[args] < 1,
    Return[{"PATH_INPUT", False, bytes}]
  ];
  {"ASCII_PATH", ZASCIIPathFacts[args[[1]]],
    If[Length[args] === 2, StringMatchQ[args[[1]], RegularExpression[args[[2]]]], Null]}
];

ZObserveRegex[fixture_List, bytes_List] := Module[{args = ZEnvelope[fixture, bytes]},
  If[args === $Failed || !ListQ[args] || Length[args] =!= 2,
    Return[{"REGEX_INPUT", False, bytes}]
  ];
  If[args[[1]] === "counter",
    {"REGEX_COUNTER", args[[2]], ZHeadName[args[[2]]]},
    {"REGEX_DIAGNOSTIC", args[[1]], StringMatchQ[args[[2]], RegularExpression[args[[1]]]]}
  ]
];

ZObserveHash[fixture_List, bytes_List] := Module[{args = ZEnvelope[fixture, bytes], item, fileBytes},
  If[args === $Failed || !ListQ[args] || Length[args] =!= 1,
    Return[{"HASH_INPUT", False, bytes}]
  ];
  item = args[[1]];
  If[ListQ[item] && Length[item] === 2,
    fileBytes = ZHexBytes[item[[1]]];
    {"FILE_HASH_SIZE", ZByteHash[fileBytes], Length[fileBytes], item[[2]]},
    {"LOWER_HEX64", StringQ[item], If[StringQ[item], StringLength[item], Null],
      StringQ[item] && StringMatchQ[item, RegularExpression["[0-9a-f]{64}"]], item}
  ]
];

ZObserveInteger[fixture_List, bytes_List] := Module[{args = ZEnvelope[fixture, bytes]},
  If[args === $Failed || !ListQ[args], Return[{"INTEGER_INPUT", False, bytes}]];
  If[Length[args] === 1, Return[{"INTEGER_MISSING", args}]];
  {"EXACT_INTEGER_DOMAIN", args[[1]], ZHeadName[args[[2]]],
    IntegerQ[args[[2]]], TrueQ[IntegerQ[args[[2]]] && args[[2]] >= 0], args[[2]]}
];

ZObserveFixture[fixture_List] := Module[
  {bytes = ZHexBytes[fixture[[8]]], operation = fixture[[7]]},
  If[ZByteHash[bytes] =!= fixture[[9]], Return[{"RAW_IDENTITY_DRIFT", fixture[[1]]}]];
  Switch[operation,
    "Z.OP.RAWJSON_DECODE_V1", ZObserveRaw[bytes],
    "Z.OP.NAMED_SIX_FIELD_PROJECTION_V1", ZObserveProjection[fixture, bytes],
    "Z.OP.EXACT_RELATION_V1", ZObserveRelation[fixture, bytes],
    "Z.OP.UNICODE_NORMALIZE_V1", ZObserveUnicode[fixture, bytes],
    "Z.OP.ASCII_PATH_GRAMMAR_V1", ZObservePath[fixture, bytes],
    "Z.OP.REGEX_DIAGNOSTIC_V1", ZObserveRegex[fixture, bytes],
    "Z.OP.LOWER_HEX64_SHAPE_V1", ZObserveHash[fixture, bytes],
    "Z.OP.EXACT_INTEGER_DOMAIN_V1", ZObserveInteger[fixture, bytes],
    _, {"UNDECLARED_CHILD_OPERATION", operation}
  ]
];

If[Length[$ScriptCommandLine] =!= 2, Exit[64]];
ZRequestPath = $ScriptCommandLine[[2]];
If[!StringQ[ZRequestPath] || !FileExistsQ[ZRequestPath], Exit[65]];
ZRequestRaw = Quiet[Check[BinaryReadList[ZRequestPath, "Byte"], $Failed]];
If[
  ZRequestRaw === $Failed || ZRequestRaw === {} || Last[ZRequestRaw] =!= 10 ||
  Count[ZRequestRaw, 10] =!= 1 || MemberQ[ZRequestRaw, 13],
  Exit[66]
];
ZRequest = ZDecode[ZRequestRaw];
If[ZRequest === $Failed || ZJSONBytes[ZRequest] =!= ZRequestRaw, Exit[67]];
If[
  !ListQ[ZRequest] || Length[ZRequest] =!= 9 ||
  ZRequest[[1]] =!= "phase6_v3_1_z_compatibility_observer_request_v1" ||
  ZRequest[[2]] =!= ZSpecSHA256 || ZRequest[[3]] =!= ZGeneratorSHA256 ||
  !StringQ[ZRequest[[4]]] || ZRequest[[5]] =!= ZFixturePlanSHA256 ||
  ZRequest[[6]] =!= ZCallCount || ZRequest[[7]] =!= ZPredicateCount ||
  ZRequest[[8]] =!= ZFrameCount || ZRequest[[9]] =!= ConstantArray[0, 17],
  Exit[68]
];
ZSession = ZRequest[[4]];

ZRuntimeFrames = {
  {1, 0, {"RUNTIME_PATH", First[$CommandLine]}},
  {1, 1, {"RUNTIME_PATH_HASH", If[FileExistsQ[First[$CommandLine]], FileHash[First[$CommandLine], "SHA256", "HexString"], Null]}},
  {1, 2, {"RUNTIME_VERSION", $Version}},
  {1, 3, {"SCRIPT_PATH", $InputFileName}},
  {1, 4, {"SCRIPT_HASH", If[FileExistsQ[$InputFileName], FileHash[$InputFileName, "SHA256", "HexString"], Null]}},
  {1, 5, {"ARGV", $ScriptCommandLine}},
  {1, 6, {"CWD", Directory[]}},
  {1, 7, {"ENVIRONMENT_NAMES", Sort[Environment[]]}},
  {1, 8, {"SESSION", ZSession}}
};
ZFixtureFrames = Map[{#[[5]], #[[1]], ZObserveFixture[#]} &, ZChildPlan];
ZBarrierFrames = Table[
  ZStageRows = Select[ZParentPlan, #[[5]] === ZStage &];
  {ZStage, ZStage, {"PARENT_BARRIER", Length[ZStageRows], ZStageRows}},
  {ZStage, 8, 14}
];
ZCounterFrames = Table[{15, ZOrdinal, {"COUNTER", ZOrdinal, If[ZOrdinal === 0, 1, 0]}}, {ZOrdinal, 0, 6}];
ZStructuralFrames = {
  {16, 0, {"STRUCTURE", "FIXTURES", Length[ZPlan]}},
  {16, 1, {"STRUCTURE", "CHILD_FIXTURES", Length[ZChildPlan]}},
  {16, 2, {"STRUCTURE", "PARENT_FIXTURES", Length[ZParentPlan]}},
  {16, 3, {"STRUCTURE", "FRAMES", ZFrameCount}}
};
ZFrames = Join[ZRuntimeFrames, ZFixtureFrames, ZBarrierFrames, ZCounterFrames, ZStructuralFrames];
If[Length[ZFrames] =!= ZFrameCount, Exit[69]];

ZPreviousDigest = Null;
ZOrderedDigests = {};
Do[
  ZObserved = ZFrames[[ZSequence + 1]];
  ZFrame = {
    "phase6_v3_1_z_compatibility_observation_frame_v1",
    ZSpecSHA256, ZGeneratorSHA256, ZSession, ZSequence,
    ZObserved[[1]], ZObserved[[2]], ZObserved[[3]], ZPreviousDigest
  };
  ZFrameRaw = ZJSONBytes[ZFrame];
  ZFrameDigest = ZByteHash[ZFrameRaw];
  AppendTo[ZOrderedDigests, ZFrameDigest];
  WriteString[$Output, FromCharacterCode[ZFrameRaw, "UTF-8"]];
  Flush[$Output];
  ZAckLine = Quiet[Check[ReadLine[$Input], $Failed]];
  If[ZAckLine === $Failed || !StringQ[ZAckLine], Exit[70]];
  ZAck = Quiet[Check[ImportString[ZAckLine, "RawJSON"], $Failed]];
  If[
    ZAck === $Failed || ZAck =!= {
      "phase6_v3_1_z_compatibility_observation_ack_v1",
      ZSession, ZSequence, ZFrameDigest
    },
    Exit[71]
  ];
  ZPreviousDigest = ZFrameDigest,
  {ZSequence, 0, ZFrameCount - 1}
];
ZTerminal = {
  "phase6_v3_1_z_compatibility_terminal_observation_v1",
  ZSpecSHA256, ZGeneratorSHA256, ZSession, ZCallCount,
  ZPredicateCount, ZFrameCount, ZByteHash[ZJSONBytes[ZOrderedDigests]],
  ConstantArray[0, 17]
};
WriteString[$Output, FromCharacterCode[ZJSONBytes[ZTerminal], "UTF-8"]];
Flush[$Output];
Exit[0];
"""
    source = (
        template.replace("__SPEC_SHA256__", spec_sha)
        .replace("__GENERATOR_SHA256__", generator_sha)
        .replace("__FIXTURE_PLAN_SHA256__", plan_sha)
        .replace("__FIXTURE_PLAN_HEX__", plan_raw.hex())
    )
    forbidden = (
        "expected",
        "comparison",
        "pass",
        "bhpt",
        "paclet",
        "reggewheeler",
        "findfile",
        "needs[",
        "get[",
    )
    lowered = source.lower()
    if any(token in lowered for token in forbidden):
        raise AuthorityError("compatibility observer contains a forbidden role token")
    return source.encode("utf-8")


def _exclusive_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _portable_dir_rows(paths: Sequence[str]) -> list[list[Any]]:
    """Return tagged directory rows in declaration/preorder, never FS order."""
    children: dict[str, list[str]] = {".": []}
    directory_order = ["."]

    def add_child(parent: str, child: str) -> None:
        if child not in children[parent]:
            children[parent].append(child)

    for rel in paths:
        pure = PurePosixPath(rel)
        parent = "."
        for part in pure.parts[:-1]:
            current = part if parent == "." else f"{parent}/{part}"
            add_child(parent, part)
            if current not in children:
                children[current] = []
                directory_order.append(current)
            parent = current
        add_child(parent, pure.name)
    return [
        A(
            "generated-directory-row-v1",
            S(directory),
            I(0o555),
            I(len(children[directory]) + 2),
            H(
                derived_hash(
                    "ordered-child-names-v1", [S(name) for name in children[directory]]
                )
            ),
        )
        for directory in directory_order
    ]


def _freeze_tree(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink():
            raise AuthorityError(f"symlink in generated tree: {path}")
        if path.is_file():
            os.chmod(path, 0o444)
        elif path.is_dir():
            os.chmod(path, 0o555)
    os.chmod(root, 0o555)


def generate(spec_path: Path, output_root: Path) -> dict[str, Any]:
    start = time.perf_counter()
    if output_root.exists() or output_root.is_symlink():
        raise AuthorityError(f"output root must be absent: {output_root}")
    if not output_root.is_absolute():
        raise AuthorityError("output root must be absolute")
    spec, registries = validate_spec(spec_path)
    repo_root = Path(__file__).resolve(strict=True).parents[1]
    _validate_future_absence(spec, repo_root)
    input_ledger_start = _immutable_input_ledger(spec, repo_root)
    output_root.mkdir(parents=True, mode=0o700)
    spec_sha = sha256_file(spec_path)
    generator_path = Path(__file__).resolve(strict=True)
    generator_sha = sha256_file(generator_path)
    predicates, operation_metrics = expand_predicates(spec, registries)
    digest_order, digest_edges = _topological_digest_nodes(spec["digest_nodes"])

    files: dict[str, tuple[bytes, str]] = {}
    schema_catalog = _artifact_schema_catalog(spec)
    files["schema_catalog.json"] = (
        enc(
            "generated-schema-catalog-v1",
            1,
            [H(spec_sha), _tag_tree("schema-catalog-payload-v1", schema_catalog)],
        ),
        "SCHEMA_CATALOG",
    )
    digest_catalog = {
        "schema": "phase6_v3_1_z_digest_dag_v1",
        "gate_id": GATE_ID,
        "nodes": spec["digest_nodes"],
        "topological_order": digest_order,
        "edges": [list(edge) for edge in digest_edges],
        "acyclic": True,
    }
    files["digest_dag.json"] = (
        enc(
            "generated-digest-dag-v1",
            1,
            [H(spec_sha), _tag_tree("digest-dag-payload-v1", digest_catalog)],
        ),
        "DIGEST_DAG",
    )
    operation_dags = {
        "schema": "phase6_v3_1_z_operation_dags_v1",
        "gate_id": GATE_ID,
        "operations": operation_metrics,
        "call_plans": spec["call_plans"],
        "state_machine": spec["state_machine"],
        "science_graph": spec["immutable_inputs"]["science_graph"],
        "global_counts": {
            "calls": 198,
            "predicates": 80_724,
            "events": 80_724,
            "prefixes": 80_724,
            "child_frames": 51_893,
            "acks": 51_893,
            "stage_finals": 3_564,
            "stage_opens": 3_366,
            "stage0_seeds": 198,
            "child_exits": 198,
            "lifecycle_receipts": 198,
            "p17_closures": 198,
        },
    }
    files["operation_dags.json"] = (
        enc(
            "generated-operation-dags-v1",
            1,
            [H(spec_sha), _tag_tree("operation-dags-payload-v1", operation_dags)],
        ),
        "OPERATION_DAGS",
    )
    files["path_grammar.json"] = (
        enc(
            "generated-path-grammar-v1",
            1,
            [
                H(spec_sha),
                _tag_tree("path-grammar-rules-v1", spec["path_grammar"]),
            ],
        ),
        "PATH_GRAMMAR",
    )
    files["authority_progression.json"] = (
        enc(
            "generated-authority-progression-v1",
            1,
            [
                H(spec_sha),
                _tag_tree(
                    "authority-progression-payload-v1", spec["authority_progression"]
                ),
            ],
        ),
        "AUTHORITY_PROGRESSION",
    )
    resource_projection = _resource_projection(spec)
    files["resource_projection.json"] = (
        enc(
            "generated-resource-projection-v1",
            1,
            [
                H(spec_sha),
                _tag_tree("resource-projection-payload-v1", resource_projection),
            ],
        ),
        "RESOURCE_PROJECTION",
    )

    predicate_shards: list[list[Any]] = []
    for path, first, last, shard_rows in _shard_rows(predicates, "predicate_instances"):
        raw = _jsonl_bytes(encode_predicate_row(row) for row in shard_rows)
        files[path] = (raw, "PREDICATE_SHARD")
        predicate_shards.append([path, first, last, len(shard_rows), sha256_bytes(raw)])

    vectors = build_conformance_vectors(spec)
    conformance_shards: list[list[Any]] = []
    for path, first, last, shard_rows in _shard_rows(vectors, "conformance_vectors"):
        raw = _jsonl_bytes(encode_conformance_row(row) for row in shard_rows)
        files[path] = (raw, "CONFORMANCE_SHARD")
        conformance_shards.append(
            [path, first, last, len(shard_rows), sha256_bytes(raw)]
        )
    conformance_index = {
        "schema": "phase6_v3_1_z_conformance_expansion_index_v1",
        "gate_id": GATE_ID,
        "vector_count": len(vectors),
        "ordered_vector_sha256": derived_hash(
            "ordered-conformance-vectors-v1",
            [H(sha256_bytes(encode_conformance_row(row))) for row in vectors],
        ),
        "shards": conformance_shards,
    }
    files["conformance_vectors/conformance_expansion_index.json"] = (
        enc(
            "generated-conformance-expansion-index-v1",
            1,
            [H(spec_sha), _tag_tree("conformance-index-payload-v1", conformance_index)],
        ),
        "CONFORMANCE_INDEX",
    )

    streamed_files: dict[str, tuple[int, str, str]] = {}

    def write_mutation_shard(rel: str, raw: bytes) -> None:
        if rel in files or rel in streamed_files:
            raise AuthorityError(f"streamed mutation path collision: {rel}")
        _exclusive_write(output_root / rel, raw)
        streamed_files[rel] = (len(raw), sha256_bytes(raw), "MUTATION_SHARD")

    mutation_shards, mutation_index, mutation_recipe_count = (
        _stream_mutation_recipe_shards(
            spec, predicates, digest_edges, write_mutation_shard
        )
    )
    files["mutation_oracle/mutation_expansion_index.json"] = (
        enc(
            "generated-mutation-expansion-index-v1",
            1,
            [H(spec_sha), _tag_tree("mutation-index-payload-v1", mutation_index)],
        ),
        "MUTATION_INDEX",
    )

    catalog_sha = sha256_bytes(files["schema_catalog.json"][0])
    files["validator_python.py"] = (
        _generated_python_validator(spec_sha, generator_sha, catalog_sha),
        "PYTHON_VALIDATOR",
    )
    files["validator_wolfram.wl"] = (
        _generated_wolfram_validator(spec_sha, generator_sha, catalog_sha),
        "WOLFRAM_VALIDATOR",
    )
    files["compatibility_observer.wls"] = (
        _generated_compatibility_observer(spec, spec_sha, generator_sha),
        "ZERO_SCIENCE_COMPATIBILITY_OBSERVER",
    )
    shard_inventory = {
        "schema": "phase6_v3_1_z_shard_inventory_v1",
        "gate_id": GATE_ID,
        "max_rows_per_shard": MAX_SHARD_ROWS,
        "predicate_shards": predicate_shards,
        "conformance_shards": conformance_shards,
        "mutation_shards": mutation_shards,
        "counts": {
            "predicates": len(predicates),
            "conformance_vectors": len(vectors),
            "mutation_recipes": mutation_recipe_count,
            "coverage_obligations": mutation_index["coverage_obligation_count"],
        },
    }
    files["shard_inventory.json"] = (
        enc(
            "generated-shard-inventory-v1",
            1,
            [H(spec_sha), _tag_tree("shard-inventory-payload-v1", shard_inventory)],
        ),
        "SHARD_INVENTORY",
    )

    preferred = spec["generated_output_plan"]["base_leaf_paths"]
    base_set = set(preferred)
    if base_set - set(files):
        raise AuthorityError(
            f"generated base leaf paths missing: {sorted(base_set - set(files))}"
        )
    ordered_paths = list(preferred)
    ordered_paths.extend(row[0] for row in predicate_shards)
    ordered_paths.extend(row[0] for row in conformance_shards)
    ordered_paths.append("conformance_vectors/conformance_expansion_index.json")
    ordered_paths.extend(row[0] for row in mutation_shards)
    ordered_paths.append("mutation_oracle/mutation_expansion_index.json")
    if set(ordered_paths) != set(files) | set(streamed_files):
        raise AuthorityError(
            "generated leaf ordering is incomplete or contains a collision"
        )

    for rel in ordered_paths:
        if rel in files:
            _exclusive_write(output_root / rel, files[rel][0])
    leaf_rows: list[list[Any]] = []
    role_by_path: dict[str, str] = {}
    for rel in ordered_paths:
        if rel in files:
            raw, role = files[rel]
            size = len(raw)
            digest = sha256_bytes(raw)
        else:
            size, digest, role = streamed_files[rel]
        role_by_path[rel] = role
        leaf_rows.append(
            A(
                "generated-leaf-row-v1",
                S(rel),
                I(size),
                I(0o444),
                I(1),
                H(digest),
                S(role),
            )
        )
    leaf_inventory_sha = derived_hash("generated-leaf-inventory-v1", leaf_rows)
    leaf_manifest_payload = [
        H(spec_sha),
        H(generator_sha),
        H(leaf_inventory_sha),
        A("leaf-rows-v1", *leaf_rows),
    ]
    leaf_manifest_raw = enc("generated-leaf-manifest-v1", 1, leaf_manifest_payload)
    _exclusive_write(output_root / "leaf_manifest.json", leaf_manifest_raw)
    leaf_manifest_art = artifact_hash(
        "generated-leaf-manifest-v1", 1, leaf_manifest_payload
    )
    bundle_inputs = [
        H(spec_sha),
        H(generator_sha),
        H(leaf_inventory_sha),
        H(sha256_bytes(leaf_manifest_raw)),
        H(leaf_manifest_art),
    ]
    bundle_sha = derived_hash("generated-bundle-root-v1", bundle_inputs)
    bundle_payload = [*bundle_inputs, H(bundle_sha)]
    bundle_raw = enc("generated-bundle-root-v1", 1, bundle_payload)
    _exclusive_write(output_root / "bundle_root.json", bundle_raw)

    checkpoint_file_paths = [*ordered_paths, "leaf_manifest.json", "bundle_root.json"]
    checkpoint_file_rows: list[list[Any]] = []
    for rel in checkpoint_file_paths:
        path = output_root / rel
        checkpoint_file_rows.append(
            A(
                "generated-file-row-v1",
                S(rel),
                I(path.stat().st_size),
                I(0o444),
                I(1),
                H(sha256_file(path)),
                S(
                    role_by_path.get(
                        rel,
                        (
                            "LEAF_MANIFEST"
                            if rel == "leaf_manifest.json"
                            else "BUNDLE_ROOT"
                        ),
                    )
                ),
            )
        )
    dir_rows = _portable_dir_rows([*checkpoint_file_paths, "package_checkpoint.json"])
    tree_sha = derived_hash(
        "generated-package-tree-v1",
        [
            A("generated-file-rows-v1", *checkpoint_file_rows),
            A("generated-directory-rows-v1", *dir_rows),
        ],
    )
    checkpoint_payload = [
        H(spec_sha),
        H(generator_sha),
        H(sha256_bytes(leaf_manifest_raw)),
        H(sha256_bytes(bundle_raw)),
        H(bundle_sha),
        A("generated-file-rows-v1", *checkpoint_file_rows),
        A("generated-directory-rows-v1", *dir_rows),
        H(tree_sha),
        B(True),
    ]
    checkpoint_raw = enc("generated-package-checkpoint-v1", 1, checkpoint_payload)
    _exclusive_write(output_root / "package_checkpoint.json", checkpoint_raw)
    input_ledger_end = _immutable_input_ledger(spec, repo_root)
    if input_ledger_start != input_ledger_end:
        raise AuthorityError(
            "immutable source/runtime identity drifted during generation"
        )
    _freeze_tree(output_root)
    elapsed = time.perf_counter() - start
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = int(usage.ru_maxrss)
    if platform.system() != "Darwin":
        rss *= 1024
    file_paths = [path for path in output_root.rglob("*") if path.is_file()]
    total_bytes = sum(path.stat().st_size for path in file_paths)
    metrics = {
        "schema": "phase6_v3_1_z_generation_metrics_v1",
        "output_root": str(output_root),
        "spec_sha256": spec_sha,
        "generator_sha256": generator_sha,
        "bundle_root_sha256": sha256_bytes(bundle_raw),
        "bundle_authority_sha256": bundle_sha,
        "package_checkpoint_sha256": sha256_bytes(checkpoint_raw),
        "portable_tree_sha256": tree_sha,
        "wall_seconds": elapsed,
        "peak_rss_bytes": rss,
        "regular_file_count": len(file_paths),
        "directory_count": 1 + sum(path.is_dir() for path in output_root.rglob("*")),
        "generated_bytes": total_bytes,
        "predicate_count": len(predicates),
        "predicate_shard_count": len(predicate_shards),
        "conformance_vector_count": len(vectors),
        "conformance_shard_count": len(conformance_shards),
        "mutation_recipe_count": mutation_recipe_count,
        "mutation_shard_count": len(mutation_shards),
        "coverage_obligation_count": mutation_index["coverage_obligation_count"],
        "input_ledger_start_sha256": input_ledger_start["ledger_sha256"],
        "input_ledger_end_sha256": input_ledger_end["ledger_sha256"],
        "input_ledger_start_end_equal": input_ledger_start == input_ledger_end,
        "caps_pass": elapsed <= MAX_GENERATION_SECONDS
        and rss < MAX_RSS_BYTES
        and total_bytes < MAX_OUTPUT_BYTES,
    }
    if not metrics["caps_pass"]:
        raise AuthorityError(f"generation resource cap exceeded: {metrics}")
    return metrics


def _strict_jsonl_rows(path: Path) -> Iterator[list[Any]]:
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
                raise AuthorityError(
                    f"noncanonical JSONL line ending: {path}:{line_number}"
                )
            try:
                row = json.loads(raw, object_pairs_hook=_strict_pairs)
            except json.JSONDecodeError as exc:
                raise AuthorityError(
                    f"invalid JSONL {path}:{line_number}: {exc}"
                ) from exc
            if type(row) is not list or compact_array_bytes(row) != raw:
                raise AuthorityError(f"noncanonical JSONL row: {path}:{line_number}")
            yield row


def _strict_array_file(path: Path) -> tuple[bytes, list[Any]]:
    raw = path.read_bytes()
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_strict_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                AuthorityError(f"non-finite JSON token {token} in {path}")
            ),
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AuthorityError(f"invalid generated array {path}: {exc}") from exc
    if type(value) is not list or compact_array_bytes(value) != raw:
        raise AuthorityError(f"noncanonical generated array: {path}")
    return raw, value


def _expect_tag(value: Any, tag: str, context: str) -> Any:
    _validate_tagged_value(value, context)
    if value[0] != tag:
        raise AuthorityError(f"wrong tag in {context}: expected {tag}, got {value[0]}")
    if tag == "n":
        return None
    if tag == "i":
        return int(value[1])
    return value[1]


def _expect_a(value: Any, schema_id: str, context: str) -> list[Any]:
    _validate_tagged_value(value, context)
    if value[0] != "a" or value[1] != schema_id:
        raise AuthorityError(f"wrong compound schema in {context}")
    return value[2:]


def _decode_tree(value: Any) -> Any:
    _validate_tagged_value(value)
    tag = value[0]
    if tag == "n":
        return None
    if tag == "i":
        return int(value[1])
    if tag in {"s", "h", "d", "b"}:
        return value[1]
    members = value[2:]
    if members and all(
        type(member) is list
        and len(member) == 4
        and member[:2] == ["a", "named-member-v1"]
        for member in members
    ):
        result: dict[str, Any] = {}
        for member in members:
            key = _expect_tag(member[2], "s", "named member key")
            if key in result:
                raise AuthorityError(f"duplicate generated named member: {key}")
            result[key] = _decode_tree(member[3])
        return result
    return [_decode_tree(member) for member in members]


def _decode_record(
    raw_value: list[Any], schema_id: str, payload_count: int
) -> list[Any]:
    if len(raw_value) != payload_count + 2:
        raise AuthorityError(f"{schema_id} physical field count mismatch")
    if _expect_tag(raw_value[0], "s", f"{schema_id}.schema") != schema_id:
        raise AuthorityError(f"{schema_id} header mismatch")
    if _expect_tag(raw_value[1], "i", f"{schema_id}.revision") != 1:
        raise AuthorityError(f"{schema_id} revision mismatch")
    return raw_value[2:]


def _expected_shard_names(collection: str, count: int) -> list[str]:
    if count <= 0:
        raise AuthorityError(f"empty required generated collection: {collection}")
    result = []
    for shard_index, first in enumerate(range(0, count, MAX_SHARD_ROWS)):
        last = min(count, first + MAX_SHARD_ROWS) - 1
        result.append(
            f"{collection}/{collection}_{shard_index:04d}_{first:09d}_{last:09d}.jsonl"
        )
    return result


def check_tree(spec_path: Path, output_root: Path) -> dict[str, Any]:
    spec, registries = validate_spec(spec_path)
    if not output_root.is_dir() or output_root.is_symlink():
        raise AuthorityError("generated root missing, non-directory, or symlink")
    spec_sha = sha256_file(spec_path)
    generator_sha = sha256_file(Path(__file__).resolve(strict=True))
    predicates, operation_metrics = expand_predicates(spec, registries)
    digest_order, digest_edges = _topological_digest_nodes(spec["digest_nodes"])
    vectors = build_conformance_vectors(spec)
    mutation_count = _mutation_obligation_count(spec, predicates, digest_edges)

    predicate_names = _expected_shard_names("predicate_instances", len(predicates))
    conformance_names = _expected_shard_names("conformance_vectors", len(vectors))
    mutation_names = _expected_shard_names("mutation_oracle", mutation_count)
    expected_leaf_paths = [*spec["generated_output_plan"]["base_leaf_paths"]]
    expected_leaf_paths.extend(predicate_names)
    expected_leaf_paths.extend(conformance_names)
    expected_leaf_paths.append("conformance_vectors/conformance_expansion_index.json")
    expected_leaf_paths.extend(mutation_names)
    expected_leaf_paths.append("mutation_oracle/mutation_expansion_index.json")
    if len(expected_leaf_paths) != len(set(expected_leaf_paths)):
        raise AuthorityError("expected generated path collision")

    all_entries = [output_root, *output_root.rglob("*")]
    actual_files: dict[str, Path] = {}
    actual_dirs: dict[str, Path] = {".": output_root}
    for path in all_entries[1:]:
        info = path.lstat()
        rel = str(path.relative_to(output_root))
        if stat.S_ISLNK(info.st_mode):
            raise AuthorityError(f"symlink in generated tree: {rel}")
        if stat.S_ISREG(info.st_mode):
            if info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o444:
                raise AuthorityError(f"generated regular-file identity mismatch: {rel}")
            actual_files[rel] = path
        elif stat.S_ISDIR(info.st_mode):
            if stat.S_IMODE(info.st_mode) != 0o555:
                raise AuthorityError(f"generated directory identity mismatch: {rel}")
            actual_dirs[rel] = path
        else:
            raise AuthorityError(f"special entry in generated tree: {rel}")
    root_info = output_root.lstat()
    if stat.S_IMODE(root_info.st_mode) != 0o555:
        raise AuthorityError("generated root identity mismatch")
    terminal_paths = {
        "leaf_manifest.json",
        "bundle_root.json",
        "package_checkpoint.json",
    }
    if set(actual_files) != {*expected_leaf_paths, *terminal_paths}:
        raise AuthorityError(
            f"generated file set mismatch: missing={sorted({*expected_leaf_paths, *terminal_paths} - set(actual_files))} "
            f"extra={sorted(set(actual_files) - {*expected_leaf_paths, *terminal_paths})}"
        )

    predicate_shards: list[list[Any]] = []
    cursor = 0
    for rel in predicate_names:
        raw = actual_files[rel].read_bytes()
        lines = list(_strict_jsonl_rows(actual_files[rel]))
        expected_count = min(MAX_SHARD_ROWS, len(predicates) - cursor)
        if len(lines) != expected_count:
            raise AuthorityError(f"predicate shard row-count mismatch: {rel}")
        for local, parsed in enumerate(lines):
            expected_raw = encode_predicate_row(predicates[cursor + local])
            if compact_array_bytes(parsed) != expected_raw:
                raise AuthorityError(f"predicate expansion mismatch: {rel}:{local + 1}")
        predicate_shards.append(
            [
                rel,
                cursor,
                cursor + expected_count - 1,
                expected_count,
                sha256_bytes(raw),
            ]
        )
        cursor += expected_count
    if cursor != len(predicates):
        raise AuthorityError("predicate shard range gap")

    conformance_shards: list[list[Any]] = []
    cursor = 0
    for rel in conformance_names:
        raw = actual_files[rel].read_bytes()
        lines = list(_strict_jsonl_rows(actual_files[rel]))
        expected_count = min(MAX_SHARD_ROWS, len(vectors) - cursor)
        if len(lines) != expected_count:
            raise AuthorityError(f"conformance shard row-count mismatch: {rel}")
        for local, parsed in enumerate(lines):
            if compact_array_bytes(parsed) != encode_conformance_row(
                vectors[cursor + local]
            ):
                raise AuthorityError(f"conformance vector mismatch: {rel}:{local + 1}")
        conformance_shards.append(
            [
                rel,
                cursor,
                cursor + expected_count - 1,
                expected_count,
                sha256_bytes(raw),
            ]
        )
        cursor += expected_count

    seen_mutation_names: list[str] = []

    def verify_mutation_shard(rel: str, expected_raw: bytes) -> None:
        path = actual_files.get(rel)
        if path is None:
            raise AuthorityError(f"missing mutation shard: {rel}")
        if path.read_bytes() != expected_raw:
            raise AuthorityError(f"mutation shard reconstruction mismatch: {rel}")
        seen_mutation_names.append(rel)

    mutation_shards, mutation_index, recipe_count = _stream_mutation_recipe_shards(
        spec, predicates, digest_edges, verify_mutation_shard
    )
    if seen_mutation_names != mutation_names:
        raise AuthorityError("mutation shard order or range drift")

    expected_files: dict[str, tuple[bytes, str]] = {}
    schema_catalog = _artifact_schema_catalog(spec)
    expected_files["schema_catalog.json"] = (
        enc(
            "generated-schema-catalog-v1",
            1,
            [H(spec_sha), _tag_tree("schema-catalog-payload-v1", schema_catalog)],
        ),
        "SCHEMA_CATALOG",
    )
    digest_catalog = {
        "schema": "phase6_v3_1_z_digest_dag_v1",
        "gate_id": GATE_ID,
        "nodes": spec["digest_nodes"],
        "topological_order": digest_order,
        "edges": [list(edge) for edge in digest_edges],
        "acyclic": True,
    }
    expected_files["digest_dag.json"] = (
        enc(
            "generated-digest-dag-v1",
            1,
            [H(spec_sha), _tag_tree("digest-dag-payload-v1", digest_catalog)],
        ),
        "DIGEST_DAG",
    )
    global_counts = {
        "calls": 198,
        "predicates": 80_724,
        "events": 80_724,
        "prefixes": 80_724,
        "child_frames": 51_893,
        "acks": 51_893,
        "stage_finals": 3_564,
        "stage_opens": 3_366,
        "stage0_seeds": 198,
        "child_exits": 198,
        "lifecycle_receipts": 198,
        "p17_closures": 198,
    }
    operation_dags = {
        "schema": "phase6_v3_1_z_operation_dags_v1",
        "gate_id": GATE_ID,
        "operations": operation_metrics,
        "call_plans": spec["call_plans"],
        "state_machine": spec["state_machine"],
        "science_graph": spec["immutable_inputs"]["science_graph"],
        "global_counts": global_counts,
    }
    expected_files["operation_dags.json"] = (
        enc(
            "generated-operation-dags-v1",
            1,
            [H(spec_sha), _tag_tree("operation-dags-payload-v1", operation_dags)],
        ),
        "OPERATION_DAGS",
    )
    expected_files["path_grammar.json"] = (
        enc(
            "generated-path-grammar-v1",
            1,
            [H(spec_sha), _tag_tree("path-grammar-rules-v1", spec["path_grammar"])],
        ),
        "PATH_GRAMMAR",
    )
    expected_files["authority_progression.json"] = (
        enc(
            "generated-authority-progression-v1",
            1,
            [
                H(spec_sha),
                _tag_tree(
                    "authority-progression-payload-v1", spec["authority_progression"]
                ),
            ],
        ),
        "AUTHORITY_PROGRESSION",
    )
    resource_projection = _resource_projection(spec)
    expected_files["resource_projection.json"] = (
        enc(
            "generated-resource-projection-v1",
            1,
            [
                H(spec_sha),
                _tag_tree("resource-projection-payload-v1", resource_projection),
            ],
        ),
        "RESOURCE_PROJECTION",
    )
    conformance_index = {
        "schema": "phase6_v3_1_z_conformance_expansion_index_v1",
        "gate_id": GATE_ID,
        "vector_count": len(vectors),
        "ordered_vector_sha256": derived_hash(
            "ordered-conformance-vectors-v1",
            [H(sha256_bytes(encode_conformance_row(row))) for row in vectors],
        ),
        "shards": conformance_shards,
    }
    expected_files["conformance_vectors/conformance_expansion_index.json"] = (
        enc(
            "generated-conformance-expansion-index-v1",
            1,
            [H(spec_sha), _tag_tree("conformance-index-payload-v1", conformance_index)],
        ),
        "CONFORMANCE_INDEX",
    )
    expected_files["mutation_oracle/mutation_expansion_index.json"] = (
        enc(
            "generated-mutation-expansion-index-v1",
            1,
            [H(spec_sha), _tag_tree("mutation-index-payload-v1", mutation_index)],
        ),
        "MUTATION_INDEX",
    )
    catalog_sha = sha256_bytes(expected_files["schema_catalog.json"][0])
    expected_files["validator_python.py"] = (
        _generated_python_validator(spec_sha, generator_sha, catalog_sha),
        "PYTHON_VALIDATOR",
    )
    expected_files["validator_wolfram.wl"] = (
        _generated_wolfram_validator(spec_sha, generator_sha, catalog_sha),
        "WOLFRAM_VALIDATOR",
    )
    expected_files["compatibility_observer.wls"] = (
        _generated_compatibility_observer(spec, spec_sha, generator_sha),
        "ZERO_SCIENCE_COMPATIBILITY_OBSERVER",
    )
    shard_inventory = {
        "schema": "phase6_v3_1_z_shard_inventory_v1",
        "gate_id": GATE_ID,
        "max_rows_per_shard": MAX_SHARD_ROWS,
        "predicate_shards": predicate_shards,
        "conformance_shards": conformance_shards,
        "mutation_shards": mutation_shards,
        "counts": {
            "predicates": len(predicates),
            "conformance_vectors": len(vectors),
            "mutation_recipes": recipe_count,
            "coverage_obligations": mutation_index["coverage_obligation_count"],
        },
    }
    expected_files["shard_inventory.json"] = (
        enc(
            "generated-shard-inventory-v1",
            1,
            [H(spec_sha), _tag_tree("shard-inventory-payload-v1", shard_inventory)],
        ),
        "SHARD_INVENTORY",
    )
    for rel, (expected_raw, _role) in expected_files.items():
        if actual_files[rel].read_bytes() != expected_raw:
            raise AuthorityError(f"generated control leaf mismatch: {rel}")

    manifest_raw, manifest = _strict_array_file(actual_files["leaf_manifest.json"])
    manifest_payload = _decode_record(manifest, "generated-leaf-manifest-v1", 4)
    if _expect_tag(manifest_payload[0], "h", "manifest.spec") != spec_sha:
        raise AuthorityError("leaf manifest spec identity mismatch")
    if _expect_tag(manifest_payload[1], "h", "manifest.generator") != generator_sha:
        raise AuthorityError("leaf manifest generator identity mismatch")
    leaf_rows = _expect_a(manifest_payload[3], "leaf-rows-v1", "manifest leaf rows")
    if len(leaf_rows) != len(expected_leaf_paths):
        raise AuthorityError("leaf manifest cardinality mismatch")
    observed_leaf_paths: list[str] = []
    role_by_path = {rel: role for rel, (_raw, role) in expected_files.items()}
    role_by_path.update({rel: "PREDICATE_SHARD" for rel in predicate_names})
    role_by_path.update({rel: "CONFORMANCE_SHARD" for rel in conformance_names})
    role_by_path.update({rel: "MUTATION_SHARD" for rel in mutation_names})
    for ordinal, tagged_row in enumerate(leaf_rows):
        members = _expect_a(tagged_row, "generated-leaf-row-v1", f"leaf row {ordinal}")
        if len(members) != 6:
            raise AuthorityError("leaf row field count mismatch")
        rel = _expect_tag(members[0], "s", "leaf path")
        size = _expect_tag(members[1], "i", "leaf size")
        mode = _expect_tag(members[2], "i", "leaf mode")
        nlink = _expect_tag(members[3], "i", "leaf nlink")
        digest = _expect_tag(members[4], "h", "leaf digest")
        role = _expect_tag(members[5], "s", "leaf role")
        if rel != expected_leaf_paths[ordinal] or role != role_by_path[rel]:
            raise AuthorityError("leaf row declaration order/role mismatch")
        path = actual_files[rel]
        info = path.lstat()
        if (size, mode, nlink, digest) != (
            info.st_size,
            stat.S_IMODE(info.st_mode),
            info.st_nlink,
            sha256_file(path),
        ):
            raise AuthorityError(f"leaf row identity mismatch: {rel}")
        observed_leaf_paths.append(rel)
    leaf_inventory_sha = derived_hash("generated-leaf-inventory-v1", leaf_rows)
    if (
        _expect_tag(manifest_payload[2], "h", "manifest inventory")
        != leaf_inventory_sha
    ):
        raise AuthorityError("leaf inventory digest mismatch")

    bundle_raw, bundle = _strict_array_file(actual_files["bundle_root.json"])
    bundle_payload = _decode_record(bundle, "generated-bundle-root-v1", 6)
    manifest_art = artifact_hash("generated-leaf-manifest-v1", 1, manifest_payload)
    expected_bundle_inputs = [
        H(spec_sha),
        H(generator_sha),
        H(leaf_inventory_sha),
        H(sha256_bytes(manifest_raw)),
        H(manifest_art),
    ]
    if bundle_payload[:5] != expected_bundle_inputs:
        raise AuthorityError("bundle input binding mismatch")
    bundle_authority = derived_hash("generated-bundle-root-v1", expected_bundle_inputs)
    if bundle_payload[5] != H(bundle_authority):
        raise AuthorityError("bundle authority mismatch")

    checkpoint_raw, checkpoint = _strict_array_file(
        actual_files["package_checkpoint.json"]
    )
    checkpoint_payload = _decode_record(
        checkpoint, "generated-package-checkpoint-v1", 9
    )
    checkpoint_file_paths = [
        *expected_leaf_paths,
        "leaf_manifest.json",
        "bundle_root.json",
    ]
    checkpoint_file_rows = [
        A(
            "generated-file-row-v1",
            S(rel),
            I(actual_files[rel].stat().st_size),
            I(0o444),
            I(1),
            H(sha256_file(actual_files[rel])),
            S(
                role_by_path[rel]
                if rel in role_by_path
                else ("LEAF_MANIFEST" if rel == "leaf_manifest.json" else "BUNDLE_ROOT")
            ),
        )
        for rel in checkpoint_file_paths
    ]
    dir_rows = _portable_dir_rows([*checkpoint_file_paths, "package_checkpoint.json"])
    expected_dirs = {
        ".",
        *(
            str(PurePosixPath(rel).parent)
            for rel in checkpoint_file_paths
            if str(PurePosixPath(rel).parent) != "."
        ),
        "predicate_instances",
        "conformance_vectors",
        "mutation_oracle",
    }
    if set(actual_dirs) != expected_dirs:
        raise AuthorityError("generated directory inventory mismatch")
    for tagged_dir_row in dir_rows:
        members = _expect_a(
            tagged_dir_row, "generated-directory-row-v1", "directory row"
        )
        rel = _expect_tag(members[0], "s", "directory path")
        mode = _expect_tag(members[1], "i", "directory mode")
        nlink = _expect_tag(members[2], "i", "directory nlink")
        info = actual_dirs[rel].lstat()
        if (stat.S_IMODE(info.st_mode), info.st_nlink) != (mode, nlink):
            raise AuthorityError(f"generated directory stat mismatch: {rel}")
    tree_sha = derived_hash(
        "generated-package-tree-v1",
        [
            A("generated-file-rows-v1", *checkpoint_file_rows),
            A("generated-directory-rows-v1", *dir_rows),
        ],
    )
    expected_checkpoint_payload = [
        H(spec_sha),
        H(generator_sha),
        H(sha256_bytes(manifest_raw)),
        H(sha256_bytes(bundle_raw)),
        H(bundle_authority),
        A("generated-file-rows-v1", *checkpoint_file_rows),
        A("generated-directory-rows-v1", *dir_rows),
        H(tree_sha),
        B(True),
    ]
    if checkpoint_payload != expected_checkpoint_payload:
        raise AuthorityError("package checkpoint closure mismatch")
    total_bytes = sum(path.stat().st_size for path in actual_files.values())
    if total_bytes >= spec["resource_limits"]["generated_bundle_bytes_strict_max"]:
        raise AuthorityError("generated bundle byte cap exceeded")
    return {
        "schema": "phase6_v3_1_z_read_only_check_v1",
        "output_root": str(output_root),
        "predicate_count": len(predicates),
        "mutation_recipe_count": recipe_count,
        "coverage_obligation_count": mutation_index["coverage_obligation_count"],
        "bundle_root_raw_sha256": sha256_bytes(bundle_raw),
        "bundle_authority_sha256": bundle_authority,
        "package_checkpoint_sha256": sha256_bytes(checkpoint_raw),
        "portable_tree_sha256": tree_sha,
        "generated_bytes": total_bytes,
        "pass": True,
    }


def compare_trees(left: Path, right: Path) -> dict[str, Any]:
    def inventory(root: Path) -> dict[str, tuple[str, int, int, int, str]]:
        result: dict[str, tuple[str, int, int, int, str]] = {}
        for path in [root, *root.rglob("*")]:
            rel = "." if path == root else str(path.relative_to(root))
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise AuthorityError(f"symlink in compared tree: {path}")
            if stat.S_ISDIR(info.st_mode):
                result[rel] = (
                    "directory",
                    stat.S_IMODE(info.st_mode),
                    info.st_nlink,
                    0,
                    "",
                )
            elif stat.S_ISREG(info.st_mode):
                result[rel] = (
                    "file",
                    stat.S_IMODE(info.st_mode),
                    info.st_nlink,
                    info.st_size,
                    sha256_file(path),
                )
            else:
                raise AuthorityError(f"nonregular entry in compared tree: {path}")
        return result

    left_inventory = inventory(left)
    right_inventory = inventory(right)
    if left_inventory != right_inventory:
        missing_left = sorted(set(right_inventory) - set(left_inventory))
        missing_right = sorted(set(left_inventory) - set(right_inventory))
        changed = sorted(
            key
            for key in set(left_inventory) & set(right_inventory)
            if left_inventory[key] != right_inventory[key]
        )
        raise AuthorityError(
            f"portable tree mismatch: missing_left={missing_left} missing_right={missing_right} changed={changed[:20]}"
        )
    return {
        "schema": "phase6_v3_1_z_portable_tree_comparison_v1",
        "left": str(left),
        "right": str(right),
        "entry_count": len(left_inventory),
        "portable_inventory_sha256": derived_hash(
            "portable-comparison-inventory-v1",
            [
                A(
                    "portable-comparison-row-v1",
                    S(key),
                    S(left_inventory[key][0]),
                    I(left_inventory[key][1]),
                    I(left_inventory[key][2]),
                    I(left_inventory[key][3]),
                    H(left_inventory[key][4])
                    if left_inventory[key][0] == "file"
                    else N(),
                )
                for key in sorted(left_inventory)
            ],
        ),
        "byte_identical": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--spec", type=Path, required=True)
    generate_parser.add_argument("--output-root", type=Path, required=True)
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--spec", type=Path, required=True)
    check_parser.add_argument("--output-root", type=Path, required=True)
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--left", type=Path, required=True)
    compare_parser.add_argument("--right", type=Path, required=True)
    validate_parser = subparsers.add_parser("validate-spec")
    validate_parser.add_argument("--spec", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            result = generate(
                args.spec.resolve(strict=True), args.output_root.resolve(strict=False)
            )
        elif args.command == "check":
            result = check_tree(
                args.spec.resolve(strict=True), args.output_root.resolve(strict=True)
            )
        elif args.command == "compare":
            result = compare_trees(
                args.left.resolve(strict=True), args.right.resolve(strict=True)
            )
        else:
            spec, registries = validate_spec(args.spec.resolve(strict=True))
            predicates, operation_metrics = expand_predicates(spec, registries)
            _order, edges = _topological_digest_nodes(spec["digest_nodes"])
            result = {
                "schema": "phase6_v3_1_z_spec_validation_v1",
                "spec_sha256": sha256_file(args.spec.resolve(strict=True)),
                "top_level_key_count": len(spec),
                "predicate_count": len(predicates),
                "operation_metrics": operation_metrics,
                "digest_edge_count": len(edges),
                "pass": True,
            }
    except (AuthorityError, OSError, ValueError) as exc:
        error = {
            "schema": "phase6_v3_1_z_generator_failure_v1",
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "science_calls": 0,
            "wolfram_launches": 0,
        }
        sys.stderr.buffer.write(canonical_object_bytes(error))
        return 2
    sys.stdout.buffer.write(canonical_object_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
