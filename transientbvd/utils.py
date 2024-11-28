from typing import Optional, List

import sympy as sp


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
