(* Frozen Phase-6 external BHPT direct-integration calibration producer. *)

requestPath = Environment["SCHWO_BHPT_DIRECT_REQUEST"];
outputPath = Environment["SCHWO_BHPT_DIRECT_OUTPUT"];
packageRoot = Environment["SCHWO_BHPT_DIRECT_PACKAGE_ROOT"];
requestSHA256 = Environment["SCHWO_BHPT_DIRECT_REQUEST_SHA256"];

fail[message_, code_: 70] := (Print[message]; Exit[code]);

If[!StringQ[requestPath] || !FileExistsQ[requestPath],
  fail["SCHWO_BHPT_DIRECT_REQUEST must name an existing JSON request.", 64]
];
If[!StringQ[outputPath] || StringLength[outputPath] == 0,
  fail["SCHWO_BHPT_DIRECT_OUTPUT is required.", 64]
];
If[!StringQ[packageRoot] || !DirectoryQ[packageRoot],
  fail["SCHWO_BHPT_DIRECT_PACKAGE_ROOT must be an existing directory.", 64]
];
If[!StringQ[requestSHA256] || StringLength[requestSHA256] != 64,
  fail["SCHWO_BHPT_DIRECT_REQUEST_SHA256 is required.", 64]
];
If[FileExistsQ[outputPath] || FileExistsQ[outputPath <> ".partial"],
  fail["Output and partial output paths must both be absent.", 73]
];

request = Quiet[Check[Import[requestPath, "RawJSON"], $Failed]];
If[!AssociationQ[request] ||
   request["schema_version"] =!= "schwgw_phase6_bhpt_direct_selected_request_v1",
  fail["The external direct request is invalid.", 65]
];

keys = request["external_direct_domain"]["records"];
If[!ListQ[keys] || Length[keys] != 30 || !AllTrue[keys, AssociationQ],
  fail["The request must contain exactly 30 key associations.", 65]
];

workingPrecision = request["precision"]["working_precision_decimal_digits"];
precisionGoal = request["precision"]["precision_goal_decimal_digits"];
accuracyGoal = request["precision"]["accuracy_goal_decimal_digits"];
outputDigits = request["precision"]["serialized_output_digits"];
matchFractions = {4/5, 22/25, 24/25};
matchFractionLabels = {"0.8", "0.88", "0.96"};
selectedMatchIndex = 2; (* Mathematica is one-indexed; JSON records zero-indexed 1. *)

If[{workingPrecision, precisionGoal, accuracyGoal, outputDigits} =!=
   {800, 200, 200, 100},
  fail["The frozen precision contract changed.", 65]
];

Needs["PacletManager`"];
loadResult = Quiet[Check[PacletDirectoryLoad[packageRoot], $Failed]];
If[loadResult === $Failed, fail["PacletDirectoryLoad failed.", 69]];
needsResult = Quiet[Check[Needs["ReggeWheeler`"], $Failed]];
If[needsResult === $Failed, fail["Needs[ReggeWheeler`] failed.", 69]];
rwFunction = ToExpression["ReggeWheelerRadial"];

finiteComplexQ[value_] := NumberQ[value] &&
  FreeQ[value, Indeterminate | ComplexInfinity | DirectedInfinity | Infinity];

decimalString[value_] := If[
  TrueQ[value == 0],
  "0",
  ToString[FortranForm[N[value, outputDigits]]]
];

complexRecord[value_] := <|
  "real" -> decimalString[Re[value]],
  "imag" -> decimalString[Im[value]]
|>;

frequencyFor[label_] := Switch[
  label,
  "0.5", N[1/2, workingPrecision + 20],
  "1", N[1, workingPrecision + 20],
  "2", N[2, workingPrecision + 20],
  "4", N[4, workingPrecision + 20],
  _, fail["Unexpected kM label: " <> ToString[label, InputForm], 65]
];

potentialFor[sector_] := Switch[
  sector,
  "odd", "ReggeWheeler",
  "even", "Zerilli",
  _, fail["Unexpected sector: " <> ToString[sector, InputForm], 65]
];

