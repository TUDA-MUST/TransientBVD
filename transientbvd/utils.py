from typing import Optional, List
from typing import Union, overload

import numpy as np
import sympy as sp


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

    The transient voltage behavior is described by the eigenvalues of the
    characteristic polynomial. The general solution for the transient voltage is:

    .. math::

        u(t) = A e^{\lambda_1 t} + B e^{\lambda_2 t} + C e^{\lambda_3 t},

    where :math:`A`, :math:`B`, and :math:`C` are real coefficients determined
    by initial conditions. These coefficients scale the contributions from
    each eigenvalue.

    If the system has complex eigenvalues, the exponential terms are converted
    into trigonometric functions. This yields the solution:

    .. math::

        u(t) = c_1 e^{\lambda_1 t} + e^{\operatorname{Re}(\lambda_2) t}
               \left[c_2 \cos{(\operatorname{Im}(\lambda_3) t)}
               + c_3 \sin{(\operatorname{Im}(\lambda_3) t)}\right],

    where :math:`c_1`, :math:`c_2`, and :math:`c_3` are constants derived
    from the initial conditions, and :math:`\operatorname{Re}` and
    :math:`\operatorname{Im}` denote the real and imaginary parts of
    the eigenvalues, respectively.

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

    Notes
    -----
    The calculation assumes the system is modeled accurately by the BVD equivalent
    circuit. The transient response is governed by the relationship between
    resistive, capacitive, and inductive components, and the eigenvalues of the
    polynomial define the system's behavior over time.
    """
    # Validate input parameters
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("If provided, rp must be a positive value.")

    # Define the symbolic variable
    λ = sp.symbols('λ', real=False)

    # Calculate the coefficients of the characteristic polynomial
    if rp is not None:  # With optional parallel resistance
        c0 = rs / ls + 1 / (rp * c0)
        c1 = rs / (ls * c0 * rp) + 1 / (cs * ls) + 1 / (c0 * ls)
        c2 = 1 / (cs * rp * c0 * ls)
    else:  # Without parallel resistance
        c0 = rs / ls
        c1 = rs / (ls * c0) + 1 / (cs * ls) + 1 / (c0 * ls)
        c2 = 1 / (cs * c0 * ls)

    # Construct the characteristic polynomial
    characteristic_poly = λ**3 + c0 * λ**2 + c1 * λ + c2

    # Solve for the roots
    p_roots = sp.solvers.solve(characteristic_poly, λ)

    return [complex(root) for root in p_roots]  # Ensure all roots are returned as complex numbers
