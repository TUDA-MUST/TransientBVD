import unittest
import random
from transientbvd.utils import roots


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
        rp = 500  # Parallel resistance

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


if __name__ == "__main__":
    unittest.main()