conventionBudget[] := <|
  "status" -> "FROZEN_FOR_EXTERNAL_CALIBRATION_NOT_GLOBAL",
  "Fourier_convention" -> "exp(-i*k*t)",
  "tortoise_definition" -> "r_star=r+2*log(r/2-1), M=1",
  "phase_factor_definition" -> "-Reflection/((-1)^ell*Incidence)",
  "absolute_phase_origin" ->
    "BHPT tortoise coordinate with no additive constant",
  "phase_or_normalization_fit" -> False,
  "remaining_convention_uncertainty" ->
    "comparison consumers must prove the same master-function and phase convention"
|>;

matchAt[inRadial_, upRadial_, frequency_, ell_, radius_, fractionLabel_] := Module[
  {f, inValue, inDerivative, upValue, upDerivative, incomingBasis,
   incomingDerivative, determinant, incidence, reflection, transmission,
   reflectionRatio, phaseFactor, fluxResidual, exported},
  f = 1 - 2/radius;
  inValue = Quiet[Check[inRadial[radius], $Failed]];
  inDerivative = Quiet[Check[f Derivative[1][inRadial][radius], $Failed]];
  upValue = Quiet[Check[upRadial[radius], $Failed]];
  upDerivative = Quiet[Check[f Derivative[1][upRadial][radius], $Failed]];
  If[MemberQ[{inValue, inDerivative, upValue, upDerivative}, $Failed] ||
     !AllTrue[{inValue, inDerivative, upValue, upDerivative}, finiteComplexQ],
    fail["A direct radial value or derivative is nonfinite."]
  ];
  incomingBasis = Conjugate[upValue];
  incomingDerivative = Conjugate[upDerivative];
  determinant = incomingBasis upDerivative - upValue incomingDerivative;
  If[!finiteComplexQ[determinant] || TrueQ[determinant == 0],
    fail["The In/Up overlap basis has a zero or nonfinite Wronskian."]
  ];
  incidence = (inValue upDerivative - upValue inDerivative)/determinant;
  reflection = (incomingBasis inDerivative - inValue incomingDerivative)/determinant;
  If[!finiteComplexQ[incidence] || !finiteComplexQ[reflection] ||
     TrueQ[incidence == 0],
    fail["The extracted incidence/reflection amplitudes are invalid."]
  ];
  transmission = 1/incidence;
  reflectionRatio = reflection/incidence;
  phaseFactor = -reflection/((-1)^ell incidence);
  fluxResidual = Abs[Abs[reflectionRatio]^2 + Abs[transmission]^2 - 1];
  If[!AllTrue[{transmission, reflectionRatio, phaseFactor, fluxResidual},
      finiteComplexQ],
    fail["The derived direct-scattering quantities are nonfinite."]
  ];
  exported = <|
    "match_fraction_of_upstream_outer_boundary" -> fractionLabel,
    "match_radius_M" -> decimalString[radius],
    "basis_wronskian_abs" -> decimalString[Abs[determinant]],
    "incidence" -> complexRecord[incidence],
    "reflection" -> complexRecord[reflection],
    "transmission" -> complexRecord[transmission],
    "reflection_ratio" -> complexRecord[reflectionRatio],
    "phase_factor" -> complexRecord[phaseFactor],
    "flux_unitarity_residual_abs" -> decimalString[fluxResidual]
  |>;
  {exported, phaseFactor}
];

