(* Generated source-distinct, zero-science GMA-Z1 tagged-wire validator. *)
ZSpecSHA256 = "d220d33202f8002e6364ce792ffb72559bafa87bda673f750e3caf96351a02db";
ZGeneratorSHA256 = "553b663410ba5a6aaf0f0a48aa7388e2ad70835f56be4efd762e7d5a04056e40";
ZSchemaCatalogSHA256 = "c22aede7e73b8874834be3b08b912b7842e55e47c0997d33ba28525a7fe421b8";
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
