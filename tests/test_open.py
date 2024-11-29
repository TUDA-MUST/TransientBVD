import logging
import unittest
import random
from transientbvd.open import decay_time


class TestDecayTimeMethod(unittest.TestCase):
    def test_decay_time_without_rp(self):
        """Test decay time calculation without a parallel resistance (rp=None)."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads

        # Calculate decay time without rp
        result = decay_time(rs=rs, ls=ls, cs=cs, c0=c0, rp=None)

        # Expected decay time (τ = 2L / R)
        expected = 2 * ls / rs

        # Assert the result is correct
        self.assertAlmostEqual(result, expected, places=6)

    def test_decay_time_with_rp(self):
        """Test decay time calculation with a parallel resistance (rp provided)."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        rp = 500  # Parallel resistance in ohms

        # Calculate decay time with rp
        result = decay_time(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Ensure the decay time is positive and finite
        self.assertGreater(result, 0)

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12

        with self.assertRaises(ValueError):
            decay_time(rs=-rs, ls=ls, cs=cs, c0=c0)  # Negative rs

        with self.assertRaises(ValueError):
            decay_time(rs=rs, ls=0, cs=cs, c0=c0)  # Zero ls

        with self.assertRaises(ValueError):
            decay_time(rs=rs, ls=ls, cs=0, c0=c0)  # Zero cs

        with self.assertRaises(ValueError):
            decay_time(rs=rs, ls=ls, cs=cs, c0=-c0)  # Negative c0

        with self.assertRaises(ValueError):
            decay_time(rs=rs, ls=ls, cs=cs, c0=c0, rp=-100)  # Negative rp

    def test_randomized_parameters(self):
        """Test decay time with randomized positive non-zero values."""
        for _ in range(100):  # Run 100 randomized tests
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            rp = random.choice([None, random.uniform(10, 1000)])

            # Calculate decay time
            result = decay_time(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

            # Ensure the decay time is positive and finite
            self.assertGreater(result, 0)
            self.assertNotEqual(result, float("inf"))

    def test_edge_case_high_rp(self):
        """Test decay time calculation for a very high parallel resistance."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        rp = 1e6  # Very high parallel resistance

        # Calculate decay time
        result = decay_time(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Ensure decay time is finite
        self.assertGreater(result, 0)
        self.assertNotEqual(result, float("inf"))


import unittest
from transientbvd.open import optimum_resistance
from unittest.mock import patch
import random


class TestOptimumResistanceWithHints(unittest.TestCase):
    def test_optimum_resistance_basic(self):
        """Test optimum resistance calculation with valid parameters."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        resistance_range = (10, 1000)  # Resistance range in ohms

        # Calculate optimal resistance
        optimal_resistance, minimal_decay_time = optimum_resistance(
            rs, ls, cs, c0, resistance_range
        )

        # Assert the optimal resistance is within the given range
        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])

        # Assert the decay time is positive
        self.assertGreater(minimal_decay_time, 0)

    def test_hint_near_lower_bound(self):
        """Test hint is printed when optimal resistance is near the lower bound."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (10, 100)

        # Mock decay_time to force the optimizer to return a value near the lower bound
        with patch("transientbvd.open.decay_time", side_effect=lambda *args, **kwargs: kwargs["rp"]):
            with self.assertLogs(level="INFO") as log:
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
        resistance_range = (10, 100)

        # Mock decay_time to force the optimizer to return a value near the upper bound
        with patch("transientbvd.open.decay_time", side_effect=lambda *args, **kwargs: -kwargs["rp"]):
            with self.assertLogs(level="INFO") as log:
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
            optimum_resistance(-rs, ls, cs, c0, resistance_range)  # Negative rs

        with self.assertRaises(ValueError):
            optimum_resistance(rs, 0, cs, c0, resistance_range)  # Zero ls

        with self.assertRaises(ValueError):
            optimum_resistance(rs, ls, 0, c0, resistance_range)  # Zero cs

        with self.assertRaises(ValueError):
            optimum_resistance(rs, ls, cs, -c0, resistance_range)  # Negative c0

        with self.assertRaises(ValueError):
            optimum_resistance(rs, ls, cs, c0, (1000, 10))  # Invalid range (lower >= upper)

    def test_randomized_parameters(self):
        """Test optimum resistance with randomized positive non-zero values."""
        for _ in range(100):  # Run 100 randomized tests
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            resistance_range = (random.uniform(1, 10), random.uniform(50, 1000))

            # Ensure the range is valid
            if resistance_range[0] >= resistance_range[1]:
                continue

            # Calculate optimal resistance
            optimal_resistance, minimal_decay_time = optimum_resistance(
                rs, ls, cs, c0, resistance_range
            )

            # Assert the optimal resistance is within the given range
            self.assertGreaterEqual(optimal_resistance, resistance_range[0])
            self.assertLessEqual(optimal_resistance, resistance_range[1])

            # Assert the decay time is positive
            self.assertGreater(minimal_decay_time, 0)

    def test_fixed_optimal_resistance(self):
        """Test that the optimal resistance is correctly calculated for fixed parameters."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        resistance_range = (10, 1000)  # Resistance range in ohms

        # Calculate optimal resistance
        optimal_resistance, _ = optimum_resistance(rs, ls, cs, c0, resistance_range)

        # Assert the calculated optimal resistance is close to the expected value (~900 ohms)
        self.assertAlmostEqual(optimal_resistance, 900, delta=20)

    def test_edge_case_tight_range(self):
        """Test behavior when the resistance range is very narrow."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (499, 501)  # Tight range around 500 ohms

        # Calculate optimal resistance
        optimal_resistance, minimal_decay_time = optimum_resistance(
            rs, ls, cs, c0, resistance_range
        )

        # Assert the optimal resistance is within the given range
        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])

        # Assert the decay time is positive
        self.assertGreater(minimal_decay_time, 0)

    def test_edge_case_large_range(self):
        """Test behavior when the resistance range is very large."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        resistance_range = (10, 1e5)  # Large range

        # Calculate optimal resistance
        optimal_resistance, minimal_decay_time = optimum_resistance(
            rs, ls, cs, c0, resistance_range
        )

        # Assert the optimal resistance is within the given range
        self.assertGreaterEqual(optimal_resistance, resistance_range[0])
        self.assertLessEqual(optimal_resistance, resistance_range[1])

        # Assert the decay time is positive
        self.assertGreater(minimal_decay_time, 0)


if __name__ == "__main__":
    unittest.main()
