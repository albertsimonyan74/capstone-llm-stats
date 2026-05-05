# Introduction to Bayesian Statistics (2nd ed.)

## Metadata
- Authors: William M. Bolstad
- Edition: 2nd
- Year: 2007
- Publisher: Wiley-Interscience
- ISBN: 978-0-471-27020-5
- URL: https://onlinelibrary.wiley.com/doi/book/10.1002/9780470181188
- Date added to vault: 2026-05-01
- Source category: GRADUATE_TEXTBOOK

## Subject scope
Foundational undergraduate-graduate text on Bayesian inference. Covers conjugate prior families (Beta-Binomial, Normal-Normal, Gamma-Poisson), credible intervals, HPD regions, and Bayesian hypothesis testing.

## Coverage map (which task types this book grounds)
- BETA_BINOM: conjugate Beta prior + Binomial likelihood (Ch.8)
- BINOM_FLAT: uniform prior special case (Ch.8)
- HPD: highest posterior density region construction (Ch.8-9)
- CI_CREDIBLE (basic): credible-interval framing
- GAMMA_POISSON: conjugate update (Ch.10)

## How it grounds this project
Primary undergraduate reference for conjugate-update derivations in baseline/bayesian/conjugate.py. Task ground-truth derivations for BETA_BINOM_*, BINOM_FLAT_*, HPD_*, and CI_CREDIBLE_* trace to Bolstad's worked examples. Cited in Foundations footer.

## Citation in poster
Bolstad (2007)

## Citation in paper
Bolstad, W. M. (2007). *Introduction to Bayesian Statistics* (2nd ed.). Wiley.

## Bibtex key
bolstad2007bayesian

## Project artifacts that cite this
- baseline/bayesian/conjugate.py
- Task ground-truth: BETA_BINOM_*, BINOM_FLAT_*, HPD_*, CI_CREDIBLE_*
- References / Foundations footer

## Tags
#textbook #foundational #conjugate-models #credible-intervals #task-grounding
