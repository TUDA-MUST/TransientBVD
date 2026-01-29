"""
TransientBVD - Deactivation Transient Analysis

This module provides functions for analyzing the transient response of resonant circuits
modeled by the Butterworth-Van Dyke (BVD) equivalent circuit in a deactivation scenario.

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


def print_deactivation_potential(
    transducer: Transducer, resistance_range: Tuple[float, float] = (10, 5000)
) -> None:
    """
    Display the results of `deactivation_potential`, including decay times and speed improvement.

    This function evaluates how the deactivation transient response improves when introducing an
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
    # Evaluate the deactivation potential
    optimal_resistance, tau_with_rp, delta_time, percentage_improvement = (
        deactivation_potential(transducer, resistance_range)
    )

    # Extract circuit parameters directly from the Transducer object
    rs, ls = transducer.rs, transducer.ls

    # Calculate decay times without using Rp
    tau_no_rp = 2 * ls / rs
    two_tau_no_rp = 2 * tau_no_rp

    # Calculate 2τ for Rp
    two_tau_with_rp = 2 * tau_with_rp

    # Pretty print the results
    print("=" * 50)
    print("Deactivation Potential Analysis")
    print("=" * 50)

    print(transducer)

    print(f"Optimal Parallel Resistance (Rp): {optimal_resistance:.2f} Ω")
    print(f"Decay Time (τ) without Rp: {tau_no_rp:.6f} s ({tau_no_rp * 1e3:.2f} ms)")
    print(f"Decay Time (τ) with Rp: {tau_with_rp:.6f} s ({tau_with_rp * 1e3:.2f} ms)")
    print(f"2τ without Rp: {two_tau_no_rp:.6f} s ({two_tau_no_rp * 1e3:.2f} ms)")
    print(f"2τ with Rp: {two_tau_with_rp:.6f} s ({two_tau_with_rp * 1e3:.2f} ms)")
    print(f"Absolute Time Improvement: {delta_time:.6f} s ({delta_time * 1e3:.2f} ms)")
    print(f"Percentage Time Improvement: {percentage_improvement:.2f}%")
    print("=" * 50)


