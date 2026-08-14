(* Independent Black Hole Perturbation Toolkit MST benchmark for SchWO Fig. 8. *)

outputPath = Environment["SCHWO_BHPT_OUTPUT"];
packageRoot = Environment["SCHWO_BHPT_PACKAGE_ROOT"];
sourceCommit = Environment["SCHWO_BHPT_SOURCE_COMMIT"];
sourceSHA256 = Environment["SCHWO_BHPT_RADIAL_SHA256"];

If[!StringQ[outputPath] || StringLength[outputPath] == 0,
  Print["SCHWO_BHPT_OUTPUT is required."];
  Exit[64];
];
If[!StringQ[packageRoot] || !DirectoryQ[packageRoot],
  Print["SCHWO_BHPT_PACKAGE_ROOT must be an existing package directory."];
  Exit[64];
];

Needs["PacletManager`"];
PacletDirectoryLoad[packageRoot];
Needs["ReggeWheeler`"];

rwFunction = ToExpression["ReggeWheelerRadial"];
workingPrecision = 240;
precisionGoal = 80;
accuracyGoal = 80;
frequencies = N[{1/2, 1, 3/2, 2}, workingPrecision];
multipoles = Range[20, 40];

finiteComplexQ[value_] := NumberQ[value] &&
  FreeQ[value, Indeterminate | ComplexInfinity | DirectedInfinity | Infinity];

complexRecord[value_] := <|
  "real" -> N[Re[value], 17],
  "imag" -> N[Im[value], 17]
|>;

phaseRecord[k_, ell_] := Module[
  {radial, amplitudes, incidence, reflection, odd, sigma, epsilon, even},
  radial = rwFunction[
    2,
    ell,
    k,
    Method -> "MST",
    "BoundaryConditions" -> "In",
    "Potential" -> "ReggeWheeler",
    WorkingPrecision -> workingPrecision,
    PrecisionGoal -> precisionGoal,
    AccuracyGoal -> accuracyGoal
  ];
  If[radial === $Failed, Throw["ReggeWheelerRadial returned $Failed"]];
  amplitudes = radial["Amplitudes"];
  incidence = amplitudes["Incidence"];
  reflection = amplitudes["Reflection"];
  If[!finiteComplexQ[incidence] || !finiteComplexQ[reflection] || incidence == 0,
    Throw["nonfinite BHPT amplitude at kM=" <> ToString[k, InputForm] <>
      ", ell=" <> ToString[ell, InputForm]]
  ];
  odd = -reflection/((-1)^ell incidence);
  sigma = (ell - 1) ell (ell + 1) (ell + 2);
  epsilon = 2 k;
  even = odd (sigma + 6 I epsilon)/(sigma - 6 I epsilon);
  If[!finiteComplexQ[odd] || !finiteComplexQ[even],
    Throw["nonfinite BHPT phase factor at kM=" <> ToString[k, InputForm] <>
      ", ell=" <> ToString[ell, InputForm]]
  ];
  <|
    "kM" -> N[k, 17],
    "ell" -> ell,
    "incidence" -> complexRecord[incidence],
    "reflection" -> complexRecord[reflection],
    "odd" -> complexRecord[odd],
    "even_from_chandrasekhar" -> complexRecord[even]
  |>
];

records = Catch[
  Flatten[Table[phaseRecord[k, ell], {k, frequencies}, {ell, multipoles}], 1]
];
If[StringQ[records], Print[records]; Exit[70]];

payload = <|
  "schema_version" -> "schwo_bhpt_reggewheeler_mst_benchmark_v1",
  "toolkit" -> "BlackHolePerturbationToolkit/ReggeWheeler",
  "toolkit_url" -> "https://bhptoolkit.org/ReggeWheeler/",
  "toolkit_repository" -> "https://github.com/BlackHolePerturbationToolkit/ReggeWheeler",
  "toolkit_license" -> "MIT",
  "toolkit_source_commit" -> sourceCommit,
  "regge_wheeler_radial_sha256" -> sourceSHA256,
  "wolfram_version" -> $Version,
  "system_id" -> $SystemID,
  "method" -> "MST",
  "spin_weight_argument" -> 2,
  "potential" -> "ReggeWheeler",
  "boundary_conditions" -> "In",
  "working_precision" -> workingPrecision,
  "precision_goal" -> precisionGoal,
  "accuracy_goal" -> accuracyGoal,
  "odd_phase_definition" -> "-Reflection/((-1)^ell*Incidence)",
  "even_phase_source" -> "exact_chandrasekhar_starobinsky_ratio",
  "even_is_independent_radial_solution" -> False,
  "frequencies_kM" -> N[frequencies, 17],
  "ell_range" -> {First[multipoles], Last[multipoles]},
  "records" -> records
|>;

exportResult = Export[outputPath, payload, "RawJSON"];
If[exportResult === $Failed || !FileExistsQ[outputPath] || FileByteCount[outputPath] == 0,
  Exit[74]
];
Exit[0];
