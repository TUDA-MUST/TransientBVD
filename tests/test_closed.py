import unittest
from unittest.mock import patch
import numpy as np

from transientbvd.closed import closed_potential, print_closed_potential, closed_4tau, switching_time, closed_current


class TestClosedCurrent(unittest.TestCase):
    """Tests for the closed_current function."""

    def test_closed_current_no_overboost(self):
        """
        Test closed_current without overboost (ub=None).

        Checks a small t yields a lower current than steady-state,
        and t->inf returns steady-state current.
        """
        ucw = 40.0
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12

        # 1) Small time
        t_small = 0.0005
        i_small = closed_current(
            t=t_small, ucw=ucw, rs=rs, ls=ls, cs=cs, c0=c0
        )
        self.assertGreater(i_small, 0.0)
        self.assertLess(i_small, ucw / rs)

        # 2) t->inf
        i_inf = closed_current(
            t=np.inf, ucw=ucw, rs=rs, ls=ls, cs=cs, c0=c0
        )
        self.assertAlmostEqual(i_inf, ucw / rs, places=7)

    def test_closed_current_with_overboost(self):
        """
        Test closed_current with overboost:
          - t < t_sw => uses ub
          - t >= t_sw => continuity + ucw
        """
        t_sw = 0.002
        ucw = 30.0
        ub = 45.0
        rs = 21.05
        ls = 35.15e-3
        cs = 448.62e-12
        c0 = 4075.69e-12

        # t < t_sw => overboost
        t_before = 0.001
        i_before = closed_current(t_before, ucw, rs, ls, cs, c0, ub, t_sw)
        self.assertGreater(i_before, 0.0)
        self.assertLess(i_before, ub / rs)

        # t >= t_sw => switch to ucw
        t_after = 0.003
        i_after = closed_current(t_after, ucw, rs, ls, cs, c0, ub, t_sw)
        self.assertGreater(i_after, 0.0)

    def test_closed_current_inf(self):
        """
        t = np.inf => returns abs(ucw / rs).
        (Though we assert positivity, so effectively ucw/rs.)
        """
        i_inf = closed_current(
            t=np.inf, ucw=25, rs=20, ls=30e-3, cs=300e-12, c0=4000e-12
        )
        self.assertAlmostEqual(i_inf, 25/20, places=7)

    def test_closed_current_negative_time(self):
        """Check assertion if user provides negative t."""
        with self.assertRaises(AssertionError):
            closed_current(
                t=-0.001, ucw=40, rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12
            )

    def test_closed_current_invalid_usage(self):
        """
        - ub <= ucw => AssertionError
        - ub or other params <= 0 => AssertionError
        - t_sw > 0 but ub=None => ValueError
        """
        # ub <= ucw
        with self.assertRaises(AssertionError):
            closed_current(t=0.001, ucw=40, rs=24.764, ls=38.959e-3, cs=400.33e-12,
                           c0=3970.1e-12, ub=30, t_sw=0.002)
        # ub < 0
        with self.assertRaises(AssertionError):
            closed_current(t=0.001, ucw=40, rs=24.764, ls=38.959e-3, cs=400.33e-12,
                           c0=3970.1e-12, ub=-45, t_sw=0.002)
        # t_sw but no ub
        with self.assertRaises(ValueError):
            closed_current(t=0.001, ucw=40, rs=24.764, ls=38.959e-3, cs=400.33e-12,
                           c0=3970.1e-12, ub=None, t_sw=0.001)


class TestSwitchingTime(unittest.TestCase):
    """Tests for the switching_time function."""

    def test_switching_time_basic(self):
        """Check valid scenario with ub > ucw => positive time."""
        ub = 60.0
        ucw = 40.0
        rs = 24.764
        ls = 38.959e-3

        result = switching_time(ub, ucw, rs, ls)
        self.assertGreater(result, 0.0)

    def test_switching_time_invalid_ub_le_ucw(self):
        """
        If ub <= ucw => ValueError per docstring.
        """
        with self.assertRaises(ValueError):
            switching_time(ub=30, ucw=40, rs=24.764, ls=38.959e-3)

    def test_switching_time_asserts(self):
        """Test negative or zero parameters => AssertionError."""
        # Negative rs
        with self.assertRaises(AssertionError):
            switching_time(ub=60, ucw=40, rs=-1, ls=1e-3)
        # Negative ls
        with self.assertRaises(AssertionError):
            switching_time(ub=60, ucw=40, rs=20, ls=-1e-3)
        # ub or ucw <= 0
        with self.assertRaises(AssertionError):
            switching_time(ub=-10, ucw=20, rs=10, ls=1e-3)
        with self.assertRaises(AssertionError):
            switching_time(ub=10, ucw=-20, rs=10, ls=1e-3)


