(* Fresh one-key V3.1 external BHPT MST API smoke; not scientific evidence. *)
$HistoryLength = 0;
packageRoot = Environment["SCHWO_V31_BHPT_PACKAGE_ROOT"];
outputPath = Environment["SCHWO_V31_BHPT_OUTPUT"];
If[!DirectoryQ[packageRoot] || !StringQ[outputPath] || FileExistsQ[outputPath], Exit[64]];
Needs["PacletManager`"];
If[Quiet[Check[PacletDirectoryLoad[packageRoot], $Failed]] === $Failed, Exit[69]];
If[Quiet[Check[Needs["ReggeWheeler`"], $Failed]] === $Failed, Exit[69]];
rw = ToExpression["ReggeWheelerRadial"];
radial = Quiet[Check[rw[2, 2, N[1/10, 90], Method -> "MST",
  "BoundaryConditions" -> "In", "Potential" -> "ReggeWheeler",
  WorkingPrecision -> 80, PrecisionGoal -> 40, AccuracyGoal -> 40], $Failed]];
If[radial === $Failed, Exit[70]];
amplitudes = radial["Amplitudes"];
incidence = amplitudes["Incidence"];
reflection = amplitudes["Reflection"];
transmission = amplitudes["Transmission"];
If[!And @@ (NumberQ /@ {incidence, reflection, transmission}), Exit[70]];
record[z_] := <|"real" -> ToString[FortranForm[N[Re[z], 40]]],
  "imag" -> ToString[FortranForm[N[Im[z], 40]]]|>;
payload = <|
  "schema" -> "schwo.phase6.v3_1.bhpt_mst_smoke.v1",
  "method" -> "MST", "parity" -> "odd", "ell" -> 2, "kM" -> "0.1",
  "fresh_external_call_count" -> 1,
  "incidence" -> record[incidence], "reflection" -> record[reflection],
  "transmission" -> record[transmission], "wolfram_version" -> $Version,
  "system_id" -> $SystemID,
  "numerical_source" -> ExpandFileName[FindFile["ReggeWheeler`NumericalIntegration`"]]
|>;
If[Export[outputPath, payload, "RawJSON"] === $Failed, Exit[74]];
Exit[0];
