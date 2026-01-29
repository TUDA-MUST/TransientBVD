from transientbvd import select_transducer, deactivation_tau, deactivation_two_tau

# Step 1: Select a predefined transducer
selected_name = "SMBLTD45F28H_28kHz"
transducer = select_transducer(selected_name)
print(f"Selected Transducer:\n{transducer}\n")

# Step 2: Calculate τ (tau) and 2τ (two tau) without parallel resistance (rp=None)
tau_no_rp = deactivation_tau(transducer)
two_tau_no_rp = deactivation_two_tau(transducer)

print("Decay Times without Parallel Resistance (rp=None):")
print(f"  τ (Tau): {tau_no_rp:.6f} s ({tau_no_rp * 1e3:.2f} ms)")
print(f"  2τ (Two Tau): {two_tau_no_rp:.6f} s ({two_tau_no_rp * 1e3:.2f} ms)\n")

# Step 3: Calculate τ (tau) and 2τ (two tau) with a specified parallel resistance (rp=950 Ω)
rp = 900  # Parallel resistance in ohms
tau_with_rp = deactivation_tau(transducer, rp)
two_tau_with_rp = deactivation_two_tau(transducer, rp)

print(f"Decay Times with Parallel Resistance (rp={rp} Ω):")
print(f"  τ (Tau): {tau_with_rp:.6f} s ({tau_with_rp * 1e3:.2f} ms)")
print(f"  2τ (Two Tau): {two_tau_with_rp:.6f} s ({two_tau_with_rp * 1e3:.2f} ms)")
