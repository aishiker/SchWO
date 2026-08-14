from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.perturbations import Sector


@dataclass(frozen=True)
class OuterBasisState:
    """One finite-radius Jost/plane-wave basis state.

    ``sign=-1`` is incoming and ``sign=+1`` is outgoing for the project
    Fourier convention ``exp(-i k t)``.  ``series_residual`` is the local
    RW/Zerilli ODE residual normalized by the three terms in the equation.
    """

    psi: complex
    dpsi_dr: complex
    sign: int
    basis: str
    series_order: int
    series_residual: float
    tail_ratio: float


def outer_asymptotic_basis(
    *,
    sector: Sector | str,
    ell: int,
    r: float,
    k: float,
    background: StaticSphericalBackground,
    sign: int,
    basis: str = "jost_1_over_r",
    series_order: int = 160,
) -> OuterBasisState:
    """Return a controlled Schwarzschild outer basis at finite radius.

    The Jost form is

    ``exp(sign*i*k*r_star) * sum(a_n/r**n, n=0..N)``.

    Coefficients are generated directly from the RW/Zerilli equation rather
    than from a fitted phase correction.  The historical bare plane wave is
    retained only as an explicit diagnostic mode.
    """

    sector_enum = sector if isinstance(sector, Sector) else Sector(str(sector))
    if ell < 2:
        raise ValueError("Radiative RW/Zerilli modes require ell >= 2.")
    if sign not in {-1, 1}:
        raise ValueError("sign must be -1 (incoming) or +1 (outgoing).")
    if k <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if r <= background.horizon_radius:
        raise ValueError("Outer basis requires r > r_horizon.")
    if basis not in {"jost_1_over_r", "plane_wave"}:
        raise ValueError("unsupported outer basis")
    if (
        not isinstance(series_order, int)
        or isinstance(series_order, bool)
        or not 2 <= series_order <= 256
    ):
        raise ValueError("series_order must be an integer in [2, 256].")

    r_star = float(background.r_star(r))
    lapse = float(background.f(r))
    phase = complex(np.exp(sign * 1j * k * r_star))
    if basis == "plane_wave":
        return OuterBasisState(
            psi=phase,
            dpsi_dr=complex(sign * 1j * k * phase / lapse),
            sign=sign,
            basis=basis,
            series_order=0,
            series_residual=_basis_ode_residual(
                sector=sector_enum,
                ell=ell,
                r=r,
                k=k,
                background=background,
                sign=sign,
                terms=np.asarray([1.0 + 0.0j]),
            ),
            tail_ratio=0.0,
        )

    terms = _jost_terms(
        sector=sector_enum,
        ell=ell,
        k=k,
        mass=float(background.M),
        sign=sign,
        order=series_order,
        r=float(r),
    )
    series = complex(np.sum(terms))
    derivative_series = complex(-np.sum(np.arange(terms.size) * terms) / float(r))
    cancellation = float(np.sum(np.abs(terms)) / max(abs(series), np.finfo(float).eps))
    if cancellation > 1.0e8:
        series, derivative_series, second_series = _decimal_jost_sums(
            sector=sector_enum,
            ell=ell,
            k=k,
            mass=float(background.M),
            sign=sign,
            order=terms.size - 1,
            r=float(r),
        )
    else:
        indices = np.arange(terms.size, dtype=np.float64)
        second_series = complex(
            np.sum(indices * (indices + 1.0) * terms) / float(r) ** 2
        )
    psi = phase * series
    dpsi_dr = phase * (sign * 1j * k * series / lapse + derivative_series)
    denominator = max(abs(series), np.finfo(float).eps)
    tail_width = min(4, terms.size - 1)
    tail_ratio = float(np.sum(np.abs(terms[-tail_width:])) / denominator)
    return OuterBasisState(
        psi=complex(psi),
        dpsi_dr=complex(dpsi_dr),
        sign=sign,
        basis=basis,
        series_order=terms.size - 1,
        series_residual=_basis_ode_residual_from_sums(
            sector=sector_enum,
            ell=ell,
            r=r,
            k=k,
            background=background,
            sign=sign,
            series=series,
            first=derivative_series,
            second=second_series,
        ),
        tail_ratio=tail_ratio,
    )


