import numpy as np
import matplotlib.pyplot as plt
from transientbvd import predefined_transducer, tau_decay

def plot_decay_time_vs_resistance():
    # Step 1: Select a predefined transducer
    selected_name = "SMBLTD45F40H_1"
    transducer = predefined_transducer(selected_name)
    print(f"Selected Transducer: {transducer}\n")

    # Step 2: Define the range of resistance values
    rp_values = np.logspace(1, 4, 100)  # Logarithmic scale from 10 Ω to 10,000 Ω

    # Step 3: Calculate decay times for each resistance value
    decay_times = [
        tau_decay(
            rs=transducer.rs,
            ls=transducer.ls,
            cs=transducer.cs,
            c0=transducer.c0,
            rp=rp
        )
        for rp in rp_values
    ]

    # Step 4: Plot Decay Time vs Resistance
    plt.figure(figsize=(8, 6))
    plt.plot(rp_values, decay_times, label="Decay Time (τ)", linewidth=2)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Parallel Resistance (rp) [Ω]")
    plt.ylabel("Decay Time (τ) [s]")
    plt.title("Decay Time vs Parallel Resistance")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_decay_time_vs_resistance()