directRecord[key_] := Module[
  {kLabel, sector, ell, frequency, potential, outerRadius, matchRadii,
   domainRules, radialPair, inRadial, upRadial, methodNames, potentials,
   boundaryNames, matched, matchRecords, phases, selected, phaseSpread,
   numericalBudget},
  If[Sort[Keys[key]] =!= Sort[{"ell", "kM", "sector"}],
    fail["A direct key has unexpected fields.", 65]
  ];
  kLabel = key["kM"];
  sector = key["sector"];
  ell = key["ell"];
  If[!IntegerQ[ell] || ell < 2, fail["ell must be an integer >= 2.", 65]];
  frequency = frequencyFor[kLabel];
  potential = potentialFor[sector];
  outerRadius = N[100/Abs[frequency], workingPrecision];
  matchRadii = N[outerRadius matchFractions, workingPrecision];
  domainRules = {
    "In" -> Max[matchRadii],
    "Up" -> Min[matchRadii]
  };
  radialPair = Quiet[Check[
    rwFunction[
      2,
      ell,
      frequency,
      Method -> {"NumericalIntegration", "Domain" -> domainRules},
      "BoundaryConditions" -> {"In", "Up"},
      "Potential" -> potential,
      WorkingPrecision -> workingPrecision,
      PrecisionGoal -> precisionGoal,
      AccuracyGoal -> accuracyGoal
    ],
    $Failed
  ]];
  If[radialPair === $Failed || !AssociationQ[radialPair] ||
     !And @@ (KeyExistsQ[radialPair, #] & /@ {"In", "Up"}),
    fail["ReggeWheelerRadial direct integration returned no In/Up pair for " <>
      kLabel <> "/" <> sector <> "/" <> ToString[ell]]
  ];
  inRadial = radialPair["In"];
  upRadial = radialPair["Up"];
  methodNames = {First[inRadial["Method"]], First[upRadial["Method"]]};
  potentials = {inRadial["Potential"], upRadial["Potential"]};
  boundaryNames = {inRadial["BoundaryConditions"],
    upRadial["BoundaryConditions"]};
  If[methodNames =!= {"NumericalIntegration", "NumericalIntegration"} ||
     potentials =!= {potential, potential} ||
     boundaryNames =!= {"In", "Up"},
    fail["The returned BHPT objects do not prove the requested direct method."]
  ];
  matched = MapThread[
    matchAt[inRadial, upRadial, frequency, ell, #1, #2] &,
    {matchRadii, matchFractionLabels}
  ];
  matchRecords = matched[[All, 1]];
  phases = matched[[All, 2]];
  selected = matchRecords[[selectedMatchIndex]];
  phaseSpread = Max[Abs[# - phases[[selectedMatchIndex]]] & /@ phases];
  numericalBudget = <|
    "status" -> "PARTIAL_MEASURED_NOT_ACCEPTANCE",
    "matching_radius_phase_spread_abs" -> decimalString[phaseSpread],
    "selected_flux_unitarity_residual_abs" ->
      selected["flux_unitarity_residual_abs"],
    "working_precision_decimal_digits" -> workingPrecision,
    "precision_goal_decimal_digits" -> precisionGoal,
    "accuracy_goal_decimal_digits" -> accuracyGoal,
    "unquantified_sources" -> {
      "BHPT upstream asymptotic-series truncation at r=100/abs(kM)",
      "NDSolve discretization beyond the frozen precision/accuracy goals",
      "cross-backend difference is assessed by a separate consumer"
    }
  |>;
  <|
    "kM" -> kLabel,
    "sector" -> sector,
    "ell" -> ell,
    "potential" -> potential,
    "method" -> "NumericalIntegration",
    "boundary_conditions_solved" -> {"In", "Up"},
    "external_api_call_count" -> 1,
    "external_boundary_solution_count" -> 2,
    "sector_is_independent_external_radial_solution" -> True,
    "parity_derived_even_used" -> False,
    "derived_from_sector" -> Null,
    "match_records" -> matchRecords,
    "selected_match_index" -> 1,
    "incidence" -> selected["incidence"],
    "reflection" -> selected["reflection"],
    "transmission" -> selected["transmission"],
    "reflection_ratio" -> selected["reflection_ratio"],
    "phase_factor" -> selected["phase_factor"],
    "numerical_uncertainty_budget" -> numericalBudget,
    "convention_uncertainty_budget" -> conventionBudget[]
  |>
];

records = directRecord /@ keys;
If[Length[records] != 30, fail["The direct producer did not return 30 records."]];

sourceFiles = request["toolkit_source"]["files"];
sourceHashes = AssociationMap[sourceFiles[#]["sha256"] &, Keys[sourceFiles]];

payload = <|
  "schema_version" -> "schwgw_phase6_bhpt_direct_selected_raw_v1",
  "acceptance_scope" ->
    "EXTERNAL_SOURCE_CALIBRATION_ONLY_NOT_DOMAIN_ACCEPTANCE",
  "global_green_permitted" -> False,
  "scientific_acceptance_status" -> "NOT_ASSESSED",
  "paper_figure_agreement_used" -> False,
  "request_sha256" -> requestSHA256,
  "external_direct_domain" -> <|
    "schema" -> "schwgw_phase6_external_direct_calibration_v1",
    "purpose" -> "EXTERNAL_SOURCE_CALIBRATION_ONLY_NOT_DOMAIN_ACCEPTANCE",
    "count" -> 30,
    "key_list_sha256" ->
      "d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b"
  |>,
  "toolkit" -> <|
    "name" -> "BlackHolePerturbationToolkit/ReggeWheeler",
    "repository" ->
      "https://github.com/BlackHolePerturbationToolkit/ReggeWheeler",
    "license" -> "MIT",
    "source_commit" -> request["toolkit_source"]["commit"],
    "source_hashes" -> sourceHashes
  |>,
  "runtime" -> <|
    "wolfram_version" -> $Version,
    "system_id" -> $SystemID
  |>,
  "backend_contract" -> <|
    "method" -> "NumericalIntegration",
    "spin_weight_argument" -> 2,
    "potential_by_sector" -> <|
      "odd" -> "ReggeWheeler",
      "even" -> "Zerilli"
    |>,
    "boundary_conditions_solved" -> {"In", "Up"},
    "external_api_calls_per_key" -> 1,
    "external_api_call_count" -> 30,
    "external_boundary_solutions_per_key" -> 2,
    "external_boundary_solution_count" -> 60,
    "even_is_independent_radial_solution" -> True,
    "parity_derived_even_used" -> False,
    "internal_solver_fallback_used" -> False,
    "project_solver_components_used" -> {}
  |>,
  "precision" -> <|
    "working_precision_decimal_digits" -> workingPrecision,
    "precision_goal_decimal_digits" -> precisionGoal,
    "accuracy_goal_decimal_digits" -> accuracyGoal,
    "serialized_output_digits" -> outputDigits
  |>,
  "matching" -> <|
    "method" -> "two-solution Wronskian decomposition",
    "upstream_outer_boundary_radius_formula_M" -> "100/abs(kM)",
    "match_radius_fractions_of_upstream_outer_boundary" ->
      matchFractionLabels,
    "selected_match_index" -> 1,
    "phase_factor_definition" -> "-Reflection/((-1)^ell*Incidence)",
    "transmission_definition" -> "1/Incidence",
    "reflection_ratio_definition" -> "Reflection/Incidence"
  |>,
  "numerical_uncertainty_budget" -> <|
    "status" -> "PARTIAL_PER_RECORD_NOT_DOMAIN_ACCEPTANCE",
    "measured_terms" -> {
      "three-radius matching spread",
      "selected-radius flux unitarity residual"
    },
    "acceptance_threshold_frozen" -> False
  |>,
  "convention_uncertainty_budget" -> conventionBudget[],
  "record_count" -> Length[records],
  "records" -> records
|>;

partialPath = outputPath <> ".partial";
exportResult = Quiet[Check[Export[partialPath, payload, "RawJSON"], $Failed]];
If[exportResult === $Failed || !FileExistsQ[partialPath] ||
   FileByteCount[partialPath] == 0,
  fail["RawJSON export failed.", 74]
];
renameResult = Quiet[Check[RenameFile[partialPath, outputPath], $Failed]];
If[renameResult === $Failed || !FileExistsQ[outputPath],
  fail["Atomic RawJSON publication failed.", 74]
];
Exit[0];
