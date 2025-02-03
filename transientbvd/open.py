import cmath
import logging
from typing import Optional
from typing import Tuple

import numpy as np
from scipy.optimize import minimize_scalar

from .utils import roots


def print_open_potential(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    resistance_range: Tuple[float, float] = (10, 5000)
) -> None:
    """
    Pretty print the results of open_potential, including decay times and speed improvement.

    Parameters
    ----------
    rs : float
        Series resistance in ohms (BVD model parameter).
    ls : float
        Inductance in henries (BVD model parameter).
    cs : float
        Series capacitance in farads (BVD model parameter).
    c0 : float
        Parallel capacitance in farads (BVD model parameter).
    resistance_range : Tuple[float, float], optional
        A tuple representing the lower and upper bounds of resistances (in ohms) to evaluate
        for damping optimization. Default is (10, 5000).
    """
    # Evaluate the open_potential
    optimal_resistance, tau_with_rp, delta_time, percentage_improvement = open_potential(
        rs, ls, cs, c0, resistance_range
    )

    # Calculate decay times without using rp
    tau_no_rp = 2 * ls / rs
    two_tau_no_rp = 2 * tau_no_rp

    # Calculate 2τ for rp
    two_tau_with_rp = 2 * tau_with_rp

    # Calculate speed improvement factor
    speed_improvement = tau_no_rp / tau_with_rp if tau_with_rp > 0 else float("inf")

    # Pretty print the results
    print("=" * 50)
    print("Open Potential Analysis")
    print("=" * 50)
    print(f"Series Resistance (Rs): {rs:.2f} Ω")
    print(f"Inductance (Ls): {ls:.6e} H")
    print(f"Series Capacitance (Cs): {cs:.6e} F")
    print(f"Parallel Capacitance (C0): {c0:.6e} F")
    print(f"Resistance Range: {resistance_range[0]} Ω to {resistance_range[1]} Ω")
    print("-" * 50)
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
    rs: float,
    ls: float,
    cs: float,
    c0: float,
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

    The improvement is expressed as the absolute difference in decay time and the percentage reduction.

    Parameters
    ----------
    rs : float
        Series resistance in ohms (BVD model parameter).
    ls : float
        Inductance in henries (BVD model parameter).
    cs : float
        Series capacitance in farads (BVD model parameter).
    c0 : float
        Parallel capacitance in farads (BVD model parameter).
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
    optimal_resistance, tau_with_rp = optimum_resistance(rs, ls, cs, c0, resistance_range)

    # Compute the absolute and percentage improvements
    delta_time = tau_no_rp - tau_with_rp
    percentage_improvement = (delta_time / tau_no_rp) * 100 if tau_no_rp > 0 else 0.0

    return optimal_resistance, tau_with_rp, delta_time, percentage_improvement


def open_tau(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    rp: Optional[float] = None
) -> float:
    """
    Calculate the decay time (τ) for a given parallel resistance (rp) or without it.

    Parameters
    ----------
    rs : float
        Series resistance in ohms (BVD model parameter).
    ls : float
        Inductance in henries (BVD model parameter).
    cs : float
        Series capacitance in farads (BVD model parameter).
    c0 : float
        Parallel capacitance in farads (BVD model parameter).
    rp : Optional[float], default=None
        Parallel resistance in ohms. If None, decay time is calculated without rp.

    Returns
    -------
    float
        Decay time (τ) in seconds.

    Raises
    ------
    ValueError
        If any BVD model parameter (rs, ls, cs, c0) is not positive or if rp is non-positive.

    Notes
    -----
    - When `rp` is not provided, the decay time is calculated using the formula:
      τ = 2 * ls / rs (approximating an open circuit).
    - When `rp` is provided, the decay time is determined using the eigenvalues of
      the characteristic polynomial.
    """
    # Validate input parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("rp must be positive if provided.")

    if rp is None:
        # Calculate the decay time without using rp (τ = 2L / R)
        tau_no_rp = 2 * ls / rs
        return tau_no_rp

    # Calculate the decay time using rp and the eigenvalues
    calculated_roots = roots(rs, ls, cs, c0, rp=rp)
    second_root = calculated_roots[1]  # Replace λ2 with a more generic name
    decay_rate = abs(second_root.real)
    return 1 / decay_rate if decay_rate > 0 else float("inf")


def open_two_tau(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    rp: Optional[float] = None
) -> float:
    """
    Calculate twice the decay time (2τ) for a given parallel resistance (rp) or without it.

    Parameters
    ----------
    rs : float
        Series resistance in ohms (BVD model parameter).
    ls : float
        Inductance in henries (BVD model parameter).
    cs : float
        Series capacitance in farads (BVD model parameter).
    c0 : float
        Parallel capacitance in farads (BVD model parameter).
    rp : Optional[float], default=None
        Parallel resistance in ohms. If None, decay time is calculated without rp.

    Returns
    -------
    float
        Twice the decay time (2τ) in seconds.

    Raises
    ------
    ValueError
        If any BVD model parameter (rs, ls, cs, c0) is not positive or if rp is non-positive.

    Notes
    -----
    - When `rp` is not provided, the decay time is calculated using the formula:
      2τ = 4 * ls / rs (approximating an open circuit).
    - When `rp` is provided, the decay time is determined using the eigenvalues of
      the characteristic polynomial.
    """
    return 2 * open_tau(rs, ls, cs, c0, rp)


