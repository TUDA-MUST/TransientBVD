# __init__.py

# Import submodules
from . import open

# Optionally import specific methods or classes directly
from .open import potential, decay_time, optimum_resistance
# from .closed import transient_voltage_closed

# Import rest of methods directly
from .transducer import predefined_transducer, predefined_transducers, Transducer
from .utils import roots
