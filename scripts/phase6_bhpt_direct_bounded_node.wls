(* One-key bounded BHPT NumericalIntegration producer for Phase-6 V1. *)

$HistoryLength = 0;

fail[message_, code_: 70] := (Print[message]; Exit[code]);

requiredEnvironment[name_] := Module[{value = Environment[name]},
  If[!StringQ[value] || StringLength[value] == 0,
    fail[name <> " is required.", 64]
  ];
  value
];

packageRoot = requiredEnvironment["SCHWO_BHPT_BOUNDED_PACKAGE_ROOT"];
outputPath = requiredEnvironment["SCHWO_BHPT_BOUNDED_OUTPUT"];
kLabel = requiredEnvironment["SCHWO_BHPT_BOUNDED_KM"];
sector = requiredEnvironment["SCHWO_BHPT_BOUNDED_SECTOR"];
expectedNumericalSource = requiredEnvironment["SCHWO_BHPT_BOUNDED_NUMERICAL_SOURCE"];
expectedNumericalSHA256 = requiredEnvironment["SCHWO_BHPT_BOUNDED_NUMERICAL_SHA256"];

integerEnvironment[name_] := Module[{text = requiredEnvironment[name]},
  If[!StringMatchQ[text, DigitCharacter ..],
    fail[name <> " must contain only decimal digits.", 65]
  ];
  FromDigits[text]
];

ell = integerEnvironment["SCHWO_BHPT_BOUNDED_ELL"];
workingPrecision = integerEnvironment["SCHWO_BHPT_BOUNDED_WP"];
precisionGoal = integerEnvironment["SCHWO_BHPT_BOUNDED_PG"];
accuracyGoal = integerEnvironment["SCHWO_BHPT_BOUNDED_AG"];
outputDigits = integerEnvironment["SCHWO_BHPT_BOUNDED_DIGITS"];

If[!DirectoryQ[packageRoot], fail["BHPT package root is unavailable.", 69]];
If[FileExistsQ[outputPath] || FileExistsQ[outputPath <> ".partial"],
  fail["Output and partial paths must be absent.", 73]
];
If[!IntegerQ[ell] || ell < 2 || !IntegerQ[workingPrecision] ||
   !IntegerQ[precisionGoal] || !IntegerQ[accuracyGoal] ||
   !IntegerQ[outputDigits] || workingPrecision < 30 ||
   precisionGoal < 10 || accuracyGoal < 10 ||
   precisionGoal >= workingPrecision || accuracyGoal >= workingPrecision ||
   outputDigits < 16 || outputDigits > workingPrecision,
  fail["Invalid key or precision configuration.", 65]
];
If[!MemberQ[{"0.5", "1", "2", "4"}, kLabel] ||
   !MemberQ[{"odd", "even"}, sector],
  fail["Invalid selected-domain key.", 65]
];

frequency = Switch[kLabel,
  "0.5", N[1/2, workingPrecision + 10],
  "1", N[1, workingPrecision + 10],
  "2", N[2, workingPrecision + 10],
  "4", N[4, workingPrecision + 10]
];
potential = If[sector === "odd", "ReggeWheeler", "Zerilli"];
matchFractions = {4/5, 22/25, 24/25};
matchLabels = {"0.8", "0.88", "0.96"};
selectedMatchIndex = 2;
outerRadius = N[Max[300, 8 Sqrt[ell (ell + 1)]/Abs[frequency]],
  workingPrecision];
matchRadii = N[outerRadius matchFractions, workingPrecision];
domainRules = {"In" -> Max[matchRadii], "Up" -> Min[matchRadii]};

Needs["PacletManager`"];
If[Quiet[Check[PacletDirectoryLoad[packageRoot], $Failed]] === $Failed,
  fail["PacletDirectoryLoad failed.", 69]
];
If[Quiet[Check[Needs["ReggeWheeler`"], $Failed]] === $Failed,
  fail["Needs[ReggeWheeler`] failed.", 69]
];
loadedNumericalSource = ExpandFileName[
  FindFile["ReggeWheeler`NumericalIntegration`"]
];
If[loadedNumericalSource =!= ExpandFileName[expectedNumericalSource] ||
   ToLowerCase[FileHash[loadedNumericalSource, "SHA256", "HexString"]] =!=
     ToLowerCase[expectedNumericalSHA256],
  fail["Loaded NumericalIntegration source identity changed.", 69]
];
rwFunction = ToExpression["ReggeWheelerRadial"];

finiteComplexQ[value_] := NumberQ[value] &&
  FreeQ[value, Indeterminate | ComplexInfinity | DirectedInfinity | Infinity];

decimalString[value_] := If[TrueQ[value == 0], "0",
  ToString[FortranForm[N[value, outputDigits]]]
];

complexRecord[value_] := <|
  "real" -> decimalString[Re[value]],
  "imag" -> decimalString[Im[value]]
|>;