def match_outer_asymptotic(
    *,
    psi: complex,
    dpsi_dr: complex,
    r: float,
    k: float,
    background: StaticSphericalBackground,
    sector: Sector | str | None = None,
    ell: int | None = None,
    basis: str = "plane_wave",
    series_order: int = 160,
) -> tuple[complex, complex, float, float]:
    """Match a radial state to incoming/outgoing finite-radius bases.

    Callers selecting ``jost_1_over_r`` must provide ``sector`` and ``ell``.
    The explicit default ``plane_wave`` preserves the old low-level API; all
    production radial-solver paths pass their configured basis explicitly.
    """
    if k <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if r <= background.horizon_radius:
        raise ValueError("Outer matching requires r > r_horizon.")

    if basis == "jost_1_over_r" and (sector is None or ell is None):
        raise ValueError("Jost matching requires sector and ell.")
    if basis == "jost_1_over_r":
        incoming = outer_asymptotic_basis(
            sector=sector,
            ell=int(ell),
            r=r,
            k=k,
            background=background,
            sign=-1,
            basis=basis,
            series_order=series_order,
        )
        outgoing = outer_asymptotic_basis(
            sector=sector,
            ell=int(ell),
            r=r,
            k=k,
            background=background,
            sign=1,
            basis=basis,
            series_order=series_order,
        )
    else:
        # The sector/ell values are irrelevant for the plane-wave state, but
        # provide a valid radiative pair so the shared helper can report its
        # local residual.
        incoming = outer_asymptotic_basis(
            sector=Sector.ODD if sector is None else sector,
            ell=2 if ell is None else int(ell),
            r=r,
            k=k,
            background=background,
            sign=-1,
            basis=basis,
            series_order=series_order,
        )
        outgoing = outer_asymptotic_basis(
            sector=Sector.ODD if sector is None else sector,
            ell=2 if ell is None else int(ell),
            r=r,
            k=k,
            background=background,
            sign=1,
            basis=basis,
            series_order=series_order,
        )
    matrix = np.array(
        [
            [incoming.psi, outgoing.psi],
            [incoming.dpsi_dr, outgoing.dpsi_dr],
        ],
        dtype=complex,
    )
    rhs = np.array([psi, dpsi_dr], dtype=complex)
    A_in, A_out = np.linalg.solve(matrix, rhs)
    reconstructed = matrix @ np.array([A_in, A_out], dtype=complex)
    denominator = max(float(np.linalg.norm(rhs)), np.finfo(float).eps)
    residual = float(np.linalg.norm(reconstructed - rhs) / denominator)
    condition_number = float(np.linalg.cond(matrix))
    return complex(A_in), complex(A_out), residual, condition_number


def _jost_terms(
    *,
    sector: Sector,
    ell: int,
    k: float,
    mass: float,
    sign: int,
    order: int,
    r: float,
) -> np.ndarray:
    """Generate scaled Jost terms ``a_n/r**n`` without coefficient overflow."""

    potential = _potential_series(sector=sector, ell=ell, mass=mass, order=order + 2)
    f_squared = np.asarray([1.0, -4.0 * mass, 4.0 * mass**2], dtype=np.complex128)
    ff_prime_plus_phase = np.zeros(order + 3, dtype=np.complex128)
    ff_prime_plus_phase[0] = 2.0j * sign * k
    ff_prime_plus_phase[1] = -4.0j * sign * k * mass
    ff_prime_plus_phase[2] = 2.0 * mass
    ff_prime_plus_phase[3] = -4.0 * mass**2
    terms = np.zeros(order + 1, dtype=np.complex128)
    terms[0] = 1.0 + 0.0j
    decreasing_run = 0
    increasing_run = 0
    optimal_index: int | None = None
    for index in range(1, order + 1):
        power = index + 1
        known = 0.0j
        for offset, coefficient in enumerate(f_squared):
            source = power - offset - 2
            if 0 <= source < index:
                known += (
                    coefficient
                    * source
                    * (source + 1)
                    * terms[source]
                    * r ** (source - index)
                )
        for offset, coefficient in enumerate(ff_prime_plus_phase):
            source = power - offset - 1
            if 0 <= source < index:
                known += (
                    coefficient
                    * (-source)
                    * terms[source]
                    * r ** (source - index)
                )
        for offset in range(2, min(power, potential.size - 1) + 1):
            source = power - offset
            if 0 <= source < index:
                known -= potential[offset] * terms[source] * r ** (source - index)
        pivot = -2.0j * sign * k * index
        terms[index] = -known / pivot
        if abs(terms[index]) < abs(terms[index - 1]):
            decreasing_run += 1
            increasing_run = 0
            optimal_index = None
        else:
            if increasing_run == 0 and decreasing_run >= 8:
                optimal_index = index - 1
            increasing_run += 1
            decreasing_run = 0
        if increasing_run >= 4 and optimal_index is not None:
            terms = terms[: optimal_index + 1]
            break
        if (
            index >= 16
            and index + 1 < order
            and max(abs(value) for value in terms[index - 3 : index + 1]) < 1.0e-18
            and all(
                abs(terms[position]) <= abs(terms[position - 1])
                for position in range(index - 3, index + 1)
            )
        ):
            terms = terms[: index + 1]
            break
    if not np.all(np.isfinite(terms)):
        raise RuntimeError("Jost term recurrence produced non-finite values.")
    return terms


