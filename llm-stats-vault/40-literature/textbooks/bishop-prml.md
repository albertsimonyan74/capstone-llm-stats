# Pattern Recognition and Machine Learning

## Metadata
- Author: Christopher M. Bishop
- Edition: 1st
- Year: 2006
- Publisher: Springer
- ISBN: 978-0-387-31073-2
- URL: https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/
- Date added to vault: 2026-05-01
- Source category: GRADUATE_TEXTBOOK

## Subject scope
Comprehensive graduate ML reference. Covers Dirichlet-Multinomial models (Ch.2), variational inference (Ch.10), Bayesian linear regression (Ch.3), Gaussian processes (Ch.6), and EM (Ch.9).

## Coverage map (which task types this book grounds)
- VB_*: variational Bayes — mean-field, ELBO derivation (Ch.10)
- DIRICHLET_*: Dirichlet-Multinomial conjugate updates (Ch.2)
- BAYES_REG: Bayesian linear regression (Ch.3)
- LOG_ML: marginal likelihood / evidence (Ch.3, 10)

## How it grounds this project
Core reference for variational Bayes (VB_*) and Dirichlet (DIRICHLET_*) task ground-truth derivations. Bishop's mean-field VB derivation is the analytic baseline against which code/data_preprocessing/bayesian/advanced_methods.py:VB.solve() is checked. Cited in Foundations footer.

## Citation in poster
Bishop (2006)

## Citation in paper
Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer.

## Bibtex key
bishop2006prml

## Project artifacts that cite this
- code/data_preprocessing/bayesian/advanced_methods.py (VB class)
- code/data_preprocessing/bayesian/conjugate.py (Dirichlet)
- Task ground-truth: VB_*, DIRICHLET_*, BAYES_REG_*, LOG_ML_*
- References / Foundations footer

## Tags
#textbook #variational-bayes #dirichlet #ml #task-grounding
