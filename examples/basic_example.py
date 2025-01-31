# basic_example.py
from transientbvd import print_open_potential
from transientbvd.closed import print_closed_potential


def main():
    # Define the BVD model parameters
    rs = 24.764  # Series resistance in ohms
    ls = 38.959e-3  # Inductance in henries
    cs = 400.33e-12  # Series capacitance in farads
    c0 = 3970.1e-12  # Parallel capacitance in farads
    resistance_range = (10, 1000)  # Range of resistances to evaluate in ohms

    # Use print_open_potential to display analysis
    print_open_potential(rs, ls, cs, c0, resistance_range)

    # use a boost voltage of 20V and a continuous wave voltage of 10V
    print_closed_potential(rs, ls, cs, c0, ucw=10.0, ub=20.0)

if __name__ == "__main__":
    main()