matchAt[inRadial_, upRadial_, radius_, fractionLabel_] := Module[
  {f, inValue, inDerivative, upValue, upDerivative, incomingBasis,
   incomingDerivative, determinant, incidence, reflection, transmission,
   reflectionRatio, phaseFactor, fluxResidual},
  f = 1 - 2/radius;
  inValue = Quiet[Check[inRadial[radius], $Failed]];
  inDerivative = Quiet[Check[f Derivative[1][inRadial][radius], $Failed]];
  upValue = Quiet[Check[upRadial[radius], $Failed]];
  upDerivative = Quiet[Check[f Derivative[1][upRadial][radius], $Failed]];
  If[MemberQ[{inValue, inDerivative, upValue, upDerivative}, $Failed] ||
     !AllTrue[{inValue, inDerivative, upValue, upDerivative}, finiteComplexQ],
    fail["A radial value or derivative is nonfinite."]
  ];
  incomingBasis = Conjugate[upValue];
  incomingDerivative = Conjugate[upDerivative];
  determinant = incomingBasis upDerivative - upValue incomingDerivative;
  If[!finiteComplexQ[determinant] || TrueQ[determinant == 0],
    fail["The overlap basis Wronskian is zero or nonfinite."]
  ];
  incidence = (inValue upDerivative - upValue inDerivative)/determinant;
  reflection = (incomingBasis inDerivative - inValue incomingDerivative)/determinant;
  transmission = 1/incidence;
  reflectionRatio = reflection/incidence;
  phaseFactor = -reflection/((-1)^ell incidence);
  fluxResidual = Abs[Abs[reflectionRatio]^2 + Abs[transmission]^2 - 1];
  If[!AllTrue[{incidence, reflection, transmission, reflectionRatio,
      phaseFactor, fluxResidual}, finiteComplexQ],
    fail["A derived scattering quantity is nonfinite."]
  ];
  {
  <|
    "fraction" -> fractionLabel,
    "radius_M" -> decimalString[radius],
    "basis_wronskian_abs" -> decimalString[Abs[determinant]],
    "incidence" -> complexRecord[incidence],
    "reflection" -> complexRecord[reflection],
    "transmission" -> complexRecord[transmission],
    "reflection_ratio" -> complexRecord[reflectionRatio],
    "phase_factor" -> complexRecord[phaseFactor],
    "flux_unitarity_residual_abs" -> decimalString[fluxResidual]
  |>,
  phaseFactor
  }
];

{elapsedSeconds, radialPair} = AbsoluteTiming[
  Quiet[Check[
    rwFunction[
      2, ell, frequency,
      Method -> {"NumericalIntegration", "Domain" -> domainRules},
      "BoundaryConditions" -> {"In", "Up"},
      "Potential" -> potential,
      WorkingPrecision -> workingPrecision,
      PrecisionGoal -> precisionGoal,
      AccuracyGoal -> accuracyGoal
    ],
    $Failed
  ]]
];
If[radialPair === $Failed || !AssociationQ[radialPair] ||
   !And @@ (KeyExistsQ[radialPair, #] & /@ {"In", "Up"}),
  fail["ReggeWheelerRadial returned no In/Up pair."]
];
inRadial = radialPair["In"];
upRadial = radialPair["Up"];
If[{First[inRadial["Method"]], First[upRadial["Method"]]} =!=
     {"NumericalIntegration", "NumericalIntegration"} ||
   {inRadial["Potential"], upRadial["Potential"]} =!= {potential, potential} ||
   {inRadial["BoundaryConditions"], upRadial["BoundaryConditions"]} =!=
     {"In", "Up"},
  fail["Returned BHPT objects do not prove the requested direct method."]
];

matched = MapThread[matchAt[inRadial, upRadial, #1, #2] &,
  {matchRadii, matchLabels}
];
matchRecords = matched[[All, 1]];
phaseValues = matched[[All, 2]];
selected = matchRecords[[selectedMatchIndex]];
phaseSpread = Max[Abs[# - phaseValues[[selectedMatchIndex]]] & /@ phaseValues];

payload = <|
  "schema" -> "schwgw_phase6_bhpt_direct_bounded_node_v1",
  "key" -> <|"ell" -> ell, "kM" -> kLabel, "sector" -> sector|>,
  "potential" -> potential,
  "method" -> "NumericalIntegration",
  "boundary_conditions_solved" -> {"In", "Up"},
  "parity_derived_even_used" -> False,
  "precision" -> <|
    "working_precision_decimal_digits" -> workingPrecision,
    "precision_goal_decimal_digits" -> precisionGoal,
    "accuracy_goal_decimal_digits" -> accuracyGoal,
    "serialized_output_digits" -> outputDigits
  |>,
  "outer_boundary_radius_M" -> decimalString[outerRadius],
  "match_records" -> matchRecords,
  "selected_match_index" -> 1,
  "phase_factor" -> selected["phase_factor"],
  "reflection_ratio" -> selected["reflection_ratio"],
  "transmission" -> selected["transmission"],
  "matching_radius_phase_spread_abs" -> decimalString[phaseSpread],
  "selected_flux_unitarity_residual_abs" ->
    selected["flux_unitarity_residual_abs"],
  "solver_elapsed_seconds" -> decimalString[elapsedSeconds],
  "runtime" -> <|"wolfram_version" -> $Version, "system_id" -> $SystemID|>,
  "loaded_numerical_integration" -> <|
    "path" -> loadedNumericalSource,
    "sha256" -> ToLowerCase[expectedNumericalSHA256]
  |>,
  "global_green_permitted" -> False
|>;

partialPath = outputPath <> ".partial";
If[Quiet[Check[Export[partialPath, payload, "RawJSON"], $Failed]] === $Failed,
  fail["RawJSON export failed.", 74]
];
If[Quiet[Check[RenameFile[partialPath, outputPath], $Failed]] === $Failed,
  fail["Atomic RawJSON publication failed.", 74]
];
Exit[0];
