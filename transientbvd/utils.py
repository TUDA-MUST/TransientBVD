from typing import Optional, List
from typing import Union, overload

import numpy as np
from sympy import solve, symbols
from sympy.abc import x


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


from mpmath import mp
from typing import List, Optional

def roots_with_mpmath(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    rp: Optional[float] = None,
    precision: int = 50
) -> List[complex]:
    r"""
    Calculate the roots of the characteristic polynomial using mpmath for high precision.

    Parameters
    ----------
    rs : float
        Series resistance in ohms.
    ls : float
        Inductance in henries.
    cs : float
        Series capacitance in farads.
    c0 : float
        Parallel capacitance in farads.
    rp : Optional[float]
        Parallel resistance in ohms. If None, considers the open circuit.
    precision : int, default=50
        Number of significant digits for the root calculations.

    Returns
    -------
    List[complex]
        Roots of the characteristic polynomial.
    """
    # Set precision
    mp.dps = precision

    # Validate input parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("If provided, rp must be a positive value.")

    # Calculate polynomial coefficients
    if rp is not None:
        a2 = mp.mpf(rs / ls) + mp.mpf(1 / (rp * c0))
        a1 = (
            mp.mpf(rs / (rp * ls * c0))
            + mp.mpf(1 / (cs * ls))
            + mp.mpf(1 / (ls * c0))
        )
        a0 = mp.mpf(1 / (cs * rp * c0 * ls))
    else:
        a2 = mp.mpf(rs / ls)
        a1 = mp.mpf(rs / (ls * c0)) + mp.mpf(1 / (cs * ls)) + mp.mpf(1 / (ls * c0))
        a0 = mp.mpf(1 / (cs * ls * c0))

    # Polynomial coefficients in decreasing order
    coefficients = [1, a2, a1, a0]

    # Calculate roots using mpmath.polyroots
    roots = mp.polyroots(coefficients, maxsteps=100000)

    return [complex(root) for root in roots]

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

    # Debug: Print coefficients
    print(f"Coefficients: a2={a2}, a1={a1}, a0={a0}")

    # Construct the characteristic polynomial
    x = symbols('x')
    eq = x**3 + a2 * x**2 + a1 * x + a0

    # Solve for the roots
    p_roots = solve(eq, x)

    # Debug: Print roots
    print(f"Calculated roots: {p_roots}")

    return [complex(root.evalf()) for root in p_roots]  # Convert roots to complex numbers


if __name__ == "__main__":
    # Example circuit parameters
    rs = 24.764  # Series resistance in ohms
    ls = 38.959e-3  # Inductance in henries
    cs = 400.33e-12  # Series capacitance in farads
    c0 = 3970.1e-12  # Parallel capacitance in farads
    rp = 2000  # Parallel resistance in ohms
    precision = 100  # Precision for mpmath

    # Calculate roots using the SymPy-based method
    sympy_roots = roots(rs, ls, cs, c0, rp)
    print(f"SymPy roots:")
    for root in sympy_roots:
        print(f"  {root}")

    # Calculate roots using the mpmath-based method
    mpmath_roots = roots_with_mpmath(rs, ls, cs, c0, rp, precision=precision)
    print(f"\nmpmath roots (precision={precision}):")
    for root in mpmath_roots:
        print(f"  {root}")

    # Compare the two sets of roots
    print("\nComparison:")
    for sympy_root, mpmath_root in zip(sympy_roots, mpmath_roots):
        real_diff = abs(sympy_root.real - mpmath_root.real)
        imag_diff = abs(sympy_root.imag - mpmath_root.imag)
        print(f"SymPy: {sympy_root}, mpmath: {mpmath_root}")
        print(f"  Real difference: {real_diff:.10e}, Imaginary difference: {imag_diff:.10e}")
