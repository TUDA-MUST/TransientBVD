"""
TransientBVD - Utility Functions

This module provides general-purpose utility functions for transient analysis
of resonant circuits modeled by the Butterworth-Van Dyke (BVD) equivalent circuit.

Functions include resonance frequency calculation, polynomial root solving,
and other numerical methods used throughout the TransientBVD package.
"""
from typing import List
from typing import overload, Optional, Union

import numpy as np
from sympy import solve, symbols

from .transducer import Transducer, EquivalentCircuitParams


@overload
def resonance_frequency(ls: float, cs: float) -> float:
    ...


@overload
def resonance_frequency(rs: float, ls: float, cs: float, c0: float) -> float:
    ...


@overload
def resonance_frequency(obj: Union[Transducer, EquivalentCircuitParams]) -> float:
    ...


def resonance_frequency(
        ls: Optional[float] = None,
        cs: Optional[float] = None,
        rs: Optional[float] = None,
        c0: Optional[float] = None,
        obj: Optional[Union[Transducer, EquivalentCircuitParams]] = None
) -> float:
    """
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
    rs : float, optional
        Series resistance in ohms.
    c0 : float, optional
        Parallel capacitance in farads.
    obj : Union[Transducer, EquivalentCircuitParams], optional
        A transducer or equivalent circuit object.

    Returns
    -------
    float
        The resonance frequency in hertz.

    Notes
    -----
    - If a `Transducer` or `EquivalentCircuitParams` object is provided, the function extracts
      the necessary parameters from it.
    - Only `ls` and `cs` are used in the calculation.

    Raises
    ------
    ValueError
        If required parameters are missing or invalid.
    """

    # If an object is provided, extract parameters
    if obj is not None:
        ls, cs = obj.ls, obj.cs

    # Ensure required parameters are present
    if ls is None or cs is None:
        raise ValueError(
            "Both 'ls' and 'cs' must be provided directly or "
            "via a Transducer/EquivalentCircuitParams object.")
    if ls <= 0 or cs <= 0:
        raise ValueError("Both 'ls' and 'cs' must be positive.")

    # Calculate and return resonance frequency
    return 1 / (2 * np.pi * (ls * cs) ** 0.5)


@overload
def roots(
        rs: float, ls: float, cs: float, c0: float, rp: Optional[float] = None
) -> List[complex]:
    ...


@overload
def roots(
        obj: Union[Transducer, EquivalentCircuitParams], rp: Optional[float] = None
) -> List[complex]:
    ...


def roots(
        rs: Optional[float] = None,
        ls: Optional[float] = None,
        cs: Optional[float] = None,
        c0: Optional[float] = None,
        rp: Optional[float] = None,
        obj: Optional[Union[Transducer, EquivalentCircuitParams]] = None
) -> List[complex]:
    """
    Calculate the roots of the characteristic polynomial for transient response
    in a system modeled by the Butterworth-Van Dyke (BVD) equivalent circuit.

    Parameters
    ----------
    rs : float, optional
        Series resistance in ohms.
    ls : float, optional
        Inductance in henries.
    cs : float, optional
        Series capacitance in farads.
    c0 : float, optional
        Parallel capacitance in farads.
    rp : float, optional
        Parallel resistance in ohms (default: None, meaning no parallel resistance).
    obj : Union[Transducer, EquivalentCircuitParams], optional
        A `Transducer` or `EquivalentCircuitParams` object.

    Returns
    -------
    List[complex]
        Roots of the characteristic polynomial.

    Notes
    -----
    - If an object (`Transducer` or `EquivalentCircuitParams`) is provided, it extracts
      `rs`, `ls`, `cs`, and `c0` automatically.
    - If `rp` is passed, it overrides the object's `rp` value.
    - Uses symbolic algebra to find polynomial roots.

    Raises
    ------
    ValueError
        If required parameters are missing or invalid.
    """

    # Extract parameters from object if provided
    if obj is not None:
        rs, ls, cs, c0 = obj.rs, obj.ls, obj.cs, obj.c0
        rp = rp if rp is not None else obj.rp  # Use given `rp`, otherwise use object's `rp`

    # Ensure required parameters are present
    if rs is None or ls is None or cs is None or c0 is None:
        raise ValueError(
            "All parameters (rs, ls, cs, c0) must be provided directly or via an object.")

    # Validate parameter values
    if rs <= 0 or ls <= 0 or cs <= 0 or c0 <= 0:
        raise ValueError("All BVD model parameters (rs, ls, cs, c0) must be positive.")
    if rp is not None and rp <= 0:
        raise ValueError("If provided, rp must be a positive value.")

    # Calculate the coefficients of the characteristic polynomial
    if rp is not None:  # With parallel resistance
        a2 = rs / ls + 1 / (rp * c0)
        a1 = rs / (rp * ls * c0) + 1 / (cs * ls) + 1 / (ls * c0)
        a0 = 1 / (cs * rp * ls * c0)
    else:  # Without parallel resistance
        a2 = rs / ls
        a1 = rs / (ls * c0) + 1 / (cs * ls) + 1 / (ls * c0)
        a0 = 1 / (cs * ls * c0)

    # Construct and solve the characteristic polynomial
    x = symbols('x')
    eq = x ** 3 + a2 * x ** 2 + a1 * x + a0
    p_roots = solve(eq, x)

    return [complex(root.evalf()) for root in p_roots]  # Convert roots to complex numbers

