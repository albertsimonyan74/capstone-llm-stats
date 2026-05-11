# An Introduction to Bayesian Analysis: Theory and Methods

## Metadata
- Authors: Jayanta K. Ghosh, Mohan Delampady, Tapas Samanta
- Edition: 1st
- Year: 2006
- Publisher: Springer (Springer Texts in Statistics)
- ISBN: 978-0-387-40084-6
- URL: https://link.springer.com/book/10.1007/978-0-387-35433-0
- Date added to vault: 2026-05-01
- Source category: GRADUATE_TEXTBOOK

## Subject scope
Graduate-level Bayesian analysis emphasizing theory. Covers Jeffreys priors, Fisher information, Rao-Cramér bounds, asymptotic posterior theory, and decision-theoretic foundations.

## Coverage map (which task types this book grounds)
- JEFFREYS_*: Jeffreys non-informative prior derivation
- FISHER_INFO_*: Fisher information for exponential families
- RC_BOUND_*: Rao-Cramér lower bound
- MLE_EFFICIENCY: asymptotic efficiency theory
- BAYES_RISK: decision-theoretic risk

## How it grounds this project
Primary reference for JEFFREYS_*, FISHER_INFO_*, RC_BOUND_* task ground-truth derivations in code/data_preprocessing/frequentist/. The intentional NotImplementedError for `dist="uniform"` in fisher_information() reflects this book's caveat that Uniform is not a regular exponential family.

## Citation in poster
Ghosh et al. (2006)

## Citation in paper
Ghosh, J. K., Delampady, M., & Samanta, T. (2006). *An Introduction to Bayesian Analysis: Theory and Methods*. Springer.

## Bibtex key
ghosh2006bayesian

## Project artifacts that cite this
- code/data_preprocessing/frequentist/fisher_information.py (regularity conditions)
- code/data_preprocessing/frequentist/rao_cramer.py
- code/data_preprocessing/bayesian/jeffreys.py
- Task ground-truth: JEFFREYS_*, FISHER_INFO_*, RC_BOUND_*, MLE_EFFICIENCY_*
- References / Foundations footer

## Tags
#textbook #priors #fisher-information #rao-cramer #task-grounding