class TestClosed4Tau(unittest.TestCase):
    """Tests for the closed_4tau function."""

    def test_closed_4tau_no_overboost(self):
        """
        With no overboost => expecting a time near 4 * tau
        for a typical RLC.
        """
        ucw = 40.0
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12

        result = closed_4tau(ucw, rs, ls, cs, c0)
        expected_approx = 4.0 * (2 * ls / rs)
        self.assertAlmostEqual(result, expected_approx, delta=5e-4)

    def test_closed_4tau_overboost_below_threshold(self):
        """
        If amplitude at t_sw < threshold, we solve the only-ub portion.
        """
        ucw = 30.0
        rs = 20.0
        ls = 35e-3
        cs = 200e-12
        c0 = None
        ub = 32.0
        t_sw = 0.001

        res = closed_4tau(ucw, rs, ls, cs, c0, ub, t_sw)
        self.assertGreater(res, 0)

    def test_closed_4tau_overboost_exceeds_threshold(self):
        """
        If amplitude at t_sw >= threshold, we solve second-phase log expression.
        """
        ucw = 30.0
        rs = 20.0
        ls = 35e-3
        cs = 200e-12
        ub = 60.0
        t_sw = 0.0005

        res = closed_4tau(ucw, rs, ls, cs, None, ub, t_sw)
        self.assertGreaterEqual(res, t_sw)

    def test_closed_4tau_assertions(self):
        """Negative or zero parameters => AssertionError, ub <= ucw => ValueError."""
        with self.assertRaises(AssertionError):
            closed_4tau(ucw=-10, rs=10, ls=1e-3, cs=1e-12)
        with self.assertRaises(AssertionError):
            closed_4tau(ucw=10, rs=-5, ls=1e-3, cs=1e-12)
        with self.assertRaises(ValueError):
            # ub <= ucw => ValueError
            closed_4tau(ucw=20, rs=10, ls=1e-3, cs=1e-12, ub=10)


class TestClosedPotential(unittest.TestCase):
    """Tests for closed_potential and print_closed_potential."""

    def test_closed_potential_basic(self):
        """
        Overboost scenario: ensure t_sw, tau_no_boost, tau_with_boost, delta_time, pct_improvement are valid.
        """
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        ucw = 40.0
        ub = 60.0

        t_sw, tau_no_boost, tau_with_boost, delta_time, pct_improvement = closed_potential(rs, ls, cs, c0, ucw, ub)
        self.assertGreater(t_sw, 0)
        self.assertGreater(tau_no_boost, 0)
        self.assertGreater(tau_with_boost, 0)
        self.assertGreater(delta_time, 0)
        self.assertGreater(pct_improvement, 0)

    @patch("builtins.print")
    def test_print_closed_potential(self, mock_print):
        """Ensure print_closed_potential calls print at least once."""
        rs = 24.764
        ls = 38.959e-3
        cs = 400.33e-12
        c0 = 3970.1e-12
        ucw = 40.0
        ub = 60.0

        print_closed_potential(rs, ls, cs, c0, ucw, ub)
        self.assertTrue(mock_print.called)

    def test_closed_potential_asserts(self):
        """Check negative or zero arguments cause assertion errors, or ub <= ucw => ValueError."""
        with self.assertRaises(AssertionError):
            closed_potential(-1, 1, 1e-12, 1e-12, 10, 20)
        with self.assertRaises(AssertionError):
            closed_potential(1, 0, 1e-12, 1e-12, 10, 20)
        with self.assertRaises(AssertionError):
            closed_potential(1, 1, -1e-12, 1e-12, 10, 20)
        with self.assertRaises(AssertionError):
            closed_potential(1, 1, 1e-12, 1e-12, -10, 20)

        # ub <= ucw => ValueError
        with self.assertRaises(ValueError):
            closed_potential(1, 1, 1e-12, 1e-12, 20, 10)


if __name__ == "__main__":
    unittest.main()
