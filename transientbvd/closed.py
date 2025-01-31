from typing import Tuple, Optional
import numpy as np
import math


def closed_current(
    t: float,
    ucw: float,
    rs: float,
    ls: float,
    cs: float,
    c0: Optional[float],
    ub: Optional[float] = None,
    t_sw: Optional[float] = None
) -> float:
    """
    Compute the transient current response for a closed circuit (BVD model).

    Initially applying a boost voltage amplitude (U_b) accelerates the current rise,
    reaching the desired steady-state current faster. After this initial phase,
    the voltage is reduced to the operating level voltage amplitude (U_cw) for continuous wave mode.

    Parameters
    ----------
    t : float
        Time in seconds. If `np.inf` is provided, this returns the steady-state current (U_cw / R_s).
    ucw : float
        Operating (continuous-wave) voltage amplitude in volts. Must be > 0.
    rs : float
        Series resistance in ohms. Must be > 0.
    ls : float
        Inductance in henries. Must be > 0.
    cs : float
        Series capacitance in farads. Must be > 0.
    c0 : float, optional
        Parallel capacitance in farads. If provided, must be > 0.
    ub : float, optional
        Overboost voltage amplitude in volts. If provided, must be > 0 and > ucw.
    t_sw : float, optional
        Switching time in seconds. If provided, must be > 0. If not provided but ub is given,
        it is computed via `switching_time`.

    Returns
    -------
    float
        The transient current at time t.
        - If t == np.inf, returns the steady-state current (ucw / rs).
        - If overboosting is used and t < t_sw, uses ub.
        - If overboosting is used and t >= t_sw, switches to ucw with continuity.
        - Otherwise, uses only ucw from t=0.

    Raises
    ------
    ValueError
        If t_sw is provided without ub (invalid usage).
    AssertionError
        If any of rs, ls, cs, c0, ucw, or ub (when provided) are <= 0.
        If ub <= ucw.
        If t_sw <= 0.
        If t < 0.
    """
    # Basic parameter checks
    assert ucw > 0, "ucw must be positive."
    assert rs > 0, "rs must be positive."
    assert ls > 0, "ls must be positive."
    assert cs > 0, "cs must be positive."
    if c0 is not None:
        assert c0 > 0, "c0 must be positive if provided."
    if ub is not None:
        assert ub > 0, "ub must be positive if provided."
        assert ub > ucw, "ub must be greater than ucw."
    if t_sw is not None:
        assert t_sw > 0, "t_sw must be positive if provided."

    # Validate overboost usage
    if ub is None and t_sw is not None:
        raise ValueError("Either 'ub' must be provided for overboosting, or 't_sw' must be None.")

    # If overboosting is specified but no switching time, compute the optimal one
    if ub is not None and t_sw is None:
        t_sw = switching_time(ub, ucw, rs, ls)
        print("Hint: Using optimal switching time t_sw =", t_sw)

    # Convert array-like times to float
    if isinstance(t, (np.ndarray, list)):
        t = float(t[0])

    # Steady-state current if t == np.inf
    if np.isinf(t):
        return abs(ucw / rs)  # absolute in case ucw or rs were negative, but we assert > 0, so just "ucw / rs" is fine
    else:
        assert t >= 0, "Time must be non-negative."

    # Fundamental parameters
    w_r = 1.0 / math.sqrt(ls * cs)
    tau = 2.0 * ls / rs

    # Overboost logic
    if ub is not None and t_sw is not None:
        # If we're before the switching time, use U_b
        if t < t_sw:
            return (ub / rs) * math.cos(w_r * t) * (1 - math.exp(-t / tau))
        else:
            # After switching time, ensure continuity
            amp_t_sw = (ub / rs) * (1 - math.exp(-t_sw / tau))
            phase_offset = w_r * t_sw
            return (
                amp_t_sw
                * math.exp(-(t - t_sw) / tau)
                * math.cos(w_r * (t - t_sw) + phase_offset)
                + (ucw / rs)
                * math.cos(w_r * (t - t_sw) + phase_offset)
                * (1 - math.exp(-(t - t_sw) / tau))
            )

    # Default case (no overboosting)
    return (ucw / rs) * math.cos(w_r * t) * (1 - math.exp(-t / tau))


