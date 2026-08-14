from __future__ import annotations

import numpy as np
import pytest

from schwgw.validation.phase6_polarization_transfer import (
    AbsolutePhaseConvention,
    linear_to_helicity_transform,
    polarization_basis_rotation,
    polarization_transfer_from_columns,
    rotate_polarization_transfer,
)


def test_columns_form_the_full_complex_transfer_matrix() -> None:
    phase = AbsolutePhaseConvention()
    transfer = polarization_transfer_from_columns(
        [2.0 + 1.0j, 0.3 - 0.2j],
        [-0.4j, 1.5 + 0.7j],
        field_definition="scattered",
        phase_convention=phase,
    )
    np.testing.assert_array_equal(
        transfer.matrix,
        np.array([[2.0 + 1.0j, -0.4j], [0.3 - 0.2j, 1.5 + 0.7j]]),
    )
    assert transfer.matrix.flags.writeable is False
    assert transfer.trace_fdagger_f == pytest.approx(
        float(np.sum(np.abs(transfer.matrix) ** 2))
    )
    assert len(phase.sha256()) == 64
    assert "per artifact" not in phase.coulomb_subtraction
    assert transfer.incident_basis_angle_rad == 0.0
    assert transfer.observer_basis_angle_rad == 0.0


def test_basis_covariance_preserves_singular_values_and_total_power() -> None:
    transfer = polarization_transfer_from_columns(
        [1.0 + 0.3j, -0.2 + 0.1j],
        [0.4 - 0.5j, 2.0 + 0.2j],
        field_definition="total",
        phase_convention=AbsolutePhaseConvention(),
    )
    rotated = rotate_polarization_transfer(
        transfer,
        incident_basis_angle=0.23,
        observer_basis_angle=-0.41,
    )
    np.testing.assert_allclose(
        rotated.singular_values, transfer.singular_values, atol=2e-15
    )
    assert rotated.trace_fdagger_f == pytest.approx(transfer.trace_fdagger_f)
    assert abs(rotated.determinant) == pytest.approx(abs(transfer.determinant))
    assert rotated.incident_basis_label == transfer.incident_basis_label
    assert rotated.observer_basis_label == transfer.observer_basis_label
    assert rotated.incident_basis_angle_rad == pytest.approx(0.23)
    assert rotated.observer_basis_angle_rad == pytest.approx(-0.41)


def test_rotation_and_helicity_conventions_are_explicit() -> None:
    rotation = polarization_basis_rotation(np.pi / 4.0)
    np.testing.assert_allclose(rotation @ np.array([1.0, 0.0]), [0.0, -1.0], atol=1e-15)
    transform = linear_to_helicity_transform()
    np.testing.assert_allclose(transform @ transform.conj().T, np.eye(2), atol=2e-15)


def test_diagonal_helicity_response_has_zero_mixing() -> None:
    transform = linear_to_helicity_transform()
    desired_helicity = np.diag([2.0 + 0.1j, 0.5 - 0.2j])
    linear = transform.conj().T @ desired_helicity @ transform
    transfer = polarization_transfer_from_columns(
        linear[:, 0],
        linear[:, 1],
        field_definition="scattered",
        phase_convention=AbsolutePhaseConvention(),
    )
    assert transfer.helicity_mixing_power == pytest.approx(0.0, abs=2e-30)


def test_total_and_scattered_definitions_cannot_be_implicit() -> None:
    with pytest.raises(ValueError, match="total or scattered"):
        polarization_transfer_from_columns(
            [1.0, 0.0],
            [0.0, 1.0],
            field_definition="unspecified",
            phase_convention=AbsolutePhaseConvention(),
        )


def test_absolute_phase_convention_rejects_placeholders() -> None:
    with pytest.raises(ValueError, match="not frozen"):
        AbsolutePhaseConvention(coulomb_subtraction="explicitly recorded per artifact")
