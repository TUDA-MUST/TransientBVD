"""
TransientBVD - Open Circuit Transient Analysis

This module provides functions for analyzing the transient response of resonant circuits
modeled by the Butterworth-Van Dyke (BVD) equivalent circuit in an open-circuit scenario.

It includes methods for evaluating decay times, optimizing parallel resistance for damping,
and computing transient currents using the system's characteristic polynomial.
"""
import cmath
import logging
from typing import Optional
from typing import Tuple

import numpy as np
from scipy.optimize import minimize_scalar

from .transducer import Transducer
from .utils import roots


def print_open_potential(
    transducer: Transducer,
    resistance_range: Tuple[float, float] = (10, 5000)
) -> None:
    """
    Display the results of `open_potential`, including decay times and speed improvement.

    This function evaluates how the transient response improves when introducing an
    optimal parallel resistance (Rp). It prints decay times with and without Rp, as well
    as the absolute and percentage improvements.

    Parameters
    ----------
    transducer : Transducer
        The transducer object containing the necessary circuit parameters.
    resistance_range : Tuple[float, float], optional
        The range of resistance values (in ohms) to evaluate for optimal damping.
        Default is (10, 5000) Ω.
    """
    # Evaluate the open_potential
    optimal_resistance, tau_with_rp, delta_time, percentage_improvement = open_potential(
        transducer, resistance_range
    )

    # Extract circuit parameters directly from the Transducer object
    rs, ls = transducer.rs, transducer.ls

    # Calculate decay times without using Rp
    tau_no_rp = 2 * ls / rs
    two_tau_no_rp = 2 * tau_no_rp

    # Calculate 2τ for Rp
    two_tau_with_rp = 2 * tau_with_rp

    # Calculate speed improvement factor
    speed_improvement = tau_no_rp / tau_with_rp if tau_with_rp > 0 else float("inf")

    # Pretty print the results
    print("=" * 50)
    print("Open Potential Analysis")
    print("=" * 50)

    # Use the pretty_print method from Transducer (inherits from EquivalentCircuitParams)
    print(transducer)

    print(f"Optimal Parallel Resistance (Rp): {optimal_resistance:.2f} Ω")
    print(f"Decay Time (τ) without Rp: {tau_no_rp:.6f} s ({tau_no_rp * 1e3:.2f} ms)")
    print(f"Decay Time (τ) with Rp: {tau_with_rp:.6f} s ({tau_with_rp * 1e3:.2f} ms)")
    print(f"2τ without Rp: {two_tau_no_rp:.6f} s ({two_tau_no_rp * 1e3:.2f} ms)")
    print(f"2τ with Rp: {two_tau_with_rp:.6f} s ({two_tau_with_rp * 1e3:.2f} ms)")
    print(f"Absolute Time Improvement: {delta_time:.6f} s ({delta_time * 1e3:.2f} ms)")
    print(f"Percentage Time Improvement: {percentage_improvement:.2f}%")
    print(f"Speed Improvement Factor: {speed_improvement:.2f}x")
    print("=" * 50)


def open_potential(
    transducer: Transducer,
    resistance_range: Tuple[float, float] = (10, 5000)
) -> Tuple[float, float, float, float]:
    r"""
    Evaluate the improvement in transient decay time when using the optimal parallel resistance
    versus not using a parallel resistance in an open-circuit scenario.

    The method calculates the decay time for two cases:
    1. With the optimal parallel resistance, where the time constant is determined
       by the eigenvalues of the characteristic polynomial.
    2. Without a parallel resistance, where the time constant is approximated as:

    .. math::

        \tau = \frac{2L}{R},

    where :math:`L` is the inductance and :math:`R` is the series resistance.

    The improvement is expressed as the absolute difference in decay time
    and the percentage reduction.

    Parameters
    ----------
    transducer : Transducer
        A transducer object containing the necessary circuit parameters.
    resistance_range : Tuple[float, float], optional
        A tuple representing the lower and upper bounds of resistances (in ohms) to evaluate
        for damping optimization. Default is (10, 5000).

    Returns
    -------
    Tuple[float, float, float, float]
        A tuple containing:
        - The optimal resistance value (in ohms).
        - The optimized minimal decay time (in seconds).
        - The absolute improvement in decay time (in seconds).
        - The percentage improvement in decay time (%).

    Notes
    -----
    The method assumes that the system can be represented by the BVD equivalent circuit and
    that the transient response is governed by the resistive, capacitive, and inductive components.
    """
    # Extract parameters from transducer
    rs, ls, cs, c0 = transducer.rs, transducer.ls, transducer.cs, transducer.c0

    # Validate input parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if resistance_range[0] <= 0 or resistance_range[1] <= 0:
        raise ValueError("Resistance range bounds must contain positive values.")
    if resistance_range[0] >= resistance_range[1]:
        raise ValueError("Resistance range lower bound must be less than the upper bound.")

    # Calculate the decay time without using rp (τ = 2L / R)
    tau_no_rp = 2 * ls / rs

    # Calculate the optimal resistance and its corresponding decay time
    optimal_resistance, tau_with_rp = optimum_resistance(transducer, resistance_range)

    # Compute the absolute and percentage improvements
    delta_time = tau_no_rp - tau_with_rp
    percentage_improvement = (delta_time / tau_no_rp) * 100 if tau_no_rp > 0 else 0.0

    return optimal_resistance, tau_with_rp, delta_time, percentage_improvement