def deactivation_potential(
    transducer: Transducer, resistance_range: Tuple[float, float] = (10, 5000)
) -> Tuple[float, float, float, float]:
    r"""
    Evaluate the improvement in transient decay time when using the optimal parallel resistance
    versus not using a parallel resistance in a deactivation scenario.

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
        raise ValueError(
            "Resistance range lower bound must be less than the upper bound."
        )

    # Calculate the decay time without using rp (τ = 2L / R)
    tau_no_rp = 2 * ls / rs

    # Calculate the optimal resistance and its corresponding decay time
    optimal_resistance, tau_with_rp = optimum_resistance(transducer, resistance_range)

    # Compute the absolute and percentage improvements
    delta_time = tau_no_rp - tau_with_rp
    percentage_improvement = (delta_time / tau_no_rp) * 100 if tau_no_rp > 0 else 0.0

    return optimal_resistance, tau_with_rp, delta_time, percentage_improvement


def deactivation_tau(transducer: Transducer, rp: Optional[float] = None) -> float:
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
      τ = 2 * ls / rs (approximating the deactivation condition).
    - When `rp` is provided, the decay time is determined using the eigenvalues of
      the characteristic polynomial.
    """
    # Validate input parameters
    if (
        transducer.rs <= 0
        or transducer.ls <= 0
        or transducer.cs <= 0
        or transducer.c0 <= 0
    ):
        raise ValueError("All transducer parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("rp must be positive if provided.")

    if rp is None:
        # Calculate the decay time without using rp (τ = 2L / R)
        return 2 * transducer.ls / transducer.rs

    calculated_roots = roots(
        transducer.rs, transducer.ls, transducer.cs, transducer.c0, rp=rp
    )

    # If any root is unstable, fail loudly
    for r in calculated_roots:
        if complex(r).real > 1e-12:
            raise ValueError(f"Unstable system: eigenvalue {r} has positive real part.")

    # Exclude the near-zero open-circuit mode from tau selection
    nonzero_roots = [
        complex(r) for r in calculated_roots if abs(complex(r).real) > 1e-9
    ]

    # If only the ~0 mode exists, the decay time is effectively infinite
    if not nonzero_roots:
        return float("inf")

    # Slowest decay mode = real part closest to 0 (still negative)
    dominant = max(nonzero_roots, key=lambda z: z.real)
    decay_rate = -dominant.real

    return 1 / decay_rate


def deactivation_two_tau(transducer: Transducer, rp: Optional[float] = None) -> float:
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
      2τ = 4 * ls / rs (approximating the deactivation condition).
    - When `rp` is provided, the decay time is determined using the eigenvalues of
      the characteristic polynomial.
    """
    return 2 * deactivation_tau(transducer, rp)


def optimum_resistance(
    transducer: Transducer, resistance_range: Tuple[float, float] = (10, 10_000)
) -> Tuple[float, float]:
    """
    Calculate the optimal parallel resistance (highest damping)
    for the transient response in a transducer modeled by the
    Butterworth-Van Dyke (BVD) equivalent circuit using numerical optimization.

    Parameters
    ----------
    transducer : Transducer
        The transducer object containing the necessary circuit parameters.
    resistance_range : Tuple[float, float], default=(10, 10,000)
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
    if (
        transducer.rs <= 0
        or transducer.ls <= 0
        or transducer.cs <= 0
        or transducer.c0 <= 0
    ):
        raise ValueError("All transducer parameters (rs, ls, cs, c0) must be positive.")

    if resistance_range[0] <= 0 or resistance_range[1] <= 0:
        raise ValueError("Resistance bounds must be positive.")
    if resistance_range[0] >= resistance_range[1]:
        raise ValueError(
            "Resistance range must have a lower bound less than the upper bound."
        )

    def decay_time_wrapper(rp: float) -> float:
        """
        Wrapper for decay_time to match the signature for optimization.
        """
        return deactivation_tau(transducer, rp=rp)

    # Perform numerical optimization to find the resistance that minimizes decay time
    result = minimize_scalar(
        decay_time_wrapper,
        bounds=resistance_range,
        method="bounded",  # Use bounded optimization since we have a range
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
            "Consider reducing the lower bound.",
            optimal_resistance,
        )
        print(
            "Hint: The optimal resistance (%.2f Ω) is near the lower bound of the range. "
            "Consider reducing the lower bound.",
            optimal_resistance,
        )
    elif abs(optimal_resistance - upper_bound) < tolerance:
        logging.warning(
            "Hint: The optimal resistance (%.2f Ω) is near the upper bound of the range. "
            "Consider increasing the upper bound.",
            optimal_resistance,
        )
        print(
            "Hint: The optimal resistance (%.2f Ω) is near the upper bound of the range. "
            "Consider increasing the upper bound.",
            optimal_resistance,
        )

    return optimal_resistance, minimal_decay_time


def deactivation_current(
    t: float,
    i0: float,
    transducer: Transducer,
    rp: Optional[float] = None,
    di0: float = 0.0,
    d2i0: Optional[float] = None,
) -> float:
    r"""
    Calculate the transient current i(t) for a deactivation BVD model (3rd order).

    For open-circuit termination (MOSFET opens), the characteristic polynomial
    typically includes a root at 0. If you enforce i(0)=i0, i'(0)=0, i''(0)=0,
    that zero-root mode can force an unphysical constant-current solution.

    Therefore, the default initial conditions are chosen to represent a typical
    switch-off at a *current peak*:
      i(0)  = i0
      i'(0) = di0  (default 0)
      i''(0) ≈ -ω_d^2 * i0   (default inferred from oscillatory eigenpair)

    Parameters
    ----------
    t : float
        Time (s) at which to evaluate i(t).
    i0 : float
        Initial current i(0) in coef_a.
    transducer : Transducer
        Transducer containing rs, ls, cs, c0, and optional rp.
    rp : Optional[float]
        Parallel damping resistance. If None, uses transducer.rp.
        If both are None => open circuit (Rp → ∞).
    di0 : float
        Initial derivative i'(0) in coef_a/s. Default 0 (peak current assumption).
    d2i0 : Optional[float]
        Initial second derivative i''(0) in coef_a/s^2.
        If None, inferred as -ω_d^2*i0 using the oscillatory eigenpair.

    Returns
    -------
    float
        Real part of i(t).
    """
    # Use transducer's rp if not explicitly provided
    rp = transducer.rp if rp is None else rp

    # MOSFET open => open circuit
    if rp is None:
        rp = np.inf

    eigenvalues = roots(
        transducer.rs, transducer.ls, transducer.cs, transducer.c0, rp=rp
    )

    # Stability check (allow tiny numerical noise)
    for lam in eigenvalues:
        if complex(lam).real > 1e-12:
            raise ValueError(
                f"Unstable system: eigenvalue {lam} has positive real part."
            )

    # If user did not provide i''(0), infer it from the dominant oscillatory eigenpair
    if d2i0 is None:
        lam_osc = max((complex(z) for z in eigenvalues), key=lambda z: abs(z.imag))
        omega_d = abs(lam_osc.imag)
        d2i0 = -(omega_d**2) * i0 if omega_d > 0 else 0.0

    lam1_c, lam2_c, lam3_c = map(complex, eigenvalues)

    # Solve for coef_a, coef_b, coef_c from:
    # i(0)  = coef_a + coef_b + coef_c = i0
    # i'(0) = lam1*coef_a + lam2*coef_b + lam3*coef_c = di0
    # i''(0)= lam1^2*coef_a + lam2^2*coef_b + lam3^2*coef_c = d2i0
    matrix = np.array(
        [
            [1.0, 1.0, 1.0],
            [lam1_c, lam2_c, lam3_c],
            [lam1_c**2, lam2_c**2, lam3_c**2],
        ],
        dtype=complex,
    )
    rhs = np.array([i0, di0, d2i0], dtype=complex)
    coef_a, coef_b, coef_c = np.linalg.solve(matrix, rhs)

    i_t = (
        coef_a * cmath.exp(lam1_c * t)
        + coef_b * cmath.exp(lam2_c * t)
        + coef_c * cmath.exp(lam3_c * t)
    )
    return float(i_t.real)
