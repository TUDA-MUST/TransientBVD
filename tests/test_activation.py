import unittest
from unittest.mock import patch
import numpy as np

from transientbvd.activation import (
    activation_potential,
    print_activation_potential,
    activation_4tau,
    switching_time,
    activation_current,
)
from transientbvd.transducer import Transducer


class TestActivationCurrent(unittest.TestCase):
    """Tests for the activation_current function."""

    def setUp(self):
        """Setup a default transducer for testing."""
        self.transducer = Transducer(
            name="TestTransducer", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )

    def test_activation_current_no_overboost(self):
        """Test activation_current without overboost (ub=None)."""
        ucw = 40.0
        t_small = 0.0005

        # 1) Small time
        i_small = activation_current(t=t_small, transducer=self.transducer, ucw=ucw)
        self.assertGreater(i_small, 0.0)
        self.assertLess(i_small, ucw / self.transducer.rs)

        # 2) t->inf should reach steady state (ucw/rs)
        i_inf = activation_current(t=np.inf, transducer=self.transducer, ucw=ucw)
        self.assertAlmostEqual(i_inf, ucw / self.transducer.rs, places=7)

    def test_activation_current_with_overboost(self):
        """Test activation_current with overboost."""
        ucw = 30.0
        ub = 45.0
        t_sw = switching_time(self.transducer, ub, ucw)

        # t < t_sw => underboost steady-state
        t_before = 0.001
        i_before = activation_current(t_before, self.transducer, ucw, ub, t_sw)
        self.assertLess(i_before, 0.0)
        self.assertLess(i_before, ub / self.transducer.rs)

        # t >= t_sw => switch to ucw steady-state
        t_after = 0.003
        i_after = activation_current(t_after, self.transducer, ucw, ub, t_sw)
        self.assertGreater(i_after, 0.0)

    def test_activation_current_inf(self):
        """t = np.inf should return steady-state current: ucw / rs."""
        i_inf = activation_current(t=np.inf, transducer=self.transducer, ucw=25)
        self.assertAlmostEqual(i_inf, 25 / self.transducer.rs, places=7)

    def test_activation_current_invalid_usage(self):
        """Test assertion errors for invalid inputs."""
        # Negative time
        with self.assertRaises(AssertionError):
            activation_current(t=-0.001, transducer=self.transducer, ucw=40)

        # ub <= ucw
        with self.assertRaises(AssertionError):
            activation_current(
                t=0.001, transducer=self.transducer, ucw=40, ub=30, t_sw=0.002
            )

        # Negative ub
        with self.assertRaises(AssertionError):
            activation_current(
                t=0.001, transducer=self.transducer, ucw=40, ub=-45, t_sw=0.002
            )

        # t_sw given but no ub
        with self.assertRaises(ValueError):
            activation_current(t=0.001, transducer=self.transducer, ucw=40, t_sw=0.001)


class TestSwitchingTime(unittest.TestCase):
    """Tests for the switching_time function."""

    def setUp(self):
        """Setup transducer for switching time tests."""
        self.transducer = Transducer(
            name="SwitchTest", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )

    def test_switching_time_basic(self):
        """Valid case: ub > ucw => positive time."""
        ub = 60.0
        ucw = 40.0

        result = switching_time(self.transducer, ub, ucw)
        self.assertGreater(result, 0.0)

    def test_switching_time_invalid_ub_le_ucw(self):
        """Invalid case: ub <= ucw should raise ValueError."""
        with self.assertRaises(ValueError):
            switching_time(self.transducer, ub=30, ucw=40)

    def test_switching_time_asserts(self):
        """Negative or zero parameters => AssertionError."""
        with self.assertRaises(AssertionError):
            switching_time(self.transducer, ub=-10, ucw=20)
        with self.assertRaises(AssertionError):
            switching_time(self.transducer, ub=10, ucw=-20)


class TestActivation4Tau(unittest.TestCase):
    """Tests for the activation_4tau function."""

    def setUp(self):
        """Setup transducer for activation_4tau tests."""
        self.transducer = Transducer(
            name="TauTest", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )

    def test_activation_4tau_no_overboost(self):
        """No overboost => expecting a time near 4 * tau."""
        ucw = 40.0

        result = activation_4tau(self.transducer, ucw)
        expected_approx = 4.0 * (2 * self.transducer.ls / self.transducer.rs)
        self.assertAlmostEqual(result, expected_approx, delta=5e-4)

    def test_activation_4tau_overboost(self):
        """Overboost scenario: 4τ should be equal or smaller than t_sw."""
        ucw = 30.0
        ub = 60.0
        t_sw = switching_time(self.transducer, ub, ucw)

        res = activation_4tau(self.transducer, ucw, ub, t_sw)

        # The transient should settle equal or before t_sw
        self.assertLessEqual(res, t_sw)

    def test_activation_4tau_assertions(self):
        """Negative or zero parameters => AssertionError, ub <= ucw => ValueError."""
        with self.assertRaises(AssertionError):
            activation_4tau(self.transducer, ucw=-10)
        with self.assertRaises(ValueError):
            activation_4tau(self.transducer, ucw=20, ub=10)


class TestActivationPotential(unittest.TestCase):
    """Tests for activation_potential and print_activation_potential."""

    def setUp(self):
        """Setup transducer for activation_potential tests."""
        self.transducer = Transducer(
            name="PotentialTest", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
        )

    def test_activation_potential_basic(self):
        """Check t_sw, tau_no_boost, tau_with_boost, delta_time, pct_improvement."""
        ucw = 40.0
        ub = 60.0

        t_sw, tau_no_boost, tau_with_boost, delta_time, pct_improvement = (
            activation_potential(self.transducer, ucw, ub)
        )
        self.assertGreater(t_sw, 0)
        self.assertGreater(tau_no_boost, 0)
        self.assertGreater(tau_with_boost, 0)
        self.assertGreater(delta_time, 0)
        self.assertGreater(pct_improvement, 0)

    @patch("builtins.print")
    def test_print_activation_potential(self, mock_print):
        """Ensure print_activation_potential calls print at least once."""
        ucw = 40.0
        ub = 60.0

        print_activation_potential(self.transducer, ucw, ub)
        self.assertTrue(mock_print.called)

    def test_activation_potential_asserts(self):
        """Check invalid parameters trigger AssertionError or ValueError."""
        with self.assertRaises(AssertionError):
            activation_potential(self.transducer, ucw=-10, ub=60)
        with self.assertRaises(ValueError):
            activation_potential(self.transducer, ucw=20, ub=10)  # ub <= ucw


if __name__ == "__main__":
    unittest.main()
