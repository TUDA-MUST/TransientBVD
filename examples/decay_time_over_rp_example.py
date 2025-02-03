import numpy as np
import matplotlib.pyplot as plt
from transientbvd import select_transducer, open_two_tau

# Step 1: Select a predefined transducer
selected_name = "SMBLTD45F40H_1"
transducer = select_transducer(selected_name)
print(f"Selected Transducer:\n{transducer}\n")

# Step 2: Define the range of resistance values
rp_values = np.logspace(1, 4, 100)  # Logarithmic scale from 10 Ω to 10,000 Ω

# Step 3: Calculate decay times for each resistance value
decay_times = [open_two_tau(transducer, rp) for rp in rp_values]

# Step 4: Plot Decay Time vs Resistance
plt.figure(figsize=(8, 6))
plt.plot(rp_values, decay_times, label="Decay Time (2τ)", linewidth=2)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Parallel Resistance (Rp) [Ω]")
plt.ylabel("Decay Time (τ) [s]")
plt.title("Decay Time vs Parallel Resistance")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend()
plt.show()