import logging
import random
import unittest
from unittest.mock import patch

from transientbvd import tau_decay, two_tau_decay, optimum_resistance, open_potential, print_open_potential

logging.basicConfig(level=logging.WARNING)

class TestPrintOpenPotential(unittest.TestCase):
    @patch("builtins.print")  # Mock the print function
    def test_print_open_potential(self, mock_print):
        """Test that print_open_potential runs without errors."""
        rs = 21.05  # Series resistance in ohms
        ls = 35.15e-3  # Inductance in henries
        cs = 448.62e-12  # Series capacitance in farads
        c0 = 4075.69e-12  # Parallel capacitance in farads
        resistance_range = (10, 5000)  # Resistance range in ohms

        # Call the method
        print_open_potential(rs, ls, cs, c0, resistance_range)

        # Assert that print was called at least once
        self.assertTrue(mock_print.called)

class TestOpenPotentialMethod(unittest.TestCase):
    def test_open_potential_basic_case(self):
        """Test open_potential with valid parameters."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        resistance_range = (10, 5000)  # Resistance range in ohms

        # Calculate potential improvement
        optimal_resistance, tau_with_rp, delta_time, percentage_improvement = open_potential(
            rs, ls, cs, c0, resistance_range
        )

        # Assert values are reasonable and within expected ranges
        self.assertGreater(optimal_resistance, resistance_range[0])
        self.assertLess(optimal_resistance, resistance_range[1])
        self.assertGreater(tau_with_rp, 0)
        self.assertGreater(delta_time, 0)
        self.assertGreater(percentage_improvement, 0)

    def test_open_potential_speed_improvement(self):
        """
        Test potential improvement for specific parameters:
        rs = 21.05, ls = 35.15e-3, cs = 448.62e-12, c0 = 4075.69e-12, rp = 950.
        Expect decay to be 21 times faster.
        """
        rs = 21.05  # Series resistance in ohms
        ls = 35.15e-3  # Inductance in henries
        cs = 448.62e-12  # Series capacitance in farads
        c0 = 4075.69e-12  # Parallel capacitance in farads
        resistance_range = (10, 1000)  # Resistance range in ohms

        # Calculate potential improvement
        optimal_resistance, tau_with_rp, delta_time, percentage_improvement = open_potential(
            rs, ls, cs, c0, resistance_range
        )

        # Expected decay time without rp (τ_no_rp)
        tau_no_rp = 2 * ls / rs

        # Assert speed improvement
        expected_speedup = tau_no_rp / tau_with_rp

        self.assertAlmostEqual(expected_speedup, 24, delta=1)

    def test_open_potential_fixed_case(self):
        """Test potential improvement for a specific fixed case."""
        rs = 21.05  # Series resistance in ohms
        ls = 35.15e-3  # Inductance in henries
        cs = 448.62e-12  # Series capacitance in farads
        c0 = 4075.69e-12  # Parallel capacitance in farads
        resistance_range = (10, 1000)  # Resistance range in ohms

        # Calculate potential improvement
        optimal_resistance, tau_with_rp, delta_time, percentage_improvement = open_potential(
            rs, ls, cs, c0, resistance_range
        )

        # Assert specific expected values
        self.assertAlmostEqual(optimal_resistance, 950, delta=50)  # Optimal resistance ~950 ohms
        self.assertGreater(tau_with_rp, 0)
        self.assertGreater(delta_time, 0)
        self.assertGreater(percentage_improvement, 0)

class TestDecayTimeMethod(unittest.TestCase):
    def test_tau_decay_without_rp(self):
        """Test tau decay time calculation without a parallel resistance (rp=None)."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads

        # Calculate decay time without rp
        result = tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=None)

        # Expected decay time (τ = 2L / R)
        expected = 2 * ls / rs

        # Assert the result is correct
        self.assertAlmostEqual(result, expected, places=6)

    def test_tau_decay_with_rp(self):
        """Test tau decay time calculation with a parallel resistance (rp provided)."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        rp = 500  # Parallel resistance in ohms

        # Calculate decay time with rp
        result = tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Ensure the decay time is positive and finite
        self.assertGreater(result, 0)
        self.assertNotEqual(result, float("inf"))

    def test_two_tau_decay_no_rp(self):
        """
        Test two_tau_decay for specific parameters without a parallel resistance (rp=None):
        rs = 21.05, ls = 35.15e-3, cs = 448.62e-12, c0 = 4075.69e-12.
        """
        rs = 21.05  # Series resistance in ohms
        ls = 35.15e-3  # Inductance in henries
        cs = 448.62e-12  # Series capacitance in farads
        c0 = 4075.69e-12  # Parallel capacitance in farads

        # Calculate two_tau without rp
        result = two_tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=None)

        # Expected result is approximately 6.3 ms
        expected = 2 * (2 * ls / rs)  # Two tau without rp is 2 * (2 * L / R)

        # Assert the result is within an acceptable range
        self.assertAlmostEqual(result, expected, delta=1e-4)  # Tolerance of 0.1 ms

    def test_two_tau_decay_with_various_rp(self):
        """
        Test two_tau_decay for specific parameters with different parallel resistances (rp).
        rs = 21.05, ls = 35.15e-3, cs = 448.62e-12, c0 = 4075.69e-12.
        """
        rs = 21.05  # Series resistance in ohms
        ls = 35.15e-3  # Inductance in henries
        cs = 448.62e-12  # Series capacitance in farads
        c0 = 4075.69e-12  # Parallel capacitance in farads

        test_cases = [
            {"rp": 100, "expected": 1.25e-3},  # 100 ohms -> ~1.25 ms
            {"rp": 950, "expected": 0.298e-3},  # 950 ohms -> ~0.298 ms
            {"rp": 10_000, "expected": 1.37e-3}  # 10,000 ohms -> ~1.37 ms
        ]

        for case in test_cases:
            with self.subTest(rp=case["rp"]):
                rp = case["rp"]
                expected = case["expected"]

                # Calculate two_tau with given rp
                result = two_tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

                # Assert the result is within an acceptable range
                self.assertAlmostEqual(result, expected, delta=1e-4)  # Tolerance of 0.1 ms

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12

        with self.assertRaises(ValueError):
            tau_decay(rs=-rs, ls=ls, cs=cs, c0=c0)  # Negative rs

        with self.assertRaises(ValueError):
            tau_decay(rs=rs, ls=0, cs=cs, c0=c0)  # Zero ls

        with self.assertRaises(ValueError):
            tau_decay(rs=rs, ls=ls, cs=0, c0=c0)  # Zero cs

        with self.assertRaises(ValueError):
            tau_decay(rs=rs, ls=ls, cs=cs, c0=-c0)  # Negative c0

        with self.assertRaises(ValueError):
            tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=-100)  # Negative rp

    def test_randomized_parameters(self):
        """Test tau decay time with randomized positive non-zero values."""
        for _ in range(100):  # Run 100 randomized tests
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            rp = random.choice([None, random.uniform(10, 1000)])

            # Calculate decay time
            result = tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

            # Ensure the decay time is positive and finite
            self.assertGreater(result, 0)
            self.assertNotEqual(result, float("inf"))

    def test_edge_case_high_rp(self):
        """Test tau decay time calculation for a very high parallel resistance."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        rp = 1e6  # Very high parallel resistance

        # Calculate decay time
        result = tau_decay(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Ensure decay time is finite
        self.assertGreater(result, 0)
        self.assertNotEqual(result, float("inf"))

class TestOptimumResistance(unittest.TestCase):
    def test_optimum_resistance_basic(self):
        """Test optimum resistance calculation with valid parameters."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        resistance_range = (10, 1000)  # Resistance range in ohms

        optimal_resistance, minimal_decay_time = optimum_resistance(
            rs, ls, cs, c0, resistance_range
        )

        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])
        self.assertGreater(minimal_decay_time, 0)

    def test_hint_near_lower_bound(self):
        """Test hint is printed when optimal resistance is near the lower bound."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (10000, 100000)

        # Bias the decay time to favor the lower bound
        with patch("transientbvd.tau_decay", side_effect=lambda rs, ls, cs, c0, rp: rp + 1e-6):
            with self.assertLogs(level="WARNING") as log:
                optimum_resistance(rs, ls, cs, c0, resistance_range)
                self.assertTrue(
                    any("near the lower bound" in message for message in log.output)
                )

    def test_hint_near_upper_bound(self):
        """Test hint is printed when optimal resistance is near the upper bound."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (10, 50)

        with patch("transientbvd.tau_decay", side_effect=lambda rs, ls, cs, c0, rp: -rp):
            with self.assertLogs(level="WARNING") as log:
                optimum_resistance(rs, ls, cs, c0, resistance_range)
                self.assertTrue(
                    any("near the upper bound" in message for message in log.output)
                )

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (10, 1000)

        with self.assertRaises(ValueError):
            optimum_resistance(-rs, ls, cs, c0, resistance_range)

        with self.assertRaises(ValueError):
            optimum_resistance(rs, 0, cs, c0, resistance_range)

        with self.assertRaises(ValueError):
            optimum_resistance(rs, ls, 0, c0, resistance_range)

        with self.assertRaises(ValueError):
            optimum_resistance(rs, ls, cs, -c0, resistance_range)

        with self.assertRaises(ValueError):
            optimum_resistance(rs, ls, cs, c0, (1000, 10))

    def test_randomized_parameters(self):
        """Test optimum resistance with randomized positive non-zero values."""
        for _ in range(10):
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            resistance_range = (random.uniform(1, 10), random.uniform(50, 1000))

            if resistance_range[0] >= resistance_range[1]:
                continue

            optimal_resistance, minimal_decay_time = optimum_resistance(
                rs, ls, cs, c0, resistance_range
            )

            self.assertGreaterEqual(optimal_resistance, resistance_range[0])
            self.assertLessEqual(optimal_resistance, resistance_range[1])
            self.assertGreater(minimal_decay_time, 0)

    def test_fixed_optimal_resistance(self):
        """Test that the optimal resistance is correctly calculated for fixed parameters."""
        rs = 21.05  # Series resistance in ohms
        ls = 35.15e-3  # Inductance in henries
        cs = 448.62e-12  # Series capacitance in farads
        c0 = 4075.69e-12  # Parallel capacitance in farads
        resistance_range = (10, 1000)

        optimal_resistance, _ = optimum_resistance(rs, ls, cs, c0, resistance_range)
        print("Optimal resistance: ", optimal_resistance)
        self.assertAlmostEqual(optimal_resistance, 923, delta=20)

    def test_edge_case_tight_range(self):
        """Test behavior when the resistance range is very narrow."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (499, 501)

        optimal_resistance, minimal_decay_time = optimum_resistance(
            rs, ls, cs, c0, resistance_range
        )

        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])
        self.assertGreater(minimal_decay_time, 0)

    def test_edge_case_large_range(self):
        """Test behavior when the resistance range is very large."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (10, 1e5)

        optimal_resistance, minimal_decay_time = optimum_resistance(
            rs, ls, cs, c0, resistance_range
        )

        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])
        self.assertGreater(minimal_decay_time, 0)


if __name__ == "__main__":
    unittest.main()
