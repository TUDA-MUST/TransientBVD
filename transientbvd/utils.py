from typing import List, Optional
from typing import overload

import numpy as np
from sympy import solve, symbols


@overload
def resonance_frequency(ls: float, cs: float) -> float:
    ...


@overload
def resonance_frequency(rs: float, ls: float, cs: float, c0: float) -> float:
    ...


def resonance_frequency(
    rs: float = None, ls: float = None, cs: float = None, c0: float = None
) -> float:
    r"""
    Calculate the resonance frequency of a system based on the Butterworth-Van Dyke (BVD) model.

    The resonance frequency occurs when the motional inductance and motional capacitance
    form a series resonance. The frequency is given by:

    .. math::

        f_r = \frac{1}{2\pi\sqrt{L_s C_s}},

    where :math:`L_s` is the motional inductance and :math:`C_s` is the motional capacitance.

    Parameters
    ----------
    ls : float
        Motional inductance in henries (BVD model parameter).
    cs : float
        Motional capacitance in farads (BVD model parameter).

    rs : float, optional
        Series resistance in ohms (BVD model parameter).
    c0 : float, optional
        Parallel capacitance in farads (BVD model parameter).

    Returns
    -------
    float
        The resonance frequency in hertz.

    Notes
    -----
    - This function can accept either two arguments (`ls` and `cs`) or four arguments
      (`rs`, `ls`, `cs`, `c0`), for compatibility with other methods.
    - Only `ls` and `cs` are used in the calculation.

    Raises
    ------
    ValueError
        If any required parameters are not positive.
    """
    # Handle two-parameter case
    if rs is None and c0 is None:
        if ls is None or cs is None:
            raise ValueError("Both 'ls' and 'cs' must be provided.")
        if ls <= 0 or cs <= 0:
            raise ValueError("Both 'ls' and 'cs' must be positive.")

    # Handle four-parameter case
    elif rs is not None and ls is not None and cs is not None and c0 is not None:
        if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
            raise ValueError("All parameters (rs, ls, cs, c0) must be positive.")
    else:
        raise ValueError(
            "Invalid combination of arguments. Provide either (ls, cs) or (rs, ls, cs, c0)."
        )

    # Use ls and cs to calculate resonance frequency
    resonance_freq = 1 / (2 * np.pi * (ls * cs) ** 0.5)

    return resonance_freq


def roots(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    rp: Optional[float] = None
) -> List[complex]:
    r"""
    Calculate the roots of the characteristic polynomial for transient response
    in a system modeled by the Butterworth-Van Dyke (BVD) equivalent circuit.

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
    rp : Optional[float]
        Optional parallel resistance in ohms. If not provided or set to 0,
        considers only the primary circuit components.

    Returns
    -------
    List[complex]
        Roots of the characteristic polynomial.
    """
    # Validate input parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("If provided, rp must be a positive value.")

    # Calculate the coefficients of the characteristic polynomial
    if rp is not None:  # With optional parallel resistance
        a2 = rs / ls + 1 / (rp * c0)
        a1 = rs / (rp * ls * c0) + 1 / (cs * ls) + 1 / (ls * c0)
        a0 = 1 / (cs * rp * ls * c0)
    else:  # Without parallel resistance
        a2 = rs / ls
        a1 = rs / (ls * c0) + 1 / (cs * ls) + 1 / (ls * c0)
        a0 = 1 / (cs * ls * c0)

    # Construct the characteristic polynomial
    x = symbols('x')
    eq = x**3 + a2 * x**2 + a1 * x + a0

    # Solve for the roots
    p_roots = solve(eq, x)

    return [complex(root.evalf()) for root in p_roots]  # Convert roots to complex numbers


def print_circuit_params(rs: float, ls: float, cs: float, c0: float) -> None:
    """
    Print the Butterworth-Van Dyke (BVD) model circuit parameters in a formatted output.

    Parameters
    ----------
    rs : float
        Series resistance in ohms (Ω).
    ls : float
        Inductance in henries (H).
    cs : float
        Series capacitance in farads (F).
    c0 : float
        Parallel capacitance in farads (F).

    Returns
    -------
    None
        Prints the circuit parameters to the console in a formatted way.
    """
    print("Butterworth-Van Dyke (BVD) Model Parameters")
    print("=" * 50)
    print(f"Series Resistance (Rs): {rs:.2f} Ω")
    print(f"Inductance (Ls): {ls:.6e} H")
    print(f"Series Capacitance (Cs): {cs:.6e} F")
    print(f"Parallel Capacitance (C0): {c0:.6e} F")
    print("=" * 50)
