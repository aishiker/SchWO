(* One-node V3.1-X BHPT NumericalIntegration producer. *)

$HistoryLength = 0;

fail[message_, code_: 70] := (WriteString[$Output, message <> "\n"]; Exit[code]);

expectedKernel = "/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel";
expectedScript = "/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/scripts/phase6_v3_1_x_bhpt_direct.wls";
If[Length[$CommandLine] =!= 5 ||
   $CommandLine[[1]] =!= expectedKernel ||
   $CommandLine[[2]] =!= "-script" ||
   $CommandLine[[3]] =!= expectedScript ||
   $ScriptCommandLine =!= {},
  fail["usage: phase6_v3_1_x_bhpt_direct.wls REQUEST OUTPUT", 64]
];

requestPath = ExpandFileName[$CommandLine[[4]]];
outputPath = ExpandFileName[$CommandLine[[5]]];
If[!FileExistsQ[requestPath] || FileExistsQ[outputPath],
  fail["request must exist and output must be absent", 73]
];

request = Quiet[Check[Import[requestPath, "RawJSON"], $Failed]];
If[!AssociationQ[request] ||
   Sort[Keys[request]] =!= Sort[{
     "schema", "operation", "gate_id", "expected", "overlay",
     "loaded_source_records", "method_contract"
   }] ||
   request["schema"] =!= "schwo.phase6.v3_1_x.external_direct_wls_request.v1",
  fail["request schema mismatch", 65]
];
operation = request["operation"];
If[!MemberQ[{"external_direct_node", "source_load_micro_sentinel"}, operation],
  fail["request operation mismatch", 65]
];

expected = request["expected"];
key = expected["key"];
node = expected["node"];
kLabel = key["kM"];
ell = key["ell"];
If[key["parity"] =!= "odd" ||
   key["anchor_id"] =!= "V3A-MODE-BHPT-RW-001" ||
   !IntegerQ[ell] || ell < 2,
  fail["only frozen odd Route-C keys are accepted", 65]
];
If[operation === "source_load_micro_sentinel" &&
   (node["node_id"] =!= "P1" || expected["call_ordinal"] =!= 0 ||
    expected["key_ordinal"] =!= 0 || expected["node_ordinal"] =!= 1 ||
    ell =!= 2 || kLabel =!= "0.1"),
  fail["micro key/node mismatch", 65]
];

wp = node["working_precision"];
pg = node["precision_goal"];
ag = node["accuracy_goal"];
If[!And @@ (IntegerQ /@ {wp, pg, ag}) ||
   !MemberQ[{{90, 45, 45}, {120, 60, 60}}, {wp, pg, ag}],
  fail["precision node mismatch", 65]
];

exactFrequency = Switch[kLabel,
  "0.1", 1/10,
  "0.5", 1/2,
  "1", 1,
  "2", 2,
  "4", 4,
  _, fail["frequency label mismatch", 65]
];
frequency = N[exactFrequency, wp + 20];
If[Precision[frequency] < wp + 10 || Precision[frequency] === MachinePrecision,
  fail["frequency precision assertion failed", 65]
];

packageRoot = ExpandFileName[request["overlay"]["root"]];
numericalSource = ExpandFileName[
  FileNameJoin[{packageRoot, "Kernel", "NumericalIntegration.m"}]
];
If[!DirectoryQ[packageRoot] ||
   ToLowerCase[FileHash[numericalSource, "SHA256", "HexString"]] =!=
     ToLowerCase[request["overlay"]["numerical_source_sha256"]],
  fail["overlay identity mismatch", 69]
];

