# basic_example.py
from transientbvd import Transducer, print_open_potential
from transientbvd.closed import print_closed_potential

# Define the BVD model parameters and create a transducer instance
transducer = Transducer(
    rs=24.764,  # Series resistance in ohms
    ls=38.959e-3,  # Inductance in henries
    cs=400.33e-12,  # Series capacitance in farads
    c0=3970.1e-12,  # Parallel capacitance in farads
)

# Define resistance range for open potential analysis
resistance_range = (10, 1000)  # Range of resistances to evaluate in ohms

# Analyze open-circuit transient response
print_open_potential(transducer, resistance_range)

# Use a boost voltage of 20V and a continuous wave voltage of 10V
print_closed_potential(transducer, ucw=10.0, ub=20.0)
