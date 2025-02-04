"""
TransientBVD - Closed Circuit Transient Analysis

This module contains functions for analyzing the closed-circuit transient
response of resonant circuits modeled by the Butterworth-Van Dyke (BVD)
equivalent circuit.
"""

from typing import Tuple, Optional
import math

import numpy as np

from transientbvd.transducer import Transducer


def print_closed_potential(transducer: Transducer, ucw: float, ub: float) -> None:
    """
    Pretty print the results of the closed-circuit overboosting potential analysis.

    Parameters
    ----------
    transducer : Transducer
        The transducer containing the circuit parameters.
    ucw : float
        Continuous-wave voltage amplitude in volts.
    ub : float
        Overboost voltage amplitude in volts.
    """
    t_sw, tau_no_boost, tau_with_boost, delta_time, percentage_improvement = (
        closed_potential(transducer, ucw, ub)
    )

    print("=" * 50)
    print("Closed-Circuit Overboosting Potential Analysis")
    print("=" * 50)

    print(transducer)

    print(f"Switching Time (t_sw): {t_sw:.6f} s ({t_sw * 1e3:.2f} ms)")
    print(
        f"4τ without Overboosting: {tau_no_boost:.6f} s ({tau_no_boost * 1e3:.2f} ms)"
    )
    print(
        f"4τ with Overboosting: {tau_with_boost:.6f} s ({tau_with_boost * 1e3:.2f} ms)"
    )
    print(f"Absolute Time Improvement: {delta_time:.6f} s ({delta_time * 1e3:.2f} ms)")
    print(f"Percentage Time Improvement: {percentage_improvement:.2f}%")
    print("=" * 50)


def closed_potential(
    transducer: Transducer, ucw: float, ub: float
) -> Tuple[float, float, float, float, float]:
    """
    Evaluate the potential improvement in transient response time when using overboosting.

    Parameters
    ----------
    transducer : Transducer
        The transducer containing the circuit parameters.
    ucw : float
        Continuous-wave voltage amplitude in volts.
    ub : float
        Overboost voltage amplitude in volts.

    Returns
    -------
    Tuple[float, float, float, float, float]
        (t_sw, tau_no_boost, tau_with_boost, delta_time, percentage_improvement).
    """
    # Validate input parameters
    assert ucw > 0, "ucw must be positive."
    if ub <= ucw:
        raise ValueError("ub must be greater than ucw.")

    t_sw = switching_time(transducer, ub, ucw)
    tau_no_boost = closed_4tau(transducer, ucw)
    tau_with_boost = closed_4tau(transducer, ucw, ub, t_sw)

    delta_time = tau_no_boost - tau_with_boost
    percentage_improvement = (
        (delta_time / tau_no_boost) * 100 if tau_no_boost > 0 else 0.0
    )

    return t_sw, tau_no_boost, tau_with_boost, delta_time, percentage_improvement


