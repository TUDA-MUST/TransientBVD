"""
plot_closed_current_example.py

This script plots the closed-circuit transient current response from the
TransientBVD library. It compares:
1. The overboost approach (using switching time).
2. The default approach (only continuous-wave voltage).
"""

import numpy as np
import matplotlib.pyplot as plt
from transientbvd import select_transducer
from transientbvd.closed import closed_current, closed_4tau


def plot_closed_current(
    timestamps: list[float],
    transducer,
    ucw: float,
    ub: float | None = None,
    t_sw: float | None = None,
) -> None:
    """
    Plot the transient current response over time for a closed circuit using the BVD model.

    If 'ub' is given, plots two lines:
      1) Overboost approach (from 0 to t_sw with Ub, then switching to Ucw).
      2) Default approach (only Ucw from t=0).
    Adds lines for:
      - Steady-state current (horizontal)
      - 4τ time for both the overboosted and non-overboosted scenarios (vertical lines)
      - Switching time t_sw if provided.

    Parameters
    ----------
    timestamps : list[float]
        Time points (seconds) for evaluating the current.
    transducer : Transducer
        The transducer object containing the equivalent circuit parameters.
    ucw : float
        Continuous-wave voltage (volts).
    ub : float, optional
        Overboost voltage (volts). If None, no overboost is applied.
    t_sw : float, optional
        Switching time (seconds). If None, and 'ub' is given, an optimal switching time
        can be calculated internally by `switching_time`.
    """
    # 1) Evaluate currents for the overboost approach (if ub is given) or default approach
    currents_overboost = [
        closed_current(t, transducer, ucw, ub, t_sw) for t in timestamps
    ]

    # 2) Plot results
    plt.figure(figsize=(8, 5))
    label_overboost = (
        "Transient Current using overboost"
        if ub
        else "Transient Current (No Overboost)"
    )
    plt.plot(timestamps, currents_overboost, label=label_overboost, color="b")

    # 3) Add the steady-state current reference
    steady_state_current = ucw / transducer.rs
    plt.axhline(
        y=steady_state_current, color="r", linestyle="--", label="Steady-State Current"
    )

    # 4) If ub is specified, also plot the scenario without any overboost
    if ub is not None:
        # Currents if only UCW is applied from t=0
        currents_no_boost = [closed_current(t, transducer, ucw) for t in timestamps]
        plt.plot(
            timestamps,
            currents_no_boost,
            label="Transient Current (Only U_cw)",
            color="orange",
            linestyle="dashed",
        )

    # 5) Plot the 4τ time for the overboost approach (or single approach if no ub)
    t_4tau_overboost = closed_4tau(transducer, ucw, ub, t_sw)
    plt.axvline(
        x=t_4tau_overboost, color="black", linestyle="--", label="4τ (Overboost)"
    )

    # 6) If ub is specified, also show the 4τ time for no overboost
    if ub is not None:
        t_4tau_no_boost = closed_4tau(transducer, ucw)
        plt.axvline(
            x=t_4tau_no_boost, color="g", linestyle="dashed", label="4τ (Only U_cw)"
        )

    # 7) If switching time is given, visualize it
    if t_sw is not None:
        plt.axvline(x=t_sw, color="black", linestyle="solid", label="Switching Time")

    # 8) Final plot formatting
    plt.xlabel("Time (s)")
    plt.ylabel("Current (A)")
    plt.title("Closed-Circuit Transient Current Response Example")
    plt.legend()
    plt.grid()
    plt.show()


def main():
    """
    Demonstrates usage of the 'plot_closed_current' function.
    """
    # Step 1: Select a predefined transducer
    selected_name = "SMBLTD45F40H_1"
    transducer = select_transducer(selected_name)
    print(f"Selected Transducer:\n{transducer}\n")

    # Example parameters (modify as needed):
    ucw = 40.0
    ub = 60.0

    # Example timestamps
    timestamps = np.linspace(0, 0.020, 10000).tolist()

    # Optional switching time
    t_sw = 0.003  # 3 ms

    # Run the plotting function
    plot_closed_current(
        timestamps=timestamps, transducer=transducer, ucw=ucw, ub=ub, t_sw=t_sw
    )


if __name__ == "__main__":
    main()
