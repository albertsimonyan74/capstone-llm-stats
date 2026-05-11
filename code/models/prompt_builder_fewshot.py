"""
Few-shot Chain-of-Thought prompt builder.
Implements Wei et al. (2022) exemplar format for comparison against zero-shot baseline.
"""
from __future__ import annotations

EXEMPLARS: dict[str, list[dict]] = {
    "BINOM_FLAT": [
        {
            "problem": "X ~ Binomial(n=10, p=unknown). Observed x=6 successes. Flat prior Beta(1,1). Find posterior alpha, beta, and mean.",
            "reasoning": "Step 1: Flat prior is Beta(1,1), so alpha_0=1, beta_0=1.\nStep 2: Posterior update: alpha=alpha_0+x=1+6=7, beta=beta_0+(n-x)=1+4=5.\nStep 3: Posterior mean=alpha/(alpha+beta)=7/12=0.583.",
            "answer": "ANSWER: 7, 5, 0.583"
        },
        {
            "problem": "X ~ Binomial(n=20, p=unknown). Observed x=12. Flat prior Beta(1,1). Find posterior alpha, beta, and mean.",
            "reasoning": "Step 1: Flat prior Beta(1,1).\nStep 2: alpha=1+12=13, beta=1+8=9.\nStep 3: Mean=13/22=0.591.",
            "answer": "ANSWER: 13, 9, 0.591"
        }
    ],
    "MARKOV": [
        {
            "problem": "Two-state Markov chain. P(A→A)=0.7, P(A→B)=0.3, P(B→A)=0.4, P(B→B)=0.6. Find stationary distribution.",
            "reasoning": "Step 1: Stationary π satisfies πP=π.\nStep 2: π_A*0.3=π_B*0.4.\nStep 3: π_A+π_B=1.\nStep 4: Solving: π_A=0.571, π_B=0.429.",
            "answer": "ANSWER: 0.571, 0.429"
        }
    ],
    "FISHER_INFO": [
        {
            "problem": "X ~ Bernoulli(p). Find Fisher information I(p).",
            "reasoning": "Step 1: Log-likelihood l(p)=x*log(p)+(1-x)*log(1-p).\nStep 2: Score=dl/dp=x/p-(1-x)/(1-p).\nStep 3: I(p)=E[score^2]=1/(p(1-p)).",
            "answer": "ANSWER: 1/(p*(1-p))"
        }
    ],
    "BETA_BINOM": [
        {
            "problem": "Prior: Beta(2,3). Likelihood: Binomial(n=10, x=4). Find posterior alpha, beta, mean.",
            "reasoning": "Step 1: Posterior alpha=prior_alpha+x=2+4=6.\nStep 2: Posterior beta=prior_beta+(n-x)=3+6=9.\nStep 3: Mean=6/(6+9)=0.400.",
            "answer": "ANSWER: 6, 9, 0.400"
        }
    ],
    "GIBBS": [
        {
            "problem": "Bivariate normal with rho=0.5. Sample X given Y=1.0, mu_x=0, sigma_x=1. Find conditional mean and variance.",
            "reasoning": "Step 1: Conditional mean=mu_x+rho*(sigma_x/sigma_y)*(y-mu_y)=0+0.5*1.0=0.5.\nStep 2: Conditional variance=sigma_x^2*(1-rho^2)=1*(1-0.25)=0.75.",
            "answer": "ANSWER: 0.5, 0.75"
        }
    ]
}


def build_fewshot_prompt(task: dict, n_examples: int = 2) -> str:
    """
    Generate few-shot CoT prompt with exemplars (Wei et al., 2022).
    Falls back to zero-shot if no exemplars defined for task type.
    """
    from models.prompt_builder import build_prompt

    task_type = task.get("task_type", "")
    exemplars = EXEMPLARS.get(task_type, [])

    if not exemplars:
        return build_prompt(task)

    header = (
        "You are solving statistical reasoning problems. "
        "Study these examples carefully:\n\n"
    )
    examples_text = ""
    for i, ex in enumerate(exemplars[:n_examples], 1):
        examples_text += (
            f"Example {i}:\n"
            f"Problem: {ex['problem']}\n"
            f"Solution: {ex['reasoning']}\n"
            f"{ex['answer']}\n\n"
        )

    target = build_prompt(task)
    return header + examples_text + "Now solve this problem:\n" + target