def _potential_series(
    *, sector: Sector, ell: int, mass: float, order: int
) -> np.ndarray:
    values = np.zeros(order + 1, dtype=np.complex128)
    angular = float(ell * (ell + 1))
    if sector is Sector.ODD:
        values[2] = angular
        if order >= 3:
            values[3] = -2.0 * mass * angular - 6.0 * mass
        if order >= 4:
            values[4] = 12.0 * mass**2
        return values

    lambda_ = 0.5 * (ell - 1) * (ell + 2)
    bracket = np.zeros(order + 1, dtype=np.complex128)
    bracket[0] = 2.0 * lambda_**2 * (lambda_ + 1.0)
    if order >= 1:
        bracket[1] = 6.0 * lambda_**2 * mass
    if order >= 2:
        bracket[2] = 18.0 * lambda_ * mass**2
    if order >= 3:
        bracket[3] = 18.0 * mass**3
    inverse_square = np.asarray(
        [
            ((-1) ** index)
            * (index + 1)
            * (3.0 * mass / lambda_) ** index
            / lambda_**2
            for index in range(order + 1)
        ],
        dtype=np.complex128,
    )
    quotient = np.convolve(bracket, inverse_square)[: order + 1]
    lapse_times = np.convolve(
        np.asarray([1.0, -2.0 * mass], dtype=np.complex128), quotient
    )[: order - 1]
    values[2 : 2 + lapse_times.size] = lapse_times[: values.size - 2]
    return values


def _basis_ode_residual(
    *,
    sector: Sector,
    ell: int,
    r: float,
    k: float,
    background: StaticSphericalBackground,
    sign: int,
    terms: np.ndarray,
) -> float:
    indices = np.arange(terms.size, dtype=np.float64)
    series = complex(np.sum(terms))
    first = complex(-np.sum(indices * terms) / float(r))
    second = complex(
        np.sum(indices * (indices + 1.0) * terms) / float(r) ** 2
    )
    return _basis_ode_residual_from_sums(
        sector=sector,
        ell=ell,
        r=r,
        k=k,
        background=background,
        sign=sign,
        series=series,
        first=first,
        second=second,
    )


def _basis_ode_residual_from_sums(
    *,
    sector: Sector,
    ell: int,
    r: float,
    k: float,
    background: StaticSphericalBackground,
    sign: int,
    series: complex,
    first: complex,
    second: complex,
) -> float:
    lapse = float(background.f(r))
    lapse_prime = float(background.df_dr(r))
    if sector is Sector.ODD:
        potential = lapse / r**2 * (ell * (ell + 1) - 6.0 * float(background.M) / r)
    else:
        lambda_ = 0.5 * (ell - 1) * (ell + 2)
        mu = float(background.M) / r
        potential = (
            lapse
            / r**2
            * (
                2.0 * lambda_**2 * (lambda_ + 1.0)
                + 6.0 * lambda_**2 * mu
                + 18.0 * lambda_ * mu**2
                + 18.0 * mu**3
            )
            / (lambda_ + 3.0 * mu) ** 2
        )
    residual = (
        lapse**2 * second
        + lapse * (lapse_prime + 2.0j * sign * k) * first
        - potential * series
    )
    scale = (
        abs(lapse**2 * second)
        + abs(lapse * (lapse_prime + 2.0j * sign * k) * first)
        + abs(potential * series)
        + np.finfo(float).eps
    )
    return float(abs(residual) / scale)