requiredContexts = {
  "ReggeWheeler`",
  "ReggeWheeler`MST`MST`",
  "ReggeWheeler`MST`RenormalizedAngularMomentum`",
  "ReggeWheeler`NumericalIntegration`",
  "ReggeWheeler`Hyperboloidal`",
  "ReggeWheeler`ReggeWheelerRadial`",
  "ReggeWheeler`ReggeWheelerSource`",
  "ReggeWheeler`ReggeWheelerMode`"
};
requiredSourcePaths = {
  "Kernel/ReggeWheeler.m",
  "Kernel/MST/MST.m",
  "Kernel/MST/RenormalizedAngularMomentum.m",
  "Kernel/NumericalIntegration.m",
  "Kernel/Hyperboloidal.wl",
  "Kernel/ReggeWheelerRadial.m",
  "Kernel/ReggeWheelerSource.m",
  "Kernel/ReggeWheelerMode.m"
};
sourceFieldOrder = {"context", "path", "sha256", "size", "mode", "nlink"};

normalizedRelativePathQ[path_] := StringQ[path] && path =!= "" &&
  StringNormalize[path] === path &&
  StringMatchQ[path, RegularExpression["[A-Za-z0-9._/-]+"]] &&
  !StringStartsQ[path, "/"] && !StringEndsQ[path, "/"] &&
  !StringContainsQ[path, {"//", "\\", ":"}] &&
  FreeQ[StringSplit[path, "/"], "" | "." | ".."];

normalizeSourceRecord[record_, requiredContext_, requiredPath_] := Module[{values},
  If[!AssociationQ[record] || Sort[Keys[record]] =!= Sort[sourceFieldOrder],
    fail["loaded-source record schema mismatch", 69]
  ];
  values = Lookup[record, sourceFieldOrder];
  If[!MatchQ[values, {_String, _String, _String, _Integer, _Integer, _Integer}],
    fail["loaded-source record type mismatch", 69]
  ];
  If[values[[1]] =!= requiredContext || values[[2]] =!= requiredPath ||
     !normalizedRelativePathQ[values[[2]]] ||
     !StringMatchQ[values[[3]], RegularExpression["[0-9a-f]{64}"]] ||
     values[[4]] < 0 || values[[5]] =!= 292 || values[[6]] =!= 1,
    fail["loaded-source record semantic mismatch", 69]
  ];
  values
];

normalizeLedger[records_] := Module[{projection},
  If[!ListQ[records] || Length[records] =!= Length[requiredContexts],
    fail["loaded-source ledger cardinality mismatch", 69]
  ];
  projection = MapThread[
    normalizeSourceRecord,
    {records, requiredContexts, requiredSourcePaths}
  ];
  If[!DuplicateFreeQ[projection[[All, 1]]] ||
     !DuplicateFreeQ[projection[[All, 2]]],
    fail["loaded-source ledger duplicate context/path", 69]
  ];
  projection
];

freshSourceRecords[] := MapThread[
  Function[{context, relativePath},
    Module[{path, found},
      path = ExpandFileName[FileNameJoin[{packageRoot, relativePath}]];
      found = Quiet[Check[ExpandFileName[FindFile[context]], $Failed]];
      If[!FileExistsQ[path] || found === $Failed || found =!= path,
        fail["actual loaded source path mismatch", 69]
      ];
      <|
        "context" -> context,
        "path" -> relativePath,
        "sha256" -> ToLowerCase[FileHash[path, "SHA256", "HexString"]],
        "size" -> FileByteCount[path],
        "mode" -> 292,
        "nlink" -> 1
      |>
    ]
  ],
  {requiredContexts, requiredSourcePaths}
];

publishResult[payload_] := Module[{partial},
  partial = outputPath <> ".partial";
  If[FileExistsQ[partial], fail["partial output collision", 73]];
  Export[partial, payload, "RawJSON"];
  If[!FileExistsQ[partial] || FileExistsQ[outputPath],
    fail["output publication precondition failed", 73]
  ];
  RenameFile[partial, outputPath]
];

