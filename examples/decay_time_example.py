from transientbvd import select_transducer, open_tau, open_two_tau

# Step 1: Select a predefined transducer
selected_name = "SMBLTD45F40H_1"
transducer = select_transducer(selected_name)
print(f"Selected Transducer:\n{transducer}\n")

# Step 2: Calculate τ (tau) and 2τ (two tau) without parallel resistance (rp=None)
tau_no_rp = open_tau(transducer)
two_tau_no_rp = open_two_tau(transducer)

print("Decay Times without Parallel Resistance (rp=None):")
print(f"  τ (Tau): {tau_no_rp:.6f} s ({tau_no_rp * 1e3:.2f} ms)")
print(f"  2τ (Two Tau): {two_tau_no_rp:.6f} s ({two_tau_no_rp * 1e3:.2f} ms)\n")

# Step 3: Calculate τ (tau) and 2τ (two tau) with a specified parallel resistance (rp=950 Ω)
rp = 950  # Parallel resistance in ohms
tau_with_rp = open_tau(transducer, rp)
two_tau_with_rp = open_two_tau(transducer, rp)

print("Decay Times with Parallel Resistance (rp=950 Ω):")
print(f"  τ (Tau): {tau_with_rp:.6f} s ({tau_with_rp * 1e3:.2f} ms)")
print(f"  2τ (Two Tau): {two_tau_with_rp:.6f} s ({two_tau_with_rp * 1e3:.2f} ms)")
