# ---- Normal–Gamma (precision) ----
from data_preprocessing.bayesian import normal_gamma_update
ng = normal_gamma_update(mu0=0.0, kappa0=1.0, alpha0=2.0, beta0=2.0, data=[1.0, 2.0, 1.5, 0.5])
print("Normal–Gamma posterior:", ng)
print("E[mu]:", ng.posterior_mean_mu())
print("E[tau]:", ng.posterior_mean_tau())
print("E[sigma^2]:", ng.posterior_mean_sigma2())
print("CI mu (marginal t):", ng.credible_interval_mu_marginal())
print("CI tau:", ng.credible_interval_tau())
print("CI sigma^2:", ng.credible_interval_sigma2())

# ---- Posterior predictive ----
from data_preprocessing.bayesian import beta_binomial_update, gamma_poisson_update
from data_preprocessing.bayesian import beta_binomial_predictive_pmf, gamma_poisson_predictive_pmf

bb = beta_binomial_update(alpha=2, beta=2, x=6, n=10)
print("Pred P(k=3 in m=5) Beta-Binom:", beta_binomial_predictive_pmf(3, 5, bb.alpha_post, bb.beta_post))

gp = gamma_poisson_update(alpha=1.0, rate=1.0, counts=[2, 0, 3, 1])
print("Pred P(y=2) Gamma-Poisson:", gamma_poisson_predictive_pmf(2, gp.alpha_post, gp.rate_post))

# ---- Dirichlet–Multinomial predictive ----
from data_preprocessing.bayesian import dirichlet_multinomial_update, dirichlet_multinomial_predictive_pmf, dirichlet_predictive_next
dm = dirichlet_multinomial_update(alpha=[1, 1, 1], counts=[10, 5, 0])
print("Dirichlet posterior mean:", dm["posterior_mean"])
print("Predictive next:", dirichlet_predictive_next(dm["posterior_alpha"]))
print("Pred P([2,1,0] in m=3):", dirichlet_multinomial_predictive_pmf([2,1,0], dm["posterior_alpha"]))

# ---- Bayes estimators under loss ----
from data_preprocessing.bayesian import bayes_estimator_from_beta, bayes_estimator_from_gamma_shape_rate, bayes_estimator_from_student_t
print("Bayes est (Beta posterior, quadratic):", bayes_estimator_from_beta(bb.alpha_post, bb.beta_post, "quadratic"))
print("Bayes est (Beta posterior, absolute):", bayes_estimator_from_beta(bb.alpha_post, bb.beta_post, "absolute"))
print("Bayes est (Gamma posterior, 0-1):", bayes_estimator_from_gamma_shape_rate(gp.alpha_post, gp.rate_post, "0-1"))

# For Normal–Gamma marginal mu (Student-t)
df = 2 * ng.alpha_n
scale = (ng.beta_n / (ng.alpha_n * ng.kappa_n)) ** 0.5
print("Bayes est (t marginal mu, absolute):", bayes_estimator_from_student_t(ng.mu_n, scale, df, "absolute"))