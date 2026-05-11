"""
Minimal tests for baseline/frequentist modules.
Run with: pytest baseline/frequentist/test_frequentist.py -v
"""
import math
import pytest

from data_preprocessing.frequentist.fisher_information import (
    fisher_information,
    rao_cramer_bound,
)
from data_preprocessing.frequentist.order_statistics import (
    order_statistic_pdf,
    min_order_statistic_cdf,
    max_order_statistic_cdf,
    joint_min_max_density,
    range_cdf,
)


# ── fisher_information ────────────────────────────────────────────────────────

class TestFisherInformation:
    def test_binomial_matches_benchmark_task_01(self):
        # FISHER_INFO_01: theta=0.3, n=10 → 47.619...
        result = fisher_information("binomial", 0.3, 10)
        assert abs(result - 47.619047619) < 0.001

    def test_binomial_matches_benchmark_task_02(self):
        # FISHER_INFO_02: poisson theta=0.25, n=20 → 80.0
        result = fisher_information("poisson", 0.25, 20)
        assert abs(result - 80.0) < 0.001

    def test_normal_single_obs(self):
        # Normal(mu, sigma^2=1): I_1 = 1, I_n = n
        assert fisher_information("normal", 0.0, 5) == pytest.approx(5.0)

    def test_exponential_rate(self):
        # Exp(rate=2): I_1 = 1/rate^2 = 0.25, I_5 = 1.25
        assert fisher_information("exponential", 2.0, 5) == pytest.approx(1.25)

    def test_normal_var(self):
        # Normal(var=theta): I_1(theta) = 1/(2*theta^2)
        # theta=1: I_1=0.5, I_4=2.0
        assert fisher_information("normal_var", 1.0, 4) == pytest.approx(2.0)

    def test_uniform_raises(self):
        with pytest.raises(NotImplementedError):
            fisher_information("uniform", 0.5)

    def test_rao_cramer_unbiased(self):
        # Binomial n=10, theta=0.3: RC = 1/I_n = 0.021
        fi = fisher_information("binomial", 0.3, 10)
        rc = rao_cramer_bound(fi)
        assert rc == pytest.approx(1.0 / fi)

    def test_rao_cramer_biased(self):
        rc = rao_cramer_bound(10.0, bias_deriv=0.5)
        # (1 + 0.5)^2 / 10 = 0.225
        assert rc == pytest.approx(0.225)


# ── order_statistics — uniform (benchmark parity) ─────────────────────────────

class TestOrderStatisticsUniform:
    def test_order_stat_pdf_benchmark_01(self):
        # ORDER_STAT_01: k=3, n=5, y=0.6 → 1.728
        assert order_statistic_pdf(0.6, 3, 5, "uniform") == pytest.approx(1.728, rel=1e-4)

    def test_order_stat_pdf_benchmark_02(self):
        # ORDER_STAT_02: target 2.048 — k=2, n=5, y=0.2
        assert order_statistic_pdf(0.2, 2, 5, "uniform") == pytest.approx(2.048, rel=1e-4)

    def test_min_cdf_benchmark_03(self):
        # ORDER_STAT_03: x=0.3, n=5 → 0.83193
        assert min_order_statistic_cdf(0.3, 5, "uniform") == pytest.approx(0.83193, rel=1e-4)

    def test_min_cdf_benchmark_04(self):
        # ORDER_STAT_04: x=0.5, n=8 → 0.99609375
        assert min_order_statistic_cdf(0.5, 8, "uniform") == pytest.approx(0.99609375, rel=1e-4)

    def test_max_cdf_is_fn(self):
        # For uniform, max CDF = x^n
        assert max_order_statistic_cdf(0.5, 4, "uniform") == pytest.approx(0.5 ** 4)

    def test_range_cdf_uniform_analytical(self):
        # range_cdf(x, n=3): x^2 * [3 - 2x]
        x = 0.5
        expected = 0.5 ** 2 * (3 - 2 * 0.5)
        assert range_cdf(x, 3, "uniform") == pytest.approx(expected)

    def test_range_cdf_boundary(self):
        assert range_cdf(0.0, 3, "uniform") == pytest.approx(0.0)
        assert range_cdf(1.0, 3, "uniform") == pytest.approx(1.0)


# ── order_statistics — exponential ───────────────────────────────────────────

class TestOrderStatisticsExponential:
    def test_min_cdf_exponential_property(self):
        # min of n Exp(rate) ~ Exp(n*rate): F_(1)(x) = 1 - exp(-n*rate*x)
        x, n, rate = 0.5, 3, 2.0
        expected = 1.0 - math.exp(-n * rate * x)
        result = min_order_statistic_cdf(x, n, "exponential", {"rate": rate})
        assert result == pytest.approx(expected, rel=1e-5)

    def test_max_cdf_exponential(self):
        # F_(n)(x) = (1 - exp(-rate*x))^n
        x, n, rate = 2.0, 4, 1.0
        import math as _m
        expected = (1.0 - _m.exp(-rate * x)) ** n
        result = max_order_statistic_cdf(x, n, "exponential", {"rate": rate})
        assert result == pytest.approx(expected, rel=1e-5)

    def test_order_stat_pdf_integrates_to_one(self):
        from scipy.integrate import quad
        n, k, rate = 4, 2, 1.0
        val, _ = quad(
            lambda y: order_statistic_pdf(y, k, n, "exponential", {"rate": rate}),
            0.0, 100.0
        )
        assert val == pytest.approx(1.0, rel=1e-3)

    def test_joint_min_max_symmetry(self):
        # joint density should be positive for 0 < x < y
        result = joint_min_max_density(0.5, 1.5, 4, "exponential", {"rate": 1.0})
        assert result > 0.0

    def test_range_cdf_monotone(self):
        # range CDF should be monotone
        vals = [range_cdf(r, 3, "exponential") for r in [0.5, 1.0, 2.0, 5.0]]
        assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))

    def test_range_cdf_bounds(self):
        assert range_cdf(0.0, 3, "exponential") == pytest.approx(0.0)
        assert range_cdf(100.0, 3, "exponential") == pytest.approx(1.0, abs=0.01)


# ── order_statistics — normal ─────────────────────────────────────────────────

class TestOrderStatisticsNormal:
    def test_min_cdf_normal_symmetry(self):
        # For standard normal n=3, F_(1)(0) = 1 - (1 - 0.5)^3 = 1 - 0.125 = 0.875
        assert min_order_statistic_cdf(0.0, 3, "normal") == pytest.approx(0.875)

    def test_max_cdf_normal_symmetry(self):
        # F_(n)(0) = 0.5^n
        assert max_order_statistic_cdf(0.0, 4, "normal") == pytest.approx(0.5 ** 4)

    def test_range_cdf_increasing(self):
        vals = [range_cdf(r, 4, "normal") for r in [0.5, 1.0, 3.0]]
        assert vals[0] < vals[1] < vals[2]
