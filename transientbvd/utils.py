"""
TransientBVD - Utility Functions

This module provides general-purpose utility functions for transient analysis
of resonant circuits modeled by the Butterworth-Van Dyke (BVD) equivalent circuit.

Functions include resonance frequency calculation, polynomial root solving,
and other numerical methods used throughout the TransientBVD package.
"""

from typing import List
from typing import overload, Optional

import numpy as np


@overload
def resonance_frequency(ls: float, cs: float) -> float: ...


def resonance_frequency(
    ls: Optional[float] = None, cs: Optional[float] = None
) -> float:
    r"""
    Calculate the resonance frequency of a system based on the Butterworth-Van Dyke (BVD) model.

    The resonance frequency is given by:

    .. math::

        f_r = \frac{1}{2\pi\sqrt{L_s C_s}},

    where :math:`L_s` is the motional inductance and :math:`C_s` is the motional capacitance.

    Parameters
    ----------
    ls : float, optional
        Motional inductance in henries.
    cs : float, optional
        Motional capacitance in farads.

    Returns
    -------
    float
        The resonance frequency in hertz.

    Notes
    -----
    - Only `ls` and `cs` are used in the calculation.

    Raises
    ------
    ValueError
        If required parameters are missing or invalid.
    """
    # Ensure required parameters are present
    if ls is None or cs is None:
        raise ValueError(
            "Both 'ls' and 'cs' must be provided directly or "
            "via a Transducer/EquivalentCircuitParams object."
        )
    if ls <= 0 or cs <= 0:
        raise ValueError("Both 'ls' and 'cs' must be positive.")

    # Calculate and return resonance frequency
    return 1 / (2 * np.pi * (ls * cs) ** 0.5)


@overload
def roots(
    rs: float, ls: float, cs: float, c0: float, rp: Optional[float] = None
) -> List[complex]: ...


def roots(
    rs: Optional[float] = None,
    ls: Optional[float] = None,
    cs: Optional[float] = None,
    c0: Optional[float] = None,
    rp: Optional[float] = None,
) -> List[complex]:
    r"""
    Calculate the roots of the characteristic polynomial for the transient response
    of a system modeled by the Butterworth-Van Dyke (BVD) equivalent circuit.

    IMPORTANT TERMINATION SEMANTICS (matches "MOSFET opens"):
    - rp is None  => open circuit termination (Rp → ∞)
    - rp is +inf  => open circuit termination (Rp → ∞)
    - rp is finite positive => explicit parallel damping resistor

    For open circuit (Rp → ∞), the cubic has a0 = 0, which introduces a root at 0.
    That is expected for this terminal condition; the transient decay then comes from
    the oscillatory pair’s negative real part (≈ -Rs/(2Ls)).

    Returns
    -------
    List[complex]
        Roots (complex) of: s^3 + a2*s^2 + a1*s + a0 = 0

    Raises
    ------
    ValueError
        If parameters are missing or non-positive, or rp is non-positive when finite.
    """
    # Ensure required parameters are provided
    if rs is None or ls is None or cs is None or c0 is None:
        raise ValueError("All parameters (rs, ls, cs, c0) must be provided.")

    # Validate parameter values
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")

    # Normalize semantics: "no Rp" means open circuit (MOSFET open) => Rp -> ∞
    if rp is None:
        rp = np.inf

    if np.isfinite(rp):
        if rp <= 0:
            raise ValueError("If provided, rp must be a positive value.")
        # With finite parallel resistance Rp
        a2 = rs / ls + 1.0 / (rp * c0)
        a1 = rs / (rp * ls * c0) + 1.0 / (ls * cs) + 1.0 / (ls * c0)
        a0 = 1.0 / (ls * cs * rp * c0)
    else:
        # Open circuit Rp -> ∞ (MOSFET opens)
        a2 = rs / ls
        a1 = 1.0 / (ls * cs) + 1.0 / (ls * c0)
        a0 = 0.0

    # Solve cubic numerically: s^3 + a2*s^2 + a1*s + a0 = 0
    coeff = np.array([1.0, a2, a1, a0], dtype=float)
    rts = np.roots(coeff)

    # Deterministic ordering helps downstream code (tau selection, debugging)
    rts_sorted = sorted(
        (complex(x) for x in rts), key=lambda z: (z.real, z.imag), reverse=True
    )
    return rts_sorted
