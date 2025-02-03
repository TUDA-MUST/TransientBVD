from transientbvd import predefined_transducers, predefined_transducer


# Step 1: List all predefined transducers
print("Available predefined transducers:")
transducer_names = predefined_transducers()
for name in transducer_names:
    print(f"  - {name}")

print("\n")

# Step 2: Select a transducer by name and print its details
selected_name = "SMBLTD45F40H_1"  # Change to another name if desired
print(f"Details of selected transducer: {selected_name}")
transducer = predefined_transducer(selected_name)

# Use __str__ to print transducer details
print(transducer)

# Use .parameters() to get the transducer parameters
print("\nCore parameters (rs, ls, cs, c0):")
rs, ls, cs, c0 = transducer.parameters()
print(f"  rs = {rs:.4f} Ω")
print(f"  ls = {ls:.6f} H")
print(f"  cs = {cs:.2e} F")
print(f"  c0 = {c0:.2e} F")