def switching_time(
    ub: float,
    ucw: float,
    rs: float,
    ls: float
) -> float:
    """
    Calculate the switching time for the transient response.

    Initially applying a boost voltage amplitude U_b accelerates the current rise,
    allowing the transducer to reach the desired steady-state current faster.
    After this initial phase, the voltage is reduced to the operating level voltage amplitude U_cw.

    Parameters
    ----------
    ub : float
        Overboost voltage amplitude in volts (U_b). Must be > 0.
    ucw : float
        Continuous-wave voltage amplitude in volts (U_cw). Must be > 0.
    rs : float
        Series resistance in ohms. Must be > 0.
    ls : float
        Inductance in henries. Must be > 0.

    Returns
    -------
    float
        Switching time in seconds for optimal transition from U_b to U_cw.

    Raises
    ------
    ValueError
        If ub <= ucw, since the logarithm would be invalid or meaningless.
    AssertionError
        If any parameter is <= 0.
    """
    # Basic parameter checks
    assert ub > 0, "ub must be positive."
    assert ucw > 0, "ucw must be positive."
    assert rs > 0, "rs must be positive."
    assert ls > 0, "ls must be positive."

    # Raise ValueError if ub <= ucw
    if ub <= ucw:
        raise ValueError("U_b must be greater than U_cw for a valid calculation.")

    tau = 2.0 * ls / rs
    return -tau * math.log(1.0 - (ucw / ub))


def closed_4tau(
    ucw: float,
    rs: float,
    ls: float,
    cs: float,
    c0: Optional[float] = None,
    ub: Optional[float] = None,
    t_sw: Optional[float] = None
) -> float:
    """
    Calculate the time at which the oscillation amplitude first reaches 98.2% of the steady-state current.

    This is often referred to as the 4τ time, where the system has achieved approximately 98.2%
    of its final amplitude for a damped oscillation.

    Parameters
    ----------
    ucw : float
        Continuous-wave voltage amplitude in volts. Must be > 0.
    rs : float
        Series resistance in ohms. Must be > 0.
    ls : float
        Inductance in henries. Must be > 0.
    cs : float
        Series capacitance in farads. Must be > 0.
    c0 : float, optional
        Parallel capacitance in farads. If provided, must be > 0.
    ub : float, optional
        Overboost voltage amplitude in volts. If provided, must be > 0 and > ucw.
    t_sw : float, optional
        Switching time in seconds. If provided, must be > 0.

    Returns
    -------
    float
        The time in seconds at which the current amplitude first reaches 98.2% of U_cw / R_s.
    """
    # Basic parameter checks
    assert ucw > 0, "ucw must be positive."
    assert rs > 0, "rs must be positive."
    assert ls > 0, "ls must be positive."
    assert cs > 0, "cs must be positive."
    if c0 is not None:
        assert c0 > 0, "c0 must be positive if provided."
    if ub is not None:
        assert ub > 0, "ub must be positive if provided."
        if ub <= ucw:
            raise ValueError("U_b must be greater than U_cw for a valid calculation.")
    if t_sw is not None:
        assert t_sw > 0, "t_sw must be positive if provided."

    tau = 2.0 * ls / rs
    steady_state_current = ucw / rs
    threshold = 0.982 * steady_state_current  # 98.2% threshold -> 4tau

    # Possibly compute t_sw if ub is given but not specified
    if ub is not None and t_sw is None:
        t_sw = switching_time(ub, ucw, rs, ls)

    if ub is not None and t_sw is not None:
        amp_t_sw = (ub / rs) * (1 - math.exp(-t_sw / tau))

        # only ub is applied, t_sw perfectly switches
        if amp_t_sw == threshold:
            return t_sw

        # ub is applied and at t_sw, the current amplitude is greater than threshold -> only need to consider ub
        if amp_t_sw > threshold:
            t_reached = -tau * math.log(1.0 - (threshold * rs / ub))
            return float(t_reached)

        # ub is applied and at t_sw, the current amplitude is less than threshold -> we need to consider both ub and ucw
        else:
            t_reached = tau * math.log(
                (ub * math.exp(t_sw / tau) - ub - ucw * math.exp(t_sw / tau)) / (rs * threshold - ucw))
            return float(t_reached)

    # No overboost scenario
    t_reached = -tau * math.log(1.0 - (threshold * rs / ucw))
    return float(t_reached)


