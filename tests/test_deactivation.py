import logging
import random
import unittest
from unittest.mock import patch

import numpy as np

from transientbvd import (
    deactivation_tau,
    deactivation_two_tau,
    optimum_resistance,
    deactivation_potential,
    print_deactivation_potential,
    deactivation_current,
)
from transientbvd.transducer import Transducer

logging.basicConfig(level=logging.WARNING)


class TestPrintDeactivationPotential(unittest.TestCase):
    @patch("builtins.print")  # Mock the print function
    def test_print_deactivation_potential(self, mock_print):
        """Test that print_deactivation_potential runs without errors."""
        transducer = Transducer(
            name="TestTransducer", rs=21.05, ls=35.15e-3, cs=448.62e-12, c0=4075.69e-12
        )
        resistance_range = (10, 5000)  # Resistance range in ohms

        # Call the method
        print_deactivation_potential(transducer, resistance_range)

        # Assert that print was called at least once
        self.assertTrue(mock_print.called)


class TestDeactivationPotentialMethod(unittest.TestCase):
    def test_deactivation_potential_basic_case(self):
        """Test deactivation_potential with valid parameters."""
        transducer = Transducer(
            name="TestTransducer", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )
        resistance_range = (10, 5000)  # Resistance range in ohms

        # Calculate potential improvement
        optimal_resistance, tau_with_rp, delta_time, percentage_improvement = (
            deactivation_potential(transducer, resistance_range)
        )

        # Assert values are reasonable and within expected ranges
        self.assertGreater(optimal_resistance, resistance_range[0])
        self.assertLess(optimal_resistance, resistance_range[1])
        self.assertGreater(tau_with_rp, 0)
        self.assertGreater(delta_time, 0)
        self.assertGreater(percentage_improvement, 0)


class TestDecayTimeMethod(unittest.TestCase):
    def test_deactivation_tau_without_rp(self):
        """Test deactivation_tau calculation without a parallel resistance (rp=None)."""
        transducer = Transducer(
            name="TestTransducer", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )

        # Calculate decay time without rp
        result = deactivation_tau(transducer)

        # Expected decay time (τ = 2L / R)
        expected = 2 * transducer.ls / transducer.rs

        # Assert the result is correct
        self.assertAlmostEqual(result, expected, places=6)


class TestOptimumResistance(unittest.TestCase):
    def test_optimum_resistance_basic(self):
        """Test optimum_resistance calculation with valid parameters."""
        transducer = Transducer(
            name="TestTransducer", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )
        resistance_range = (10, 1000)  # Resistance range in ohms

        optimal_resistance, minimal_decay_time = optimum_resistance(
            transducer, resistance_range
        )

        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])
        self.assertGreater(minimal_decay_time, 0)


class TestDeactivationCurrent(unittest.TestCase):
    def setUp(self):
        """Setup default parameters for transducer tests."""
        self.transducer = Transducer(
            name="TestTransducer",
            rs=21.05,
            ls=35.15e-3,
            cs=448.62e-12,
            c0=4075.69e-12,
            rp=1000,  # Default parallel resistance
        )

    def test_deactivation_current_t_zero(self):
        """Test deactivation_current at t=0 should return exactly i0."""
        i0 = 1.0
        result = deactivation_current(0, i0, self.transducer)
        self.assertAlmostEqual(result, i0, places=6)

    def test_deactivation_current_open_circuit_t_zero(self):
        """Open-circuit (MOSFET opens): at t=0 the current must equal i0."""
        self.transducer.rp = None  # MOSFET open => open circuit
        i0 = 1.0
        result = deactivation_current(0.0, i0, self.transducer)
        self.assertAlmostEqual(result, i0, places=6)

    def test_deactivation_current_open_circuit_envelope_decays(self):
        """Open-circuit (MOSFET opens): ringdown envelope must decay over time.

        We avoid sign flips from oscillation by comparing the max(|i(t)|) in an
        early window vs a late window.
        """
        self.transducer.rp = None  # MOSFET open => open circuit
        i0 = 1.0

        # Use windows relative to tau ~ 2L/R (few ms for the default transducer)
        t_early = np.linspace(0.0, 1e-3, 200)  # 0 .. 1 ms
        t_late = np.linspace(10e-3, 20e-3, 400)  # 10 .. 20 ms

        early_vals = np.array(
            [deactivation_current(float(t), i0, self.transducer) for t in t_early])
        late_vals = np.array(
            [deactivation_current(float(t), i0, self.transducer) for t in t_late])

        early_max = float(np.max(np.abs(early_vals)))
        late_max = float(np.max(np.abs(late_vals)))

        # Sanity: early window should still be "near" the initial amplitude
        self.assertGreater(early_max, 0.5)

        # Envelope should decay strongly by 10-20 ms (many taus for this device)
        self.assertLess(late_max, early_max * 0.2)

        # Also ensure we didn't accidentally create a (nearly) constant current solution
        self.assertGreater(early_max - late_max, 0.1)

    def test_deactivation_current_large_t(self):
        """Test deactivation_current for large t (t → ∞) should return ~0."""
        i0 = 1.0
        result = deactivation_current(10, i0, self.transducer)  # t = 10s
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_deactivation_current_zero_i0(self):
        """Test deactivation_current with i0=0 should always return 0."""
        result = deactivation_current(1e-3, 0.0, self.transducer)  # Any time value
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_deactivation_current_high_resistance(self):
        """Test deactivation_current with very high rs to simulate deactivation condition."""
        self.transducer.rs = 1e6  # Extremely high series resistance
        i0 = 1.0
        result = deactivation_current(10e-3, i0, self.transducer)  # t = 10ms
        self.assertAlmostEqual(result, 0.0, delta=1e-3)  # Allow small numerical errors

    def test_deactivation_current_large_rp(self):
        """Test deactivation_current with a very high rp (should behave like rp=None)."""
        self.transducer.rp = 1e9  # Very large parallel resistance
        i0 = 1.0
        result = deactivation_current(1e-3, i0, self.transducer)
        self.assertNotEqual(result, float("inf"))
        self.assertNotEqual(result, float("nan"))

    def test_deactivation_current_unstable(self):
        """Test deactivation_current should raise an error if the system is unstable."""
        self.transducer.rs = -5  # Negative resistance (non-physical case)
        i0 = 1.0
        with self.assertRaises(ValueError):
            deactivation_current(1e-3, i0, self.transducer)

    def test_deactivation_current_known_case_long_time(self):
        """Test deactivation_current for known transducer values at t=100ms
        (should decay to near zero)."""
        transducer = Transducer(
            name="RealTransducer2", rs=15.0, ls=20e-3, cs=600e-12, c0=4e-9, rp=1500
        )
        i0 = 1.0
        t = 100e-3  # 100ms

        # Compute expected decay approximation manually
        tau = (2 * transducer.ls) / transducer.rs  # Approximation
        expected_i = i0 * np.exp(-t / tau)

        result = deactivation_current(t, i0, transducer)
        self.assertAlmostEqual(result, expected_i, delta=1e-6)


if __name__ == "__main__":
    unittest.main()
