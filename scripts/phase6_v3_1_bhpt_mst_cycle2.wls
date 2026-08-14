(* V3.1-U repair-cycle-2: total, one-shot, odd-only BHPT MST route. *)
$HistoryLength = 0;
packageRoot = Environment["SCHWO_V31_BHPT_PACKAGE_ROOT"];
inputPath = Environment["SCHWO_V31_BHPT_INPUT"];
outputPath = Environment["SCHWO_V31_BHPT_OUTPUT"];

record[z_] := <|
  "real" -> ToString[FortranForm[N[Re[z], 50]]],
  "imag" -> ToString[FortranForm[N[Im[z], 50]]]
|>;
errorRecord[ordinal_, key_, code_, detail_, callCount_] := <|
  "schema" -> "schwo.phase6.v3_1_u.external_anchor_outcome.v1",
  "ordinal" -> ordinal, "key" -> key, "status" -> "ERROR",
  "error" -> <|"code" -> code, "detail" -> detail|>,
  "fresh_external_call_count" -> callCount
|>;

request = Quiet[Check[Import[inputPath, "RawJSON"], $Failed]];
If[request === $Failed || !AssociationQ[request] || !ListQ[request["anchors"]], Exit[65]];
anchors = request["anchors"];

packageReady = DirectoryQ[packageRoot] &&
  Quiet[Check[Needs["PacletManager`"]; PacletDirectoryLoad[packageRoot], $Failed]] =!= $Failed &&
  Quiet[Check[Needs["ReggeWheeler`"], $Failed]] =!= $Failed;
requiredLoadedContexts = {
  "ReggeWheeler`",
  "ReggeWheeler`MST`RenormalizedAngularMomentum`",
  "ReggeWheeler`MST`MST`",
  "ReggeWheeler`NumericalIntegration`",
  "ReggeWheeler`Hyperboloidal`",
  "ReggeWheeler`ReggeWheelerRadial`",
  "ReggeWheeler`ReggeWheelerSource`",
  "ReggeWheeler`ReggeWheelerMode`"
};
requiredLoadedRelativePaths = {
  "Kernel/ReggeWheeler.m",
  "Kernel/MST/RenormalizedAngularMomentum.m",
  "Kernel/MST/MST.m",
  "Kernel/NumericalIntegration.m",
  "Kernel/Hyperboloidal.wl",
  "Kernel/ReggeWheelerRadial.m",
  "Kernel/ReggeWheelerSource.m",
  "Kernel/ReggeWheelerMode.m"
};
requiredLoadedSources = ExpandFileName[
  FileNameJoin[{packageRoot, #}]] & /@ requiredLoadedRelativePaths;
foundLoadedSources = Quiet[Check[FindFile /@ requiredLoadedContexts, $Failed]];
loadedSourceReady = packageReady && ListQ[foundLoadedSources] &&
  Length[DeleteDuplicates[foundLoadedSources]] === Length[requiredLoadedSources] &&
  And @@ (MemberQ[$Packages, #] & /@ requiredLoadedContexts) &&
  (ExpandFileName /@ foundLoadedSources) === requiredLoadedSources;
packageReady = packageReady && loadedSourceReady;
rw = If[packageReady, ToExpression["ReggeWheelerRadial"], $Failed];

one[key_, ordinal_] := Module[{ell, k, radial, amplitudes, incidence,
    reflection, transmission, ratio, s, t, gamma, logGamma},
  If[!packageReady,
    Return[errorRecord[ordinal, key, "PACKAGE_LOAD_FAILED", "ReggeWheeler package unavailable", 0]]
  ];
  ell = key["ell"]; k = ToExpression[key["kM"]];
  radial = Quiet[Check[rw[2, ell, N[k, 100], Method -> "MST",
      "BoundaryConditions" -> "In", "Potential" -> "ReggeWheeler",
      WorkingPrecision -> 90, PrecisionGoal -> 45, AccuracyGoal -> 45], $Failed]];
  If[radial === $Failed,
    Return[errorRecord[ordinal, key, "MST_FAILED", "ReggeWheelerRadial returned $Failed", 1]]
  ];
  amplitudes = Quiet[Check[radial["Amplitudes"], $Failed]];
  If[amplitudes === $Failed,
    Return[errorRecord[ordinal, key, "AMPLITUDE_INVALID", "amplitude mapping unavailable", 1]]
  ];
  incidence = Quiet[Check[amplitudes["Incidence"], $Failed]];
  reflection = Quiet[Check[amplitudes["Reflection"], $Failed]];
  transmission = Quiet[Check[amplitudes["Transmission"], $Failed]];
  If[!And @@ (NumberQ /@ {incidence, reflection, transmission}) || incidence == 0,
    Return[errorRecord[ordinal, key, "AMPLITUDE_INVALID", "non-numeric or zero incidence", 1]]
  ];
  ratio = reflection/incidence; s = -ratio/((-1)^ell);
  t = transmission/incidence; gamma = Abs[t]^2; logGamma = Log[gamma];
  <|"schema" -> "schwo.phase6.v3_1_u.external_anchor_outcome.v1",
    "ordinal" -> ordinal, "key" -> key, "status" -> "PASS",
    "method" -> "MST", "fresh_external_call_count" -> 1,
    "genuinely_independent" -> True, "even_independent_solve" -> False,
    "incidence" -> record[incidence], "reflection" -> record[reflection],
    "transmission" -> record[transmission], "reflection_ratio" -> record[ratio],
    "S" -> record[s], "T_horizon" -> record[t],
    "Gamma_flux" -> ToString[FortranForm[N[gamma, 50]]],
    "log_Gamma_flux" -> ToString[FortranForm[N[logGamma, 50]]]|>
];

outcomes = MapIndexed[one[#1, First[#2] - 1] &, anchors];
loadedSourceRecords = <|
  "path" -> #,
  "sha256" -> ToLowerCase[FileHash[#, "SHA256", "HexString"]],
  "size" -> FileByteCount[#]
|> & /@ requiredLoadedSources;
firstFailure = SelectFirst[outcomes, #["status"] === "ERROR" &, Missing["NotFound"]];
payload = <|
  "schema" -> "schwo.phase6.v3_1_u.external_batch_terminal.v1",
  "terminal" -> True, "requested_anchor_count" -> Length[anchors],
  "outcome_count" -> Length[outcomes], "outcomes" -> outcomes,
  "fresh_external_call_count" -> Total[Lookup[outcomes, "fresh_external_call_count", 0]],
  "overall_status" -> If[MissingQ[firstFailure], "PASS", "ERROR"],
  "first_failure" -> If[MissingQ[firstFailure], Null,
    KeyTake[firstFailure, {"ordinal", "key", "error"}]],
  "wolfram_version" -> $Version, "system_id" -> $SystemID,
  "loaded_source_records" -> loadedSourceRecords,
  "method_contract" -> <|"Method" -> "MST", "WorkingPrecision" -> 90,
    "PrecisionGoal" -> 45, "AccuracyGoal" -> 45,
    "Potential" -> "ReggeWheeler", "BoundaryConditions" -> "In"|>
|>;
If[Export[outputPath, payload, "RawJSON"] === $Failed, Exit[74]];
If[MissingQ[firstFailure] && Length[outcomes] === 23, Exit[0], Exit[70]];
