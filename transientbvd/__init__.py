# __init__.py
"""
TransientBVD: A library for analyzing transient behavior in the Butterworth-Van Dyke (BVD) model.
"""

# deactivation.py
from .deactivation import (
    deactivation_potential,
    print_deactivation_potential,
    deactivation_tau,
    deactivation_two_tau,
    optimum_resistance,
    deactivation_current,
)

# activation.py
from .activation import (
    activation_current,
    switching_time,
    activation_4tau,
    activation_potential,
    print_activation_potential,
)

# transducer.py
from .transducer import (
    Transducer,
    load_transducers,
    select_transducer,
    predefined_transducers,
)

# utils.py
from .utils import (
    resonance_frequency,
    roots,
)

# Define an __all__ so that `from transientbvd import *` will only import these symbols
__all__ = [
    # From deactivation.py
    "deactivation_potential",
    "print_deactivation_potential",
    "deactivation_tau",
    "deactivation_two_tau",
    "optimum_resistance",
    "deactivation_current",
    # From activation.py
    "activation_current",
    "switching_time",
    "activation_4tau",
    "activation_potential",
    "print_activation_potential",
    # From transducer.py
    "Transducer",
    "load_transducers",
    "select_transducer",
    "predefined_transducers",
    # From utils.py
    "resonance_frequency",
    "roots",
]
