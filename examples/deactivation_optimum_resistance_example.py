from transientbvd import optimum_resistance, select_transducer

# Step 1: Select a predefined transducer
selected_name = "SMBLTD45F28H_28kHz"
transducer = select_transducer(selected_name)
print(f"Selected Transducer:\n{transducer}\n")

# Step 2: Define a resistance range
resistance_range = (10, 5000)  # Resistance range in ohms

# Step 3: Calculate the optimum resistance
optimal_resistance, minimal_decay_time = optimum_resistance(
    transducer, resistance_range
)

# Step 4: Display the results
print("Optimal Resistance Calculation:")
print(f"  Resistance Range: {resistance_range[0]} Ω to {resistance_range[1]} Ω")
print(f"  Optimal Resistance: {optimal_resistance:.2f} Ω")
print(
    f"  Minimal Decay Time: {minimal_decay_time:.6f} s ({minimal_decay_time * 1e3:.2f} ms)"
)
