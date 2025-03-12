import math
import random
import unittest
import numpy as np

from transientbvd.utils import resonance_frequency, roots


class TestRootsMethod(unittest.TestCase):
    def setUp(self):
        """Setup default parameters for tests."""
        self.rs = 24.764  # ohms
        self.ls = 38.959e-3  # henries
        self.cs = 400.33e-12  # farads
        self.c0 = 3970.1e-12  # farads

    def test_valid_roots_no_rp(self):
        """Test roots calculation without parallel resistance (rp=None)."""
        result = roots(self.rs, self.ls, self.cs, self.c0)
        # For a 3rd order polynomial, we expect exactly 3 roots.
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_valid_roots_with_rp(self):
        """Test roots calculation with a specified parallel resistance."""
        rp = 900  # ohms
        result = roots(self.rs, self.ls, self.cs, self.c0, rp)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_invalid_parameters_missing(self):
        """Test that missing parameters (None) raise a ValueError."""
        with self.assertRaises(ValueError):
            roots(None, self.ls, self.cs, self.c0)
        with self.assertRaises(ValueError):
            roots(self.rs, None, self.cs, self.c0)
        with self.assertRaises(ValueError):
            roots(self.rs, self.ls, None, self.c0)
        with self.assertRaises(ValueError):
            roots(self.rs, self.ls, self.cs, None)

    def test_invalid_parameters_non_positive(self):
        """Test that non-positive parameter values raise a ValueError."""
        with self.assertRaises(ValueError):
            roots(-1, self.ls, self.cs, self.c0)
        with self.assertRaises(ValueError):
            roots(self.rs, 0, self.cs, self.c0)
        with self.assertRaises(ValueError):
            roots(self.rs, self.ls, -0.0001, self.c0)
        with self.assertRaises(ValueError):
            roots(self.rs, self.ls, self.cs, 0)

    def test_invalid_rp_non_positive(self):
        """Test that non-positive rp raises a ValueError."""
        with self.assertRaises(ValueError):
            roots(self.rs, self.ls, self.cs, self.c0, rp=-100)
        with self.assertRaises(ValueError):
            roots(self.rs, self.ls, self.cs, self.c0, rp=0)

    def test_randomized_roots(self):
        """Test roots calculation with randomized positive non-zero values."""
        for _ in range(100):
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-3, 1e-1)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            rp = random.choice([None, random.uniform(1, 1000)])
            result = roots(rs, ls, cs, c0, rp)
            self.assertEqual(len(result), 3)
            self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_extremely_small_values(self):
        """Test roots calculation with extremely small positive values."""
        rs = 1e-3
        ls = 1e-6
        cs = 1e-12
        c0 = 1e-12
        result = roots(rs, ls, cs, c0)
        self.assertEqual(len(result), 3)
        for r in result:
            self.assertFalse(math.isinf(r.real))
            self.assertFalse(math.isnan(r.real))

    def test_extremely_large_values(self):
        """Test roots calculation with extremely large parameter values."""
        rs = 1e2
        ls = 10
        cs = 1e-3
        c0 = 1e-3
        rp = 1e4
        result = roots(rs, ls, cs, c0, rp)
        self.assertEqual(len(result), 3)
        for r in result:
            self.assertFalse(math.isinf(r.real))
            self.assertFalse(math.isnan(r.real))

    def test_difference_with_and_without_rp(self):
        """Test that the roots change when a parallel resistor is provided
        compared to the deactivation scenario."""
        result_no_rp = roots(self.rs, self.ls, self.cs, self.c0, rp=None)
        result_with_rp = roots(self.rs, self.ls, self.cs, self.c0, rp=500)
        # The two sets of roots should not be identical.
        self.assertNotEqual(result_no_rp, result_with_rp)

    def test_known_case_with_rp(self):
        """Test roots calculation for a specific known case with rp = 2000 Ω."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        rp = 2000
        result = roots(rs, ls, cs, c0, rp)
        self.assertEqual(len(result), 3)
        # Verify the sum of roots equals -a2 (from Vieta's formula)
        a2 = rs / ls + 1 / (rp * c0)
        sum_roots = sum(result)
        self.assertAlmostEqual(sum_roots.real, float(-a2), delta=1e-2)


class TestResonanceFrequencyMethod(unittest.TestCase):
    def test_resonance_frequency_basic(self):
        """Test resonance frequency calculation."""
        ls = 10e-6
        cs = 1e-12
        result = resonance_frequency(ls, cs)
        expected = 1 / (2 * np.pi * (ls * cs) ** 0.5)
        self.assertAlmostEqual(result, expected, places=6)

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        with self.assertRaises(ValueError):
            resonance_frequency(-10e-6, 1e-12)
        with self.assertRaises(ValueError):
            resonance_frequency(10e-6, -1e-12)

    def test_randomized_resonance_frequency(self):
        """Test resonance frequency with randomized positive values."""
        for _ in range(100):
            ls = random.uniform(1e-6, 1e-3)
            cs = random.uniform(1e-12, 1e-6)
            result = resonance_frequency(ls, cs)
            expected = 1 / (2 * np.pi * (ls * cs) ** 0.5)
            self.assertAlmostEqual(result, expected, places=6)


if __name__ == "__main__":
    unittest.main()
