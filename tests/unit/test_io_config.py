from __future__ import annotations

import pytest

from schwgw.io.config import ConfigError, load_config


def test_load_config_parses_required_yaml_fields(tmp_path):
    path = tmp_path / "case.yaml"
    path.write_text(
        """
case_id: CASE_A
output: results.npz
background:
  M: 1.0
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_values: [0.0, 0.2]
  phi_values: [0.0]
numerics:
  lmax: 3
  boundary:
    r_in_eps: 1.0e-6
    r_out: 80.0
    rtol: 1.0e-10
    atol: 1.0e-12
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.case_id == "CASE_A"
    assert config.output == "results.npz"
    assert config.background.M == 1.0
    assert config.wave.kM == 0.5
    assert config.wave.A_plus == 0.9 + 1.1j
    assert config.wave.A_cross == 0.4 + 0.6j
    assert config.observer.kind == "angular"
    assert config.observer.r == 20.0
    assert config.observer.theta_values == (0.0, 0.2)
    assert config.observer.phi_values == (0.0,)
    assert config.numerics.lmax == 3
    assert config.numerics.boundary.r_out == 80.0
    assert config.numerics.boundary.required_eval_radius is None
    assert config.numerics.boundary.experimental_required_radius_oracle is None
    assert config.to_dict()["numerics"]["boundary"] == {
        "r_in_eps": 1.0e-6,
        "r_out": 80.0,
        "rtol": 1.0e-10,
        "atol": 1.0e-12,
        "outer_basis": "jost_1_over_r",
        "outer_series_order": 160,
    }
    assert config.convergence is None


def test_load_config_parses_optional_q018_boundary_fields(tmp_path):
    path = tmp_path / "case_q018_boundary.yaml"
    path.write_text(
        """
case_id: CASE_Q018_BOUNDARY
output: results.npz
background: {M: 1.0}
wave:
  kM: 2.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 60.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 180
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
    required_eval_radius: 60.0
    experimental_required_radius_oracle: q018_riccati
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.numerics.boundary.required_eval_radius == 60.0
    assert config.numerics.boundary.experimental_required_radius_oracle == "q018_riccati"
    assert config.to_dict()["numerics"]["boundary"] == {
        "r_in_eps": 1.0e-6,
        "r_out": 300.0,
        "rtol": 1.0e-10,
        "atol": 1.0e-12,
        "outer_basis": "jost_1_over_r",
        "outer_series_order": 160,
        "required_eval_radius": 60.0,
        "experimental_required_radius_oracle": "q018_riccati",
    }


def test_load_config_parses_generic_conditioning_backend(tmp_path):
    path = tmp_path / "case_conditioned_boundary.yaml"
    path.write_text(
        """
case_id: CASE_CONDITIONED_BOUNDARY
output: results.npz
background: {M: 1.0}
wave:
  kM: 2.0
  A_plus: {real: 1.0, imag: 0.0}
  A_cross: {real: 0.0, imag: 0.0}
observer: {r: 60.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 180
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
    required_eval_radius: 60.0
    conditioning_backend: scaled_log_riccati_auto
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.numerics.boundary.conditioning_backend == (
        "scaled_log_riccati_auto"
    )
    assert config.to_dict()["numerics"]["boundary"]["conditioning_backend"] == (
        "scaled_log_riccati_auto"
    )


@pytest.mark.parametrize(
    "extra, message",
    [
        ("conditioning_backend: unsupported", "conditioning_backend"),
        (
            "conditioning_backend: scaled_log_riccati_auto",
            "requires required_eval_radius",
        ),
    ],
)
def test_load_config_rejects_invalid_generic_conditioning_backend(
    tmp_path,
    extra,
    message,
):
    path = tmp_path / "case_invalid_conditioning.yaml"
    path.write_text(
        f"""
case_id: CASE_INVALID_CONDITIONING
output: results.npz
background: {{M: 1.0}}
wave:
  kM: 0.5
  A_plus: {{real: 1.0, imag: 0.0}}
  A_cross: {{real: 0.0, imag: 0.0}}
observer: {{r: 20.0, theta_values: [0.0], phi_values: [0.0]}}
numerics:
  lmax: 3
  boundary:
    r_in_eps: 1.0e-6
    r_out: 80.0
    rtol: 1.0e-10
    atol: 1.0e-12
    {extra}
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match=message):
        load_config(path)


def test_load_config_parses_explicit_outer_basis_and_observer_frame(tmp_path):
    path = tmp_path / "case_explicit_surfaces.yaml"
    path.write_text(
        """
case_id: CASE_EXPLICIT_SURFACES
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_values: [0.0]
  phi_values: [0.0]
  observer_frame: li_literal_cartesian
numerics:
  lmax: 3
  boundary:
    r_in_eps: 1.0e-6
    r_out: 80.0
    rtol: 1.0e-10
    atol: 1.0e-12
    outer_basis: plane_wave
    outer_series_order: 24
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.observer.observer_frame == "li_literal_cartesian"
    assert config.numerics.boundary.outer_basis == "plane_wave"
    assert config.numerics.boundary.outer_series_order == 24


def test_load_config_parses_optional_convergence_settings(tmp_path):
    path = tmp_path / "case_convergence.yaml"
    path.write_text(
        """
case_id: CASE_CONV
output: results.npz
background: {M: 1.0}
wave:
  kM: 1.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 60.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 4
  boundary: {r_in_eps: 1.0e-6, r_out: 120.0, rtol: 1.0e-9, atol: 1.0e-11}
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_values: [0.0, 0.05]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.convergence is not None
    assert config.convergence.enabled is True
    assert config.convergence.lmax_values == (2, 3, 4)
    assert config.convergence.theta_values == (0.0, 0.05)
    assert config.convergence.phi_values == (0.0,)
    assert config.convergence.selected_threshold == 1.0e-4
    assert config.convergence.near_axis_threshold == 1.0e-3


def test_load_config_parses_angular_observer_ranges_and_preserves_metadata(tmp_path):
    path = tmp_path / "case_angular_range.yaml"
    path.write_text(
        """
case_id: CASE_ANGULAR_RANGE
output: results.npz
background: {M: 1.0}
wave:
  kM: 1.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: angular
  r: 60.0
  theta_range: {start: 0.0, stop: 3.141592653589793, step: 1.5707963267948966, endpoint: true}
  phi_range: {start: 0.0, stop: 6.283185307179586, step: 1.5707963267948966, endpoint: false}
numerics:
  lmax: 4
  boundary: {r_in_eps: 1.0e-6, r_out: 120.0, rtol: 1.0e-9, atol: 1.0e-11}
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.observer.theta_values == (0.0, 1.5707963267948966, 3.141592653589793)
    assert config.observer.phi_values == (
        0.0,
        1.5707963267948966,
        3.141592653589793,
        4.71238898038469,
    )
    assert config.to_dict()["observer"] == {
        "observer_frame": "static_orthonormal",
        "r": 60.0,
        "theta_values": [0.0, 1.5707963267948966, 3.141592653589793],
        "phi_values": [
            0.0,
            1.5707963267948966,
            3.141592653589793,
            4.71238898038469,
        ],
        "theta_range": {
            "start": 0.0,
            "stop": 3.141592653589793,
            "step": 1.5707963267948966,
            "endpoint": True,
        },
        "phi_range": {
            "start": 0.0,
            "stop": 6.283185307179586,
            "step": 1.5707963267948966,
            "endpoint": False,
        },
    }


def test_load_config_parses_convergence_ranges_and_preserves_metadata(tmp_path):
    path = tmp_path / "case_convergence_range.yaml"
    path.write_text(
        """
case_id: CASE_CONV_RANGE
output: results.npz
background: {M: 1.0}
wave:
  kM: 1.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 60.0
  theta_values: [0.0]
  phi_values: [0.0]
numerics:
  lmax: 4
  boundary: {r_in_eps: 1.0e-6, r_out: 120.0, rtol: 1.0e-9, atol: 1.0e-11}
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_range: {start: 0.0, stop: 1.5707963267948966, step: 0.7853981633974483, endpoint: true}
  phi_range: {start: 0.0, stop: 6.283185307179586, step: 3.141592653589793, endpoint: false}
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.convergence is not None
    assert config.convergence.theta_values == (0.0, 0.7853981633974483, 1.5707963267948966)
    assert config.convergence.phi_values == (0.0, 3.141592653589793)
    assert config.to_dict()["convergence"]["theta_range"] == {
        "start": 0.0,
        "stop": 1.5707963267948966,
        "step": 0.7853981633974483,
        "endpoint": True,
    }
    assert config.to_dict()["convergence"]["phi_range"] == {
        "start": 0.0,
        "stop": 6.283185307179586,
        "step": 3.141592653589793,
        "endpoint": False,
    }


def test_load_config_parses_xz_plane_observer_and_masks_invalid_radii(tmp_path):
    path = tmp_path / "xz_case.yaml"
    path.write_text(
        """
case_id: CASE_XZ
output: results.npz
background: {M: 1.0}
wave:
  kM: 1.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_values: [-1.0, 0.0, 3.0]
  z_values: [0.0, 4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 3
  boundary: {r_in_eps: 1.0e-6, r_out: 20.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.observer.kind == "xz_plane"
    assert config.observer.r is None
    assert config.observer.x_values == (-1.0, 0.0, 3.0)
    assert config.observer.z_values == (0.0, 4.0)
    assert config.observer.invalid_radius_policy == "mask"
    assert config.to_dict()["observer"] == {
        "kind": "xz_plane",
        "observer_frame": "static_orthonormal",
        "x_values": [-1.0, 0.0, 3.0],
        "z_values": [0.0, 4.0],
        "invalid_radius_policy": "mask",
    }


def test_load_config_expands_xz_plane_ranges_with_endpoint(tmp_path):
    path = tmp_path / "xz_range_case.yaml"
    path.write_text(
        """
case_id: CASE_XZ_RANGE
output: results.npz
background: {M: 1.0}
wave:
  kM: 1.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_range: {start: -1.0, stop: 1.0, step: 0.5, endpoint: true}
  z_range: {start: 2.5, stop: 3.5, step: 0.5, endpoint: true}
  invalid_radius_policy: mask
numerics:
  lmax: 3
  boundary: {r_in_eps: 1.0e-6, r_out: 20.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.observer.kind == "xz_plane"
    assert config.observer.x_values == (-1.0, -0.5, 0.0, 0.5, 1.0)
    assert config.observer.z_values == (2.5, 3.0, 3.5)
    assert config.to_dict()["observer"] == {
        "kind": "xz_plane",
        "observer_frame": "static_orthonormal",
        "x_values": [-1.0, -0.5, 0.0, 0.5, 1.0],
        "z_values": [2.5, 3.0, 3.5],
        "invalid_radius_policy": "mask",
    }


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "wave.kM",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: bad, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "wave.A_plus.real",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "wave.kM must be positive",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 2.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.r must be greater than 2M",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 4
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
convergence:
  enabled: true
  lmax_values: [2, 2, 4]
  theta_values: [0.0]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
""",
            "convergence.lmax_values must be strictly increasing",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 5
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_values: [0.0]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
""",
            "numerics.lmax must equal convergence.lmax_values",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {kind: radial, r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.kind must be one of",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_values: [0.0, 1.0]
  z_values: [0.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer x-z grid must contain at least one valid point",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_values: [3.0]
  z_values: [4.0]
  invalid_radius_policy: fail
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.invalid_radius_policy must be 'mask'",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_values: [3.0]
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 5.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "numerics.boundary.r_out must be greater than the maximum valid x-z radius",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_values: [3.0]
  x_range: {start: -1.0, stop: 1.0, step: 0.5, endpoint: true}
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.x_values and observer.x_range are mutually exclusive",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_range: {start: -1.0, stop: 1.0, step: 0.0, endpoint: true}
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.x_range.step must be positive",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_range: {start: 1.0, stop: -1.0, step: 0.5, endpoint: true}
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.x_range.stop must be greater than start",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_range: {start: -1.0, stop: 1.0, step: 0.6, endpoint: true}
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.x_range must land exactly on stop when endpoint is true",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_range: {start: -1.0, stop: 1.0, step: 0.5, endpoint: false}
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.x_range.endpoint must be true",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_values: [0.0]
  theta_range: {start: 0.0, stop: 1.0, step: 0.5, endpoint: true}
  phi_values: [0.0]
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.theta_values and observer.theta_range are mutually exclusive",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  phi_values: [0.0]
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "Missing required field: observer.theta_values or observer.theta_range",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_range: {start: 0.0, stop: 1.0, step: -0.5, endpoint: true}
  phi_values: [0.0]
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.theta_range.step must be positive",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_range: {start: 0.0, stop: 0.0, step: 0.5, endpoint: false}
  phi_values: [0.0]
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.theta_range.stop must be greater than start",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_range: {start: 0.0, stop: 1.0, step: 0.6, endpoint: true}
  phi_values: [0.0]
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
            "observer.theta_range must land exactly on stop when endpoint is true",
        ),
        (
            """
case_id: CASE_A
output: results.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  r: 20.0
  theta_values: [0.0]
  phi_values: [0.0]
numerics:
  lmax: 4
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_values: [0.0]
  theta_range: {start: 0.0, stop: 1.0, step: 0.5, endpoint: true}
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
""",
            "convergence.theta_values and convergence.theta_range are mutually exclusive",
        ),
    ],
)
def test_load_config_reports_clear_validation_errors(tmp_path, yaml_text, message):
    path = tmp_path / "invalid.yaml"
    path.write_text(yaml_text, encoding="utf-8")

    with pytest.raises(ConfigError, match=message):
        load_config(path)