def _decimal_jost_sums(
    *,
    sector: Sector,
    ell: int,
    k: float,
    mass: float,
    sign: int,
    order: int,
    r: float,
) -> tuple[complex, complex, complex]:
    """Evaluate a cancellation-prone Jost series with stdlib decimal.

    The fallback keeps the default radial solver dependency-free while
    retaining enough precision for the high-ell, finite-r_out regime where
    individual asymptotic terms can exceed the final sum by many orders.
    """

    from decimal import Decimal, localcontext

    ComplexDecimal = tuple[Decimal, Decimal]

    def add(left: ComplexDecimal, right: ComplexDecimal) -> ComplexDecimal:
        return left[0] + right[0], left[1] + right[1]

    def multiply(left: ComplexDecimal, right: ComplexDecimal) -> ComplexDecimal:
        return (
            left[0] * right[0] - left[1] * right[1],
            left[0] * right[1] + left[1] * right[0],
        )

    with localcontext() as context:
        context.prec = 80
        zero = Decimal(0)
        one = Decimal(1)
        radius = Decimal(str(r))
        mass_d = Decimal(str(mass))
        k_d = Decimal(str(k))
        inverse_powers = [one]
        for _ in range(order):
            inverse_powers.append(inverse_powers[-1] / radius)
        f_squared = (one, -4 * mass_d, 4 * mass_d * mass_d)
        g: tuple[ComplexDecimal, ...] = (
            (zero, 2 * Decimal(sign) * k_d),
            (zero, -4 * Decimal(sign) * k_d * mass_d),
            (2 * mass_d, zero),
            (-4 * mass_d * mass_d, zero),
        )
        potential = _decimal_potential_series(
            sector=sector,
            ell=ell,
            mass=mass_d,
            order=order + 2,
        )
        terms: list[ComplexDecimal] = [(one, zero)]
        for index in range(1, order + 1):
            power = index + 1
            known: ComplexDecimal = (zero, zero)
            for offset, coefficient in enumerate(f_squared):
                source = power - offset - 2
                if 0 <= source < index:
                    scale = (
                        coefficient
                        * Decimal(source * (source + 1))
                        * inverse_powers[index - source]
                    )
                    known = add(known, (terms[source][0] * scale, terms[source][1] * scale))
            for offset, coefficient in enumerate(g):
                source = power - offset - 1
                if 0 <= source < index:
                    scale = -Decimal(source) * inverse_powers[index - source]
                    known = add(
                        known,
                        multiply(coefficient, (terms[source][0] * scale, terms[source][1] * scale)),
                    )
            for offset in range(2, min(power, len(potential) - 1) + 1):
                source = power - offset
                if 0 <= source < index:
                    scale = -potential[offset] * inverse_powers[index - source]
                    known = add(known, (terms[source][0] * scale, terms[source][1] * scale))
            pivot = -2 * Decimal(sign) * k_d * Decimal(index)
            terms.append((-known[1] / pivot, known[0] / pivot))
        series_real = sum((value[0] for value in terms), zero)
        series_imag = sum((value[1] for value in terms), zero)
        first_real = -sum(
            (Decimal(index) * value[0] for index, value in enumerate(terms)), zero
        ) / radius
        first_imag = -sum(
            (Decimal(index) * value[1] for index, value in enumerate(terms)), zero
        ) / radius
        second_real = sum(
            (
                Decimal(index * (index + 1)) * value[0]
                for index, value in enumerate(terms)
            ),
            zero,
        ) / radius**2
        second_imag = sum(
            (
                Decimal(index * (index + 1)) * value[1]
                for index, value in enumerate(terms)
            ),
            zero,
        ) / radius**2
        return (
            complex(float(series_real), float(series_imag)),
            complex(float(first_real), float(first_imag)),
            complex(float(second_real), float(second_imag)),
        )


def _decimal_potential_series(*, sector: Sector, ell: int, mass, order: int):
    from decimal import Decimal

    zero = Decimal(0)
    values = [zero for _ in range(order + 1)]
    angular = Decimal(ell * (ell + 1))
    if sector is Sector.ODD:
        values[2] = angular
        if order >= 3:
            values[3] = -2 * mass * angular - 6 * mass
        if order >= 4:
            values[4] = 12 * mass * mass
        return values
    lambda_ = Decimal((ell - 1) * (ell + 2)) / 2
    bracket = [zero for _ in range(order + 1)]
    bracket[0] = 2 * lambda_**2 * (lambda_ + 1)
    if order >= 1:
        bracket[1] = 6 * lambda_**2 * mass
    if order >= 2:
        bracket[2] = 18 * lambda_ * mass**2
    if order >= 3:
        bracket[3] = 18 * mass**3
    inverse = [
        Decimal((-1) ** index)
        * Decimal(index + 1)
        * (3 * mass / lambda_) ** index
        / lambda_**2
        for index in range(order + 1)
    ]
    quotient = [zero for _ in range(order + 1)]
    for left, left_value in enumerate(bracket):
        if left_value == 0:
            continue
        for right, right_value in enumerate(inverse[: order + 1 - left]):
            quotient[left + right] += left_value * right_value
    for index in range(order - 1):
        values[index + 2] += quotient[index]
        if index + 3 <= order:
            values[index + 3] -= 2 * mass * quotient[index]
    return values


__all__ = ["OuterBasisState", "match_outer_asymptotic", "outer_asymptotic_basis"]