def closed_current(
    t: float,
    transducer: Transducer,
    ucw: float,
    ub: Optional[float] = None,
    t_sw: Optional[float] = None,
) -> float:
    """
    Compute the transient current response for a closed circuit (BVD model).

    Parameters
    ----------
    t : float
        Time in seconds. If `np.inf` is provided, this returns the
        steady-state current (`U_cw / R_s`).
    transducer : Transducer
        The transducer containing the circuit parameters.
    ucw : float
        Operating (continuous-wave) voltage amplitude in volts. Must be > 0.
    ub : float, optional
        Overboost voltage amplitude in volts. If provided, must be > 0 and > `U_cw`.
    t_sw : float, optional
        Switching time in seconds. If provided, must be > 0.
        If not provided but `ub` is given, it is computed via `switching_time`.

    Returns
    -------
    float
        The transient current at time `t`.
    """

    assert t >= 0, "Time must be non-negative."

    # Extract circuit parameters
    rs, ls, cs = transducer.rs, transducer.ls, transducer.cs

    # Validate input parameters
    assert ucw > 0, "ucw must be positive."
    assert rs > 0 and ls > 0 and cs > 0, "Circuit parameters must be positive."

    if t == np.inf:
        return abs(ucw / rs)

    if ub is not None:
        assert ub > ucw, "ub must be greater than ucw."
    if t_sw is not None:
        if ub is None:
            raise ValueError("t_sw cannot be provided without ub.")
        assert t_sw > 0, "t_sw must be positive."

    # Compute switching time if needed
    if ub is not None and t_sw is None:
        t_sw = switching_time(transducer, ub, ucw)

    # Compute response
    w_r = 1.0 / math.sqrt(ls * cs)
    tau = 2.0 * ls / rs

    if ub is not None and t_sw is not None:
        if t < t_sw:
            return (ub / rs) * math.cos(w_r * t) * (1 - math.exp(-t / tau))

        # else t >= t_sw
        amp_t_sw = (ub / rs) * (1 - math.exp(-t_sw / tau))
        phase_offset = w_r * t_sw
        return amp_t_sw * math.exp(-(t - t_sw) / tau) * math.cos(
            w_r * (t - t_sw) + phase_offset
        ) + (ucw / rs) * math.cos(w_r * (t - t_sw) + phase_offset) * (
            1 - math.exp(-(t - t_sw) / tau)
        )

    return (ucw / rs) * math.cos(w_r * t) * (1 - math.exp(-t / tau))


def switching_time(transducer: Transducer, ub: float, ucw: float) -> float:
    """
    Calculate the switching time for the transient response.

    Parameters
    ----------
    transducer : Transducer
        The transducer containing the circuit parameters.
    ub : float
        Overboost voltage amplitude in volts.
    ucw : float
        Continuous-wave voltage amplitude in volts.

    Returns
    -------
    float
        Switching time in seconds.
    """
    rs, ls = transducer.rs, transducer.ls

    assert ucw > 0, "ucw must be positive."
    assert ub > 0, "ub must be positive."
    if ub <= ucw:
        raise ValueError("ub must be greater than ucw.")
    assert rs > 0 and ls > 0, "Circuit parameters must be positive."

    tau = 2.0 * ls / rs
    return -tau * math.log(1.0 - (ucw / ub))


def closed_4tau(
    transducer: Transducer,
    ucw: float,
    ub: Optional[float] = None,
    t_sw: Optional[float] = None,
) -> float:
    """
    Calculate the time at which the oscillation amplitude first reaches
    98.2% of the steady-state current.

    Parameters
    ----------
    transducer : Transducer
        The transducer containing the circuit parameters.
    ucw : float
        Continuous-wave voltage amplitude in volts.
    ub : float, optional
        Overboost voltage amplitude in volts.
    t_sw : float, optional
        Switching time in seconds.

    Returns
    -------
    float
        The 4τ time in seconds.
    """
    rs, ls, cs, _ = transducer.rs, transducer.ls, transducer.cs, transducer.c0

    assert ucw > 0, "ucw must be positive."
    assert rs > 0 and ls > 0 and cs > 0, "Circuit parameters must be positive."
    if ub is not None:
        assert ub > 0, "ub must be positive."
        if ub <= ucw:
            raise ValueError("ub must be greater than ucw.")

    if ub is not None and t_sw is None:
        t_sw = switching_time(transducer, ub, ucw)

    tau = 2.0 * ls / rs
    steady_state_current = ucw / rs
    threshold = 0.982 * steady_state_current  # 98.2% threshold -> 4τ

    if ub is not None and t_sw is not None:
        amp_t_sw = (ub / rs) * (1 - math.exp(-t_sw / tau))
        if amp_t_sw >= threshold:
            return t_sw
        return tau * math.log(
            (ub * math.exp(t_sw / tau) - ub - ucw * math.exp(t_sw / tau))
            / (rs * threshold - ucw)
        )

    return -tau * math.log(1.0 - (threshold * rs / ucw))
