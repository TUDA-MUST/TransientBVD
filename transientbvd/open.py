import logging
from typing import Tuple, Optional

from scipy.optimize import minimize_scalar

from .utils import roots

logging.basicConfig(level=logging.INFO)


def potential(
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


def decay_time(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    rp: Optional[float] = None
) -> float:
    """
    Calculate the decay time for a given parallel resistance (rp) or without it.

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
        Decay time in seconds.

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
        return decay_time(rs, ls, cs, c0, rp=rp)

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
        logging.info(
            f"Hint: The optimal resistance ({optimal_resistance:.2f} ohms) is near the lower bound of the range. "
            f"Consider reducing the lower bound.")
    elif abs(optimal_resistance - upper_bound) < tolerance:
        logging.info(
            f"Hint: The optimal resistance ({optimal_resistance:.2f} ohms) is near the upper bound of the range. "
            f"Consider increasing the upper bound.")

    return optimal_resistance, minimal_decay_time


from typing import Optional, Callable
import math


def current(
    i0: float,
    t: float,
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    rp: Optional[float] = None
) -> float:
    r"""
    Calculate the transient current behavior for a given time `t` and circuit parameters.

    This method models the current response using the roots of the characteristic polynomial
    for the Butterworth-Van Dyke (BVD) equivalent circuit.

    Parameters
    ----------
    i0 : float
        Initial current in amperes.
    t : float
        Time in seconds.
    rs : float
        Series resistance in ohms (BVD model parameter).
    ls : float
        Inductance in henries (BVD model parameter).
    cs : float
        Series capacitance in farads (BVD model parameter).
    c0 : float
        Parallel capacitance in farads (BVD model parameter).
    rp : Optional[float], default=None
        Parallel resistance in ohms. If None, calculates the open circuit response.
    voltage : Callable[[float, Optional[float]], float], default=lambda t, rp: 0
        Voltage function as a function of time `t` and parallel resistance `rp`.

    Returns
    -------
    float
        Transient current at time `t`.

    Raises
    ------
    ValueError
        If any BVD model parameter (rs, ls, cs, c0) is not positive.

    Notes
    -----
    - The `voltage` function should be implemented separately and passed to this method.
    - The roots of the characteristic polynomial are calculated using the `roots` function.
    """
    # Validate parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("Parallel resistance `rp` must be positive if provided.")

    # Calculate the roots of the characteristic polynomial
    roots_list = roots(rs, ls, cs, c0, rp)
    y1, y2, y3 = roots_list

    A = I0 * res / 10
    B = I0 / (1 / res + C0 * re(Y_list[ind][1]) + (C0 ** 2 * im(Y_list[ind][1]) ** 2) / (
                1 / res + C0 * re(Y_list[ind][1])))
    C = (C0 * B * abs(im(Y_list[ind][1]))) / (1 / res + C0 * re(Y_list[ind][1]))
    return A * math.exp(Y_list[ind][0] * t) + math.exp(re(Y_list[ind][1]) * t) * (
                B * math.cos(im(Y_list[ind][1]) * t) + C * math.cos(im(Y_list[ind][1]) * t))

    # For demonstration purposes, here's a placeholder for coefficient calculations
    # You may need to adjust these calculations based on the actual equations
    A = i0  # Initial coefficient
    # Additional coefficient calculations would go here

    # Compute the transient current using the voltage function
    transient_current = (
        (1 / rp) * voltage(t, rp) if rp else 0
        + A * math.exp(y1 * t)
        # Additional terms involving y2, y3 would be added here
    )

    return transient_current


if __name__ == "__main__":
    rs = 24.764  # Series resistance in ohms
    ls = 38.959e-3  # Inductance in henries
    cs = 400.33e-12  # Series capacitance in farads
    c0 = 3970.1e-12  # Parallel capacitance in farads
    t = decay_time(rs, ls, cs, c0)
    print(f"Decay time without parallel resistance: {t:.6f} s")
    t2 = decay_time(rs, ls, cs, c0, rp=500)
    print(f"Decay time with parallel 500 resistance: {t2:.6f} s")
    t3 = decay_time(rs, ls, cs, c0, rp=900)
    print(f"Decay time with parallel 1000 resistance: {t3:.6f} s")

    #c0=3700e-12
    #rs= 21.05
    #ls = 35.15e-3
    #cs = 448.62e-12
    #c0 = 4075.69e-12

    from sympy import solve, im, re
    from sympy.abc import x
    from utils import roots
    # Calculation of the roots of the characteristic polynom of the DGL, DGL is calculated by hand
    def calc_roots(res):
        ko = [rs / ls + 1 / (res * c0), (rs / (ls * c0 * res) + 1 / (cs * ls) + 1 / (c0 * ls)),
              1 / (cs * res * c0 * ls)]
        eq = x ** 3 + ko[0] * x ** 2 + ko[1] * x + ko[2]
        result = solve(eq, x)
        return result

    print(f"OLD: Roots with 500 resistance: {calc_roots(500)}")
    print(f"NEW: Roots with 500 resistance: {roots(rs, ls, cs, c0, rp=500)}")
    print(f"OLD: Roots with 900 resistance: {calc_roots(900)}")
    print(f"NEW: Roots with 900 resistance: {roots(rs, ls, cs, c0, rp=900)}")
    print(f"OLD: Roots with 2000 resistance: {calc_roots(2000)}")
    print(f"NEW: Roots with 2000 resistance: {roots(rs, ls, cs, c0, rp=2000)}")