def optimum_resistance(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    resistance_range: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Calculate the optimal parallel resistance (highest damping) for the transient response
    in a system modeled by the Butterworth-Van Dyke (BVD) equivalent circuit using numerical optimization.

    Parameters
    ----------
    rs : float
        Series resistance in ohms (BVD model parameter).
    ls : float
        Inductance in henries (BVD model parameter).
    cs : float
        Series capacitance in farads (BVD model parameter).
    c0 : float
        Parallel capacitance in farads (BVD model parameter).
    resistance_range : Tuple[float, float]
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
        If any BVD model parameter (rs, ls, cs, c0) is not positive or if resistance bounds are invalid.
    """
    # Validate input parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if resistance_range[0] <= 0 or resistance_range[1] <= 0:
        raise ValueError("Resistance bounds must be positive.")
    if resistance_range[0] >= resistance_range[1]:
        raise ValueError("Resistance range must have a lower bound less than the upper bound.")

    def decay_time_wrapper(rp: float) -> float:
        """
        Wrapper for decay_time to match the signature for optimization.
        """
        return open_tau(rs, ls, cs, c0, rp=rp)

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
            f"Hint: The optimal resistance ({optimal_resistance:.2f} ohms) is near the lower bound of the range. "
            f"Consider reducing the lower bound.")
    elif abs(optimal_resistance - upper_bound) < tolerance:
        logging.warning(
            f"Hint: The optimal resistance ({optimal_resistance:.2f} ohms) is near the upper bound of the range. "
            f"Consider increasing the upper bound.")

    return optimal_resistance, minimal_decay_time


def open_current(
    t: float,
    i0: float,
    rs: float,
    ls: float,
    cs: float,
    c0: Optional[float] = None,
    rp: Optional[float] = None
) -> float:
    r"""
    Calculate the transient current i(t) for an open-circuit BVD model (3rd order),
    assuming initial conditions:
      i(0) = i0, i'(0) = 0, i''(0) = 0.

    The system's eigenvalues are taken from ``roots(...)``. For a 3rd-order polynomial
    (e.g., including parallel capacitance and optional parallel resistor), we get
    three eigenvalues :math:`\lambda_1, \lambda_2, \lambda_3`. The solution is:

    .. math::

       i(t) = A\, e^{\lambda_1 t} + B\, e^{\lambda_2 t} + C\, e^{\lambda_3 t},

    with coefficients :math:`A,B,C` determined from the above initial conditions.

    Parameters
    ----------
    t : float
        Time in seconds at which to evaluate i(t).
    i0 : float
        Initial current in amperes (i(0) = i0).
    rs : float
        Series resistance in ohms.
    ls : float
        Motional inductance in henries.
    cs : float
        Motional capacitance in farads.
    c0 : float
        Parallel (static) capacitance in farads. Will not be used either way.
    rp : Optional[float]
        Parallel resistor. If None, purely open-circuit. If a value is given,
        it modifies the polynomial.

    Returns
    -------
    float
        The real part of i(t) under these assumptions.

    Notes
    -----
    - This approach is conceptual: you must confirm the three initial conditions
      truly match your physical scenario. You might prefer i'(0)=some value if you had
      a certain voltage at t=0, etc.
    - If the system ends up with repeated roots or is effectively 2nd order, handle
      those special cases. This code demonstrates the typical 3-distinct-roots scenario.
    """

    # 1) Get the eigenvalues from the BVD polynomial (3rd order if rp is not None, or still 3rd if rp=None).
    lam_list = roots(rs, ls, cs, c0, rp=rp)  # returns up to 3 complex roots typically
    if len(lam_list) != 3:
        raise ValueError(
            f"Expected 3 eigenvalues, got {len(lam_list)}. "
            "Check polynomial or special-case repeated roots."
        )

    lam1, lam2, lam3 = lam_list

    # 2) We assume i(t) = A e^(lam1 t) + B e^(lam2 t) + C e^(lam3 t).
    #    Then:
    #
    #      i'(t)  = lam1 A e^(lam1 t) + lam2 B e^(lam2 t) + lam3 C e^(lam3 t)
    #      i''(t) = lam1^2 A e^(lam1 t) + lam2^2 B e^(lam2 t) + lam3^2 C e^(lam3 t)
    #
    #    With initial conditions at t=0:
    #      i(0)    = A + B + C           = i0
    #      i'(0)   = lam1 A + lam2 B + lam3 C   = 0
    #      i''(0)  = lam1^2 A + lam2^2 B + lam3^2 C = 0

    lam1_c = complex(lam1)
    lam2_c = complex(lam2)
    lam3_c = complex(lam3)

    # 3) Form the matrix M and the RHS vector.
    #    M * [A, B, C]^T = [i0, 0, 0]^T
    #    M is:
    #      [ 1        1         1       ]
    #      [ lam1_c   lam2_c    lam3_c  ]
    #      [ lam1_c^2 lam2_c^2  lam3_c^2]

    M = np.array([
        [1.0,     1.0,     1.0    ],
        [lam1_c,  lam2_c,  lam3_c ],
        [lam1_c**2, lam2_c**2, lam3_c**2]
    ], dtype=complex)

    rhs = np.array([i0, 0.0, 0.0], dtype=complex)

    # 4) Solve the 3x3 system for A, B, C using numpy
    sol_ABC = np.linalg.solve(M, rhs)
    A_coef, B_coef, C_coef = sol_ABC

    # 5) Evaluate i(t) = A e^(lam1 t) + B e^(lam2 t) + C e^(lam3 t).
    i_t = (
        A_coef * cmath.exp(lam1_c * t)
        + B_coef * cmath.exp(lam2_c * t)
        + C_coef * cmath.exp(lam3_c * t)
    )

    # The physical current is typically the real part (the imaginary part should be near zero
    # in a well-formed system if the roots come in conjugate pairs).
    return i_t.real



