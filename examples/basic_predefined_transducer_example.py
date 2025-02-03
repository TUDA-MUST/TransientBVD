from transientbvd import predefined_transducers, select_transducer

# Step 1: List all predefined transducers
print("Available predefined transducers:")
transducer_names = predefined_transducers()
for name in transducer_names:
    print(f"  - {name}")

print("\n")

# Step 2: Select a transducer by name and print its details
selected_name = "SMBLTD45F40H_1"  # Change to another name if desired
transducer = select_transducer(selected_name)

# Use __str__ to print transducer details
print(f"Details of selected transducer:\n{transducer}")

# Step 3: Print the equivalent circuit parameters using built-in pretty print
print("\nEquivalent Circuit Parameters:")
print(transducer)

# Step 4: Access individual parameters (since Transducer inherits EquivalentCircuitParams)
print("\nAccessing individual circuit parameters:")
print(f"  rs = {transducer.rs:.4f} Ω")
print(f"  ls = {transducer.ls:.6f} H")
print(f"  cs = {transducer.cs:.2e} F")
print(f"  c0 = {transducer.c0:.2e} F")

# If the transducer has an optional parallel resistance (rp)
if transducer.rp:
    print(f"  rp = {transducer.rp:.2f} Ω")

# Step 5: Print resonance frequency
print(f"\nResonance Frequency: {transducer.frequency:.2f} Hz")