def open_tau(
    transducer: Transducer,
    rp: Optional[float] = None
) -> float:
    """
    Calculate the decay time (τ) for a given transducer with an optional parallel resistance (rp).

    Parameters
    ----------
    transducer : Transducer
        The transducer object containing the necessary circuit parameters.
    rp : Optional[float], default=None
        Parallel resistance in ohms. If None, decay time is calculated without rp.

    Returns
    -------
    float
        Decay time (τ) in seconds.

    Raises
    ------
    ValueError
        If any transducer parameter (rs, ls, cs, c0) is not positive or if rp is non-positive.

    Notes
    -----
    - When `rp` is not provided, the decay time is calculated using the formula:
      τ = 2 * ls / rs (approximating an open circuit).
    - When `rp` is provided, the decay time is determined using the eigenvalues of
      the characteristic polynomial.
    """
    # Validate input parameters
    if transducer.rs <= 0 or transducer.ls <= 0 or transducer.cs <= 0 or transducer.c0 <= 0:
        raise ValueError("All transducer parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("rp must be positive if provided.")

    if rp is None:
        # Calculate the decay time without using rp (τ = 2L / R)
        return 2 * transducer.ls / transducer.rs

    # Calculate the decay time using rp and the eigenvalues
    calculated_roots = roots(
        transducer.rs, transducer.ls, transducer.cs, transducer.c0, rp=rp
    )
    second_root = calculated_roots[1]
    decay_rate = abs(second_root.real)
    return 1 / decay_rate if decay_rate > 0 else float("inf")


def open_two_tau(
    transducer: Transducer,
    rp: Optional[float] = None
) -> float:
    """
    Calculate twice the decay time (2τ) for a given transducer with an
    optional parallel resistance (rp).

    Parameters
    ----------
    transducer : Transducer
        The transducer object containing the necessary circuit parameters.
    rp : Optional[float], default=None
        Parallel resistance in ohms. If None, decay time is calculated without rp.

    Returns
    -------
    float
        Twice the decay time (2τ) in seconds.

    Raises
    ------
    ValueError
        If any transducer parameter (rs, ls, cs, c0) is not positive or if rp is non-positive.

    Notes
    -----
    - When `rp` is not provided, the decay time is calculated using the formula:
      2τ = 4 * ls / rs (approximating an open circuit).
    - When `rp` is provided, the decay time is determined using the eigenvalues of
      the characteristic polynomial.
    """
    return 2 * open_tau(transducer, rp)


def optimum_resistance(
    transducer: Transducer,
    resistance_range: Tuple[float, float] = (10, 10_000)
) -> Tuple[float, float]:
    """
    Calculate the optimal parallel resistance (highest damping)
    for the transient response in a transducer modeled by the
    Butterworth-Van Dyke (BVD) equivalent circuit using numerical optimization.

    Parameters
    ----------
    transducer : Transducer
        The transducer object containing the necessary circuit parameters.
    resistance_range : Tuple[float, float], default=(10, 10_000)
        A tuple representing the lower and upper bounds for resistance (in ohms) to evaluate.

    Returns
    -------
    Tuple[float, float]
        A tuple containing:
        - The optimal resistance value in ohms that minimizes the decay time.
        - The corresponding decay time in seconds.

    Raises
    ------
    ValueError
        If any transducer parameter (rs, ls, cs, c0) is not positive
        or if resistance bounds are invalid.
    """
    # Validate input parameters
    if transducer.rs <= 0 or transducer.ls <= 0 or transducer.cs <= 0 or transducer.c0 <= 0:
        raise ValueError("All transducer parameters (rs, ls, cs, c0) must be positive.")

    if resistance_range[0] <= 0 or resistance_range[1] <= 0:
        raise ValueError("Resistance bounds must be positive.")
    if resistance_range[0] >= resistance_range[1]:
        raise ValueError("Resistance range must have a lower bound less than the upper bound.")

    def decay_time_wrapper(rp: float) -> float:
        """
        Wrapper for decay_time to match the signature for optimization.
        """
        return open_tau(transducer, rp=rp)

    # Perform numerical optimization to find the resistance that minimizes decay time
    result = minimize_scalar(
        decay_time_wrapper,
        bounds=resistance_range,
        method="bounded"  # Use bounded optimization since we have a range
    )

    # Extract optimal resistance and corresponding decay time
    optimal_resistance = result.x
    minimal_decay_time = result.fun

    # Check if the optimal resistance is near the bounds
    lower_bound, upper_bound = resistance_range
    tolerance = 0.01 * (upper_bound - lower_bound)  # 1% of the range
    if abs(optimal_resistance - lower_bound) < tolerance:
        logging.warning(
            "Hint: The optimal resistance (%.2f Ω) is near the lower bound of the range. "
            "Consider reducing the lower bound.", optimal_resistance
        )
    elif abs(optimal_resistance - upper_bound) < tolerance:
        logging.warning(
            "Hint: The optimal resistance (%.2f Ω) is near the upper bound of the range. "
            "Consider increasing the upper bound.", optimal_resistance
        )

    return optimal_resistance, minimal_decay_time


def open_current(
    t: float,
    i0: float,
    transducer: Transducer,
    rp: Optional[float] = None
) -> float:
    r"""
    Calculate the transient current \( i(t) \) for an open-circuit BVD model (3rd order),
    assuming initial conditions:
      \( i(0) = i_0 \), \( i'(0) = 0 \), \( i''(0) = 0 \).

    The system's eigenvalues are taken from ``roots(...)``. For a 3rd-order polynomial
    (e.g., including parallel capacitance and optional parallel resistor), we get
    three eigenvalues \( \lambda_1, \lambda_2, \lambda_3 \). The solution is:

    .. math::

       i(t) = A\, e^{\lambda_1 t} + B\, e^{\lambda_2 t} + C\, e^{\lambda_3 t},

    where \( A, B, C \) are determined from the initial conditions.

    Parameters
    ----------
    t : float
        Time in seconds at which to evaluate \( i(t) \).
    i0 : float
        Initial current in amperes (\( i(0) = i_0 \)).
    transducer : Transducer
        The transducer object containing the equivalent circuit parameters.
    rp : Optional[float], default=None
        Parallel resistance in ohms. If None, uses `transducer.rp`.

    Returns
    -------
    float
        The real part of \( i(t) \) under these assumptions.

    Notes
    -----
    - If the system ends up with repeated roots or is effectively 2nd order, special cases
      may need to be handled separately.
    - Uses `transducer.rp` by default unless a different `rp` is explicitly provided.
    """
    # Use transducer's rp if not explicitly provided
    rp = transducer.rp if rp is None else rp

    # Compute eigenvalues (roots of the characteristic equation)
    lam1_c, lam2_c, lam3_c = map(complex, roots(transducer, rp=rp))

    # Solve the 3x3 system for coefficients A, B, C
    solution_abc = np.linalg.solve(
        np.array([
            [1.0, 1.0, 1.0],
            [lam1_c, lam2_c, lam3_c],
            [lam1_c**2, lam2_c**2, lam3_c**2]
        ], dtype=complex),
        np.array([i0, 0.0, 0.0], dtype=complex)
    )

    # Compute i(t) = A e^(λ1 t) + B e^(λ2 t) + C e^(λ3 t)
    i_t = sum(
        coef * cmath.exp(lam * t)
        for coef, lam in zip(solution_abc, (lam1_c, lam2_c, lam3_c))
    )

    return i_t.real  # Return only the real part
