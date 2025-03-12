# basic_example.py
from transientbvd import print_deactivation_potential, predefined_transducers, select_transducer
from transientbvd.activation import print_activation_potential

# Step 1: List all predefined transducers
print("Available predefined transducers:")
transducer_names = predefined_transducers()
for name in transducer_names:
    print(f"  - {name}")

print("\n")

# Step 2: Select a transducer by name and print its details
selected_name = "Custom"  # Change to another name if desired
transducer = select_transducer(selected_name)

# Use __str__ to print transducer details
print(f"Details of selected transducer:\n{transducer}")


# Deactivation: Define resistance range for deactivation potential analysis
resistance_range = (1, 10000)  # Range of resistances to evaluate in ohms
print_deactivation_potential(transducer, resistance_range)

# Activation: Use a boost voltage of 20V and a continuous wave voltage of 10V
print_activation_potential(transducer, ucw=20.0, ub=40)