def closed_potential(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    ucw: float,
    ub: float
) -> Tuple[float, float, float, float, float]:
    """
    Evaluate the potential improvement in transient response time when using overboosting.

    Parameters
    ----------
    rs : float
        Series resistance in ohms. Must be > 0.
    ls : float
        Inductance in henries. Must be > 0.
    cs : float
        Series capacitance in farads. Must be > 0.
    c0 : float
        Parallel capacitance in farads. Must be > 0.
    ucw : float
        Continuous-wave voltage amplitude in volts. Must be > 0.
    ub : float
        Overboost voltage amplitude in volts. Must be > ucw.

    Returns
    -------
    Tuple[float, float, float, float, float]
        (1) t_sw: The switching time in seconds.
        (2) tau_no_boost: The 4τ duration without overboosting.
        (3) tau_with_boost: The 4τ duration with overboosting.
        (4) delta_time: Absolute improvement in seconds.
        (5) percentage_improvement: Percentage improvement in transient response time.
    """
    # Parameter checks
    assert rs > 0, "rs must be positive."
    assert ls > 0, "ls must be positive."
    assert cs > 0, "cs must be positive."
    assert c0 > 0, "c0 must be positive."
    assert ucw > 0, "ucw must be positive."
    if ub <= ucw:
        raise ValueError("U_b must be greater than U_cw for a valid calculation.")

    t_sw = switching_time(ub, ucw, rs, ls)
    tau_no_boost = closed_4tau(ucw, rs, ls, cs, c0)
    tau_with_boost = closed_4tau(ucw, rs, ls, cs, c0, ub, t_sw)

    delta_time = tau_no_boost - tau_with_boost
    if tau_no_boost > 0:
        percentage_improvement = (delta_time / tau_no_boost) * 100.0
    else:
        percentage_improvement = 0.0

    return t_sw, tau_no_boost, tau_with_boost, delta_time, percentage_improvement


def print_closed_potential(
    rs: float,
    ls: float,
    cs: float,
    c0: float,
    ucw: float,
    ub: float
) -> None:
    """
    Pretty print the results of the closed-circuit overboosting potential analysis.

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
    ucw : float
        Continuous-wave voltage amplitude in volts.
    ub : float
        Overboost voltage amplitude in volts.
    """
    t_sw, tau_no_boost, tau_with_boost, delta_time, percentage_improvement = closed_potential(
        rs, ls, cs, c0, ucw, ub
    )

    print("=" * 50)
    print("Closed-Circuit Overboosting Potential Analysis")
    print("=" * 50)
    print(f"Series Resistance (Rs): {rs:.2f} Ω")
    print(f"Inductance (Ls): {ls:.6e} H")
    print(f"Series Capacitance (Cs): {cs:.6e} F")
    print(f"Parallel Capacitance (C0): {c0:.6e} F")
    print("-" * 50)
    print(f"Switching Time (t_sw): {t_sw:.6f} s ({t_sw * 1e3:.2f} ms)")
    print(f"4τ without Overboosting: {tau_no_boost:.6f} s ({tau_no_boost * 1e3:.2f} ms)")
    print(f"4τ with Overboosting: {tau_with_boost:.6f} s ({tau_with_boost * 1e3:.2f} ms)")
    print(f"Absolute Time Improvement: {delta_time:.6f} s ({delta_time * 1e3:.2f} ms)")
    print(f"Percentage Time Improvement: {percentage_improvement:.2f}%")
    print("=" * 50)
