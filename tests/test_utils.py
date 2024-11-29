import unittest
import random

import numpy as np

from transientbvd.utils import roots

import unittest
import random
from transientbvd.utils import resonance_frequency


class TestRootsMethod(unittest.TestCase):
    def test_valid_roots_no_rp(self):
        """Test roots calculation without parallel resistance (rp=None)."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        rp = None  # No parallel resistance

        # Calculate roots
        result = roots(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Ensure at least 2 roots are returned
        self.assertGreaterEqual(len(result), 2)

        # Ensure all roots are complex numbers
        self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_valid_roots_with_rp(self):
        """Test roots calculation with specific valid parameters."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        rp = 900  # Parallel resistance

        # Calculate roots
        result = roots(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Ensure at least 3 roots are returned
        self.assertGreaterEqual(len(result), 2)

        # Ensure all roots are complex numbers
        self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12

        with self.assertRaises(ValueError):
            roots(rs=-rs, ls=ls, cs=cs, c0=c0)  # Negative rs

        with self.assertRaises(ValueError):
            roots(rs=rs, ls=0, cs=cs, c0=c0)  # Zero ls

        with self.assertRaises(ValueError):
            roots(rs=rs, ls=ls, cs=0, c0=c0)  # Zero cs

        with self.assertRaises(ValueError):
            roots(rs=rs, ls=ls, cs=cs, c0=-c0)  # Negative c0

    def test_root_randomized(self):
        """Test roots calculation with randomized positive non-zero values."""
        for _ in range(100):  # Run 100 randomized tests
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-3, 1e-1)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            rp = random.choice([None, random.uniform(1, 1000)])

            # Calculate roots
            result = roots(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

            # Ensure at least 2 roots are returned
            self.assertGreaterEqual(len(result), 2)

            # Ensure all roots are complex numbers
            self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_fixed_roots_with_rp(self):
        """Test roots calculation for specific parameters with rp = 2 kΩ."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Series capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads
        rp = 2000  # Parallel resistance in ohms

        # Calculate roots
        result = roots(rs=rs, ls=ls, cs=cs, c0=c0, rp=rp)

        # Expected roots (rounded values from the problem statement)
        expected_roots = [
            -112355.43,
            -5461.02 - 263082.45j,
            -5461.02 + 263082.45j
        ]

        # Assert that the number of roots is 3
        self.assertEqual(len(result), 3)

        # Assert that each root matches the expected root within a small tolerance
        for calc_root, expected_root in zip(result, expected_roots):
            self.assertAlmostEqual(calc_root.real, expected_root.real, delta=1e-2)
            self.assertAlmostEqual(calc_root.imag, expected_root.imag, delta=1e-2)


class TestResonanceFrequencyMethod(unittest.TestCase):
    def test_resonance_frequency_basic(self):
        """Test resonance frequency with valid inductance and capacitance."""
        ls = 10e-6  # Inductance in henries
        cs = 1e-12  # Capacitance in farads

        # Calculate resonance frequency
        result = resonance_frequency(ls=ls, cs=cs)

        # Expected resonance frequency
        expected = 1 / (2 * np.pi * (ls * cs) ** 0.5)

        # Assert the result is correct
        self.assertAlmostEqual(result, expected, places=6)

    def test_resonance_frequency_with_full_parameters(self):
        """Test resonance frequency with all BVD parameters."""
        rs = 24.764  # Series resistance in ohms
        ls = 38.959e-3  # Inductance in henries
        cs = 400.33e-12  # Capacitance in farads
        c0 = 3970.1e-12  # Parallel capacitance in farads

        # Calculate resonance frequency
        result = resonance_frequency(rs=rs, ls=ls, cs=cs, c0=c0)

        # Expected resonance frequency
        expected = 1 / (2 * np.pi * (ls * cs) ** 0.5)

        # Assert the result is correct
        self.assertAlmostEqual(result, expected, places=6)

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        ls = 10e-6  # Inductance in henries
        cs = 1e-12  # Capacitance in farads

        with self.assertRaises(ValueError):
            resonance_frequency(ls=-ls, cs=cs)  # Negative ls

        with self.assertRaises(ValueError):
            resonance_frequency(ls=ls, cs=0)  # Zero cs

        rs = 24.764  # Series resistance in ohms
        c0 = 3970.1e-12  # Parallel capacitance in farads

        with self.assertRaises(ValueError):
            resonance_frequency(rs=rs, ls=ls, cs=cs, c0=-c0)  # Negative c0

    def test_randomized_parameters(self):
        """Test resonance frequency with randomized positive non-zero values."""
        for _ in range(100):  # Run 100 randomized tests
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)

            # Calculate resonance frequency
            result = resonance_frequency(ls=ls, cs=cs)

            # Expected resonance frequency
            expected = 1 / (2 * np.pi * (ls * cs) ** 0.5)

            # Assert the result is correct
            self.assertAlmostEqual(result, expected, places=6)

    def test_randomized_full_parameters(self):
        """Test resonance frequency with randomized full BVD parameters."""
        for _ in range(100):  # Run 100 randomized tests
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)

            # Calculate resonance frequency
            result = resonance_frequency(rs=rs, ls=ls, cs=cs, c0=c0)

            # Expected resonance frequency
            expected = 1 / (2 * np.pi * (ls * cs) ** 0.5)

            # Assert the result is correct
            self.assertAlmostEqual(result, expected, places=6)


if __name__ == "__main__":
    unittest.main()
