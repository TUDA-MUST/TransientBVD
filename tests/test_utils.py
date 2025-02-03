import random
import unittest
import numpy as np

from transientbvd.utils import resonance_frequency, roots
from transientbvd import Transducer


class TestRootsMethod(unittest.TestCase):
    def setUp(self):
        """Setup default parameters for transducer tests."""
        self.transducer = Transducer(
            rs=24.764,
            ls=38.959e-3,
            cs=400.33e-12,
            c0=3970.1e-12
        )

    def test_valid_roots_no_rp(self):
        """Test roots calculation without parallel resistance (rp=None)."""
        result = roots(self.transducer.rs, self.transducer.ls, self.transducer.cs, self.transducer.c0)
        self.assertGreaterEqual(len(result), 2)
        self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_valid_roots_with_rp(self):
        """Test roots calculation with specific valid parameters."""
        self.transducer.set_rp(900)
        result = roots(self.transducer.rs, self.transducer.ls, self.transducer.cs, self.transducer.c0, self.transducer.rp)
        self.assertGreaterEqual(len(result), 2)
        self.assertTrue(all(isinstance(root, complex) for root in result))

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        with self.assertRaises(ValueError):
            roots(-10, self.transducer.ls, self.transducer.cs, self.transducer.c0)
        with self.assertRaises(ValueError):
            roots(self.transducer.rs, 0, self.transducer.cs, self.transducer.c0)
        with self.assertRaises(ValueError):
            roots(self.transducer.rs, self.transducer.ls, 0, self.transducer.c0)

    def test_randomized_roots(self):
        """Test roots calculation with randomized positive non-zero values."""
        for _ in range(100):
            rs = random.uniform(1, 100)
            ls = random.uniform(1e-3, 1e-1)
            cs = random.uniform(1e-12, 1e-6)
            c0 = random.uniform(1e-12, 1e-6)
            rp = random.choice([None, random.uniform(1, 1000)])
            result = roots(rs, ls, cs, c0, rp)
            self.assertGreaterEqual(len(result), 2)
            self.assertTrue(all(isinstance(root, complex) for root in result))


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