preLoadPackages = $Packages;
preLoadContextPath = $ContextPath;
preLoadSearchPath = $Path;
preLoadReggeWheelerPackages = Select[
  Join[preLoadPackages, preLoadContextPath],
  StringQ[#] && StringStartsQ[#, "ReggeWheeler`"] &
];
preLoadFindFile = Quiet[Check[FindFile["ReggeWheeler`"], $Failed]];
If[preLoadReggeWheelerPackages =!= {},
  fail["preloaded ReggeWheeler context contamination", 69]
];
preLoadFindFileRecord = If[preLoadFindFile === $Failed, Null, preLoadFindFile];

Needs["PacletManager`"];
preLoadReggeWheelerPaclets = Quiet[Check[PacletFind["ReggeWheeler"], $Failed]];
If[preLoadReggeWheelerPaclets === $Failed || !ListQ[preLoadReggeWheelerPaclets],
  fail["pre-load ReggeWheeler Paclet inventory failed", 69]
];
If[Quiet[Check[PacletDirectoryLoad[packageRoot], $Failed]] === $Failed,
  fail["PacletDirectoryLoad failed", 69]
];
loadedReggeWheelerPaclets = Quiet[Check[PacletFind["ReggeWheeler"], $Failed]];
If[loadedReggeWheelerPaclets === $Failed || !ListQ[loadedReggeWheelerPaclets],
  fail["post-load ReggeWheeler Paclet inventory failed", 69]
];
If[Quiet[Check[Needs["ReggeWheeler`"], $Failed]] === $Failed,
  fail["Needs[ReggeWheeler`] failed", 69]
];
If[Quiet[Check[Scan[Needs, Rest[requiredContexts]], $Failed]] === $Failed ||
   Sort[Select[$Packages, MemberQ[requiredContexts, #] &]] =!=
     Sort[requiredContexts],
  fail["actual loaded context closure mismatch", 69]
];
loadedNumerical = ExpandFileName[FindFile["ReggeWheeler`NumericalIntegration`"]];
If[loadedNumerical =!= numericalSource,
  fail["unexpected loaded NumericalIntegration source", 69]
];
expectedProjection = normalizeLedger[request["loaded_source_records"]];
loadedStart = freshSourceRecords[];
actualStartProjection = normalizeLedger[loadedStart];
If[!SameQ[actualStartProjection, expectedProjection],
  fail["loaded source start mismatch", 69]
];

observedEnvironment = Association @ Map[
  Function[name, name -> Environment[name]], Sort[Environment[]]
];

If[operation === "source_load_micro_sentinel",
  loadedEnd = freshSourceRecords[];
  actualEndProjection = normalizeLedger[loadedEnd];
  If[!SameQ[actualEndProjection, expectedProjection] ||
     !SameQ[actualEndProjection, actualStartProjection],
    fail["loaded source micro end mismatch", 69]
  ];
  microResult = <|
    "schema" -> "schwo.phase6.v3_1_x.source_load_micro_wls_result.v1",
    "operation" -> "source_load_micro_sentinel",
    "key" -> key,
    "node" -> node,
    "overlay" -> request["overlay"],
    "projection_field_order" -> sourceFieldOrder,
    "expected_source_projection" -> expectedProjection,
    "loaded_contexts_start" -> requiredContexts,
    "loaded_contexts_end" -> requiredContexts,
    "loaded_source_start" -> loadedStart,
    "loaded_source_end" -> loadedEnd,
    "loaded_source_projection_start" -> actualStartProjection,
    "loaded_source_projection_end" -> actualEndProjection,
    "preload_state" -> <|
      "packages" -> preLoadPackages,
      "context_path" -> preLoadContextPath,
      "search_path" -> preLoadSearchPath,
      "regge_wheeler_context_count" -> 0,
      "regge_wheeler_paclet_candidate_count" ->
        Length[preLoadReggeWheelerPaclets],
      "find_file_before_load" -> preLoadFindFileRecord
    |>,
    "paclet" -> <|
      "candidate_count_after_load" -> Length[loadedReggeWheelerPaclets],
      "loaded_count" -> 1,
      "loaded_root" -> packageRoot
    |>,
    "counters" -> <|
      "wolfram_launch_count" -> 1,
      "request_count" -> 1,
      "source_record_count_start" -> 8,
      "source_record_count_end" -> 8,
      "external_api_call_count" -> 0,
      "regge_wheeler_radial_call_count" -> 0,
      "solver_call_count" -> 0,
      "boundary_solution_count" -> 0,
      "overlap_record_count" -> 0,
      "scientific_call_count" -> 0
    |>,
    "scientific_evidence" -> False,
    "reusable_as_science" -> False,
    "reusable_as_full_sentinel_record" -> False,
    "terminal_state" -> "PASS_PENDING_FORMAL_T7_REVIEW",
    "runtime" -> <|
      "wolfram_version" -> $Version,
      "system_id" -> $SystemID,
      "observed_environment" -> observedEnvironment,
      "fake_child" -> False
    |>
  |>;
  publishResult[microResult];
  Exit[0];
];

rout = node["outer_multiplier"] N[
  Max[300, 8 Sqrt[ell (ell + 1)]/frequency], wp + 10
];
fractions = {4/5, 22/25, 24/25};
fractionLabels = {"0.80", "0.88", "0.96"};
radii = N[rout fractions, wp + 10];
domainRules = {"In" -> radii[[3]], "Up" -> radii[[1]]};
started = AbsoluteTime[];
pair = Quiet[Check[
  ReggeWheelerRadial[
    2, ell, frequency,
    Method -> {"NumericalIntegration", "Domain" -> domainRules},
    "BoundaryConditions" -> {"In", "Up"},
    "Potential" -> "ReggeWheeler",
    WorkingPrecision -> wp,
    PrecisionGoal -> pg,
    AccuracyGoal -> ag
  ],
  $Failed
]];
elapsed = AbsoluteTime[] - started;
If[pair === $Failed || !AssociationQ[pair] ||
   !And @@ (KeyExistsQ[pair, #] & /@ {"In", "Up"}),
  fail["ReggeWheelerRadial NumericalIntegration returned no In/Up pair"]
];
inRadial = pair["In"];
upRadial = pair["Up"];
If[{First[inRadial["Method"]], First[upRadial["Method"]]} =!=
     {"NumericalIntegration", "NumericalIntegration"} ||
   {inRadial["Potential"], upRadial["Potential"]} =!=
     {"ReggeWheeler", "ReggeWheeler"} ||
   {inRadial["BoundaryConditions"], upRadial["BoundaryConditions"]} =!=
     {"In", "Up"},
  fail["returned direct-method identity mismatch"]
];

finiteComplexQ[value_] := NumberQ[value] &&
  FreeQ[value, Indeterminate | ComplexInfinity | DirectedInfinity | Infinity];
decimalString[value_] := Module[{text, parts, mantissa, exponent = ""},
  text = StringReplace[
    ToString[FortranForm[N[value, wp]]],
    {"D" -> "e", "E" -> "e", "*10^" -> "e", "*^" -> "e"}
  ];
  parts = StringSplit[text, "e", 2];
  mantissa = parts[[1]];
  If[StringContainsQ[mantissa, "."],
    mantissa = StringReplace[mantissa, RegularExpression["0+$"] -> ""];
    mantissa = StringTrim[mantissa, "."]
  ];
  If[Length[parts] == 2, exponent = "e" <> parts[[2]]];
  mantissa <> exponent
];
significantDigits[text_] := Module[{mantissa, digits, significant},
  mantissa = First[StringSplit[text, "e", 2]];
  If[StringContainsQ[mantissa, "."] && StringEndsQ[mantissa, "0"],
    fail["noncanonical padded decimal", 65]
  ];
  digits = StringDelete[mantissa, {"-", "."}];
  significant = StringReplace[digits, RegularExpression["^0+"] -> ""];
  If[StringLength[significant] == 0, fail["nonexact scalar has no digits", 65]];
  StringLength[significant]
];
scalarRecord[value_] := Module[{numeric, text, sourcePrecision, sourceAccuracy, digits},
  If[TrueQ[value == 0],
    Return[<|
      "decimal" -> "0", "exact_zero" -> True,
      "source_precision_digits" -> Null, "source_accuracy_digits" -> Null,
      "serialized_significant_digits" -> 0
    |>]
  ];
  numeric = N[value, wp];
  text = decimalString[numeric];
  sourcePrecision = Floor[Precision[numeric]];
  sourceAccuracy = Floor[Accuracy[numeric]];
  digits = significantDigits[text];
  If[sourcePrecision < wp || sourceAccuracy < ag || digits < pg,
    fail["serialized numerical precision witness insufficient", 65]
  ];
  <|
    "decimal" -> text, "exact_zero" -> False,
    "source_precision_digits" -> sourcePrecision,
    "source_accuracy_digits" -> sourceAccuracy,
    "serialized_significant_digits" -> digits
  |>
];
complexRecord[value_] := <|"real" -> scalarRecord[Re[value]], "imag" -> scalarRecord[Im[value]]|>;

overlaps = MapThread[
  Function[{radius, label},
    Module[{f, h, hdot, u, udot},
      f = 1 - 2/radius;
      h = Quiet[Check[inRadial[radius], $Failed]];
      hdot = Quiet[Check[f Derivative[1][inRadial][radius], $Failed]];
      u = Quiet[Check[upRadial[radius], $Failed]];
      udot = Quiet[Check[f Derivative[1][upRadial][radius], $Failed]];
      If[MemberQ[{h, hdot, u, udot}, $Failed] ||
         !AllTrue[{h, hdot, u, udot}, finiteComplexQ],
        fail["nonfinite overlap basis value"]
      ];
      <|
        "fraction" -> label,
        "radius_M" -> scalarRecord[radius],
        "H" -> complexRecord[h],
        "Hdot" -> complexRecord[hdot],
        "U" -> complexRecord[u],
        "Udot" -> complexRecord[udot]
      |>
    ]
  ],
  {radii, fractionLabels}
];

loadedEnd = freshSourceRecords[];
actualEndProjection = normalizeLedger[loadedEnd];
If[!SameQ[actualEndProjection, expectedProjection] ||
   !SameQ[actualEndProjection, actualStartProjection],
  fail["loaded source end mismatch", 69]
];

result = <|
  "schema" -> "schwo.phase6.v3_1_x.external_direct_raw_node.v1",
  "call_ordinal" -> expected["call_ordinal"],
  "key_ordinal" -> expected["key_ordinal"],
  "key" -> key,
  "node_ordinal" -> expected["node_ordinal"],
  "node" -> node,
  "method" -> "NumericalIntegration",
  "potential" -> "ReggeWheeler",
  "boundary_conditions" -> {"In", "Up"},
  "frequency" -> <|
    "label" -> kLabel,
    "exact_numerator" -> Numerator[exactFrequency],
    "exact_denominator" -> Denominator[exactFrequency],
    "input_precision_digits" -> Floor[Precision[frequency]]
  |>,
  "external_api_call_count" -> 1,
  "external_boundary_solution_count" -> 2,
  "mst_call_count" -> 0,
  "internal_solver_call_count" -> 0,
  "overlay" -> request["overlay"],
  "overlaps" -> overlaps,
  "loaded_contexts_start" -> requiredContexts,
  "loaded_contexts_end" -> requiredContexts,
  "loaded_source_start" -> loadedStart,
  "loaded_source_end" -> loadedEnd,
  "runtime" -> <|
    "elapsed_seconds" -> decimalString[elapsed],
    "wolfram_version" -> $Version,
    "system_id" -> $SystemID,
    "observed_environment" -> observedEnvironment
  |>
|>;

publishResult[result];
Exit[0];
