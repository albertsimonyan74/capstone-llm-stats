# Bayesian Methods for Data Analysis (3rd ed.)

## Metadata
- Authors: Bradley P. Carlin, Thomas A. Louis
- Edition: 3rd
- Year: 2008
- Publisher: Chapman & Hall / CRC (Texts in Statistical Science)
- ISBN: 978-1-58488-697-6
- URL: https://www.routledge.com/Bayesian-Methods-for-Data-Analysis/Carlin-Louis/p/book/9781584886976
- Date added to vault: 2026-05-01
- Source category: GRADUATE_TEXTBOOK

## Subject scope
Advanced graduate Bayesian computation. Covers MCMC (Gibbs, Metropolis-Hastings, HMC), Bayesian regression, hierarchical and multilevel models, Bayes factor computation, and reversible-jump MCMC.

## Coverage map (which task types this book grounds)
- GIBBS, MH, HMC: MCMC algorithms (Ch.3-4)
- HIERARCHICAL: hierarchical Bayesian models (Ch.5)
- REGRESSION (Bayesian): Bayesian linear regression (Ch.4)
- RJMCMC: reversible-jump MCMC and Bayes factors (Ch.4)
- BAYES_FACTOR: marginal-likelihood estimation

## How it grounds this project
Core Phase-2 task reference. code/data_preprocessing/bayesian/advanced_methods.py implementations of Gibbs, MH, HMC, and RJMCMC trace to Carlin & Louis algorithms. The MCMC-as-ground-truth-solver-only convention (out of scope for benchmark prompts) follows their distinction between teaching MCMC vs using it.

## Citation in poster
Carlin & Louis (2008)

## Citation in paper
Carlin, B. P., & Louis, T. A. (2008). *Bayesian Methods for Data Analysis* (3rd ed.). Chapman & Hall/CRC.

## Bibtex key
carlin2008bayesian

## Project artifacts that cite this
- code/data_preprocessing/bayesian/advanced_methods.py (full module)
- Task ground-truth: GIBBS_*, MH_*, HMC_*, HIERARCHICAL_*, REGRESSION_*, RJMCMC_*
- Phase-2 build script (build_tasks_advanced.py)
- References / Foundations footer

## Tags
#textbook #mcmc #hierarchical #phase-2 #task-grounding
