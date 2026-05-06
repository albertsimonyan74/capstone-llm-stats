"""Assemble poster/poster.html — single self-contained A0 poster.

Reads the 7 SVGs from poster/figures/, strips XML/DOCTYPE preamble,
inlines them into a single HTML file with print-ready CSS.
"""
from __future__ import annotations
import json
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "poster.html")
DERIVED = os.path.join(FIGS, "derived", "disagreement_matrix_2x2.json")


def load_svg(name: str) -> str:
    """Read SVG, strip <?xml?> + <!DOCTYPE>, return inline-ready <svg>...</svg>.
    Force width:100% / height:auto via inline style on the root <svg> tag."""
    with open(os.path.join(FIGS, name), "r", encoding="utf-8") as fh:
        s = fh.read()
    s = re.sub(r"<\?xml[^>]*\?>\s*", "", s)
    s = re.sub(r"<!DOCTYPE[^>]*>\s*", "", s)
    s = re.sub(
        r"<svg\b([^>]*)>",
        lambda m: f'<svg{m.group(1)} preserveAspectRatio="xMidYMid meet" style="width:100%;height:auto;display:block;">',
        s,
        count=1,
    )
    return s.strip()


def main() -> None:
    with open(DERIVED, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    n_total = d["n_total"]
    pass_flip_n = d["cells"]["kw_pass_judge_fail"]
    dir_pct = d["summary"]["directional_pass_flip_pct"]
    total_dis = d["summary"]["total_disagreement_pct"]

    subs = {
        "@@NMACR@@":          load_svg("nmacr_weights.svg"),
        "@@DISAGREEMENT@@":   load_svg("disagreement_matrix.svg"),
        "@@KRIPPENDORFF@@":   load_svg("krippendorff_strip.svg"),
        "@@LEADERBOARD@@":    load_svg("dimension_leaderboard.svg"),
        "@@ROBUSTNESS@@":     load_svg("robustness_heatmap.svg"),
        "@@CALIBRATION@@":    load_svg("calibration_ece_paired.svg"),
        "@@TAXONOMY@@":       load_svg("failure_taxonomy_stacked.svg"),
        "@@N_TOTAL@@":        f"{n_total:,}",
        "@@PASS_FLIP_N@@":    str(pass_flip_n),
        "@@DIR_PCT@@":        f"{dir_pct:.2f}",
        "@@TOTAL_DIS@@":      f"{total_dis:.2f}",
    }

    html = TEMPLATE
    for k, v in subs.items():
        html = html.replace(k, v)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Wrote {OUT} ({len(html):,} bytes)")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Reason or pattern-match? — DS 299 Capstone Poster</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
@page { size: 841mm 1189mm; margin: 0; }

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: #ffffff;
  color: #0f172a;
  font-family: 'Space Grotesk', system-ui, sans-serif;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.poster {
  width: 841mm;
  height: 1189mm;
  padding: 32mm 28mm 24mm 28mm;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 7mm;
  position: relative;
  overflow: hidden;
}

/* ============ TITLE BAND ============ */
.title-band {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: flex-end;
  gap: 14mm;
  padding-bottom: 6mm;
  border-bottom: 0.6mm solid #0f172a;
}
.title-eyebrow {
  font-family: 'Space Mono', monospace;
  font-size: 11pt;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #0d9488;
  margin-bottom: 4mm;
}
.title-main {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 56pt;
  font-weight: 700;
  line-height: 1.04;
  color: #0f172a;
  letter-spacing: -0.015em;
}
.title-main .accent { color: #0d9488; font-style: italic; font-weight: 600; }
.title-sub {
  margin-top: 4mm;
  font-size: 16pt;
  font-weight: 400;
  color: #475569;
  line-height: 1.35;
  max-width: 480mm;
}
.author-block {
  text-align: right;
  font-family: 'Space Mono', monospace;
  font-size: 10.5pt;
  line-height: 1.6;
  color: #0f172a;
}
.author-block .name {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 16pt;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: -0.01em;
}
.author-block .meta-line {
  font-weight: 400;
  color: #475569;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 9.5pt;
}
.author-block .supervisor {
  margin-top: 2mm;
  font-style: italic;
  font-family: 'Space Grotesk', sans-serif;
  text-transform: none;
  letter-spacing: 0;
  color: #0f172a;
  font-size: 11pt;
}

/* ============ SECTION CHROME ============ */
.eyebrow {
  font-family: 'Space Mono', monospace;
  font-size: 11pt;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #0d9488;
  margin-bottom: 3.5mm;
  display: flex;
  align-items: baseline;
  gap: 4mm;
}
.eyebrow .num {
  display: inline-block;
  padding: 0.6mm 2mm;
  background: #0f172a;
  color: #ffffff;
  font-size: 9pt;
  letter-spacing: 0.12em;
  border-radius: 1mm;
}
.eyebrow .star {
  color: #d97706;
  font-size: 12pt;
  letter-spacing: 0;
}

.section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22pt;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: -0.01em;
  line-height: 1.15;
  margin-bottom: 2mm;
}

.body-text {
  font-size: 11.5pt;
  line-height: 1.55;
  color: #0f172a;
  font-weight: 400;
}

.body-text strong { font-weight: 600; color: #0f172a; }

ul.bullets {
  list-style: none;
  padding: 0;
}
ul.bullets li {
  padding: 1.2mm 0 1.2mm 6mm;
  position: relative;
  font-size: 11.5pt;
  line-height: 1.5;
  color: #0f172a;
}
ul.bullets li::before {
  content: "\\25B8";
  position: absolute;
  left: 0;
  top: 1.2mm;
  color: #0d9488;
  font-weight: 700;
}

.caption {
  font-style: italic;
  color: #475569;
  font-size: 10pt;
  line-height: 1.45;
  margin-top: 2.5mm;
}
.caption .num { font-family: 'Space Mono', monospace; font-style: normal; color: #0f172a; font-weight: 700; }

/* ============ ABSTRACT / PROBLEM / CONTRIBS ============ */
.three-col {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 9mm;
  padding: 4mm 0 7mm 0;
  border-bottom: 0.3mm solid #e2e8f0;
}
.col { display: flex; flex-direction: column; }

/* ============ METHODS ============ */
.methods {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 9mm;
  align-items: center;
  padding-bottom: 6mm;
  border-bottom: 0.3mm solid #e2e8f0;
}
.methods .figure { width: 100%; }

/* ============ JUDGE VALIDATION ============ */
.judge-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9mm;
  padding-bottom: 6mm;
  border-bottom: 0.3mm solid #e2e8f0;
}
.judge-row .panel { display: flex; flex-direction: column; }
.judge-row .panel-fig { flex: 1; display: flex; align-items: center; justify-content: center; }

/* ============ DIMENSION LEADERBOARD (HEADLINE) ============ */
.headline {
  padding: 5mm 0 6mm 0;
  border-top: 0.3mm solid #e2e8f0;
  border-bottom: 0.3mm solid #e2e8f0;
}
.headline .figure { width: 100%; }

/* ============ ROBUSTNESS ============ */
.robustness {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 9mm;
  padding: 2mm 0 6mm 0;
  border-bottom: 0.3mm solid #e2e8f0;
}
.robustness .figure { width: 100%; max-height: 220mm; }
.robustness .figure svg { max-height: 220mm; }
.callouts {
  display: flex;
  flex-direction: column;
  gap: 5mm;
}
.callout {
  border-left: 1mm solid #0d9488;
  padding: 2mm 0 2mm 4mm;
  background: #f8fafc;
}
.callout .label {
  font-family: 'Space Mono', monospace;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #0d9488;
}
.callout .text {
  font-size: 11pt;
  line-height: 1.45;
  color: #0f172a;
  margin-top: 1mm;
}
.callout.warn { border-left-color: #d97706; }
.callout.warn .label { color: #d97706; }
.callout.bad  { border-left-color: #dc2626; }
.callout.bad  .label { color: #dc2626; }

/* ============ CALIBRATION ============ */
.calibration {
  padding: 2mm 0 6mm 0;
  border-bottom: 0.3mm solid #e2e8f0;
}
.calibration .figure { max-width: 100%; }

/* ============ TAXONOMY + CONCLUSION ============ */
.tax-row {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 9mm;
  padding: 2mm 0 6mm 0;
  border-bottom: 0.3mm solid #e2e8f0;
}
.tax-row .figure { width: 100%; }

/* ============ FOOTER ============ */
.footer {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  gap: 9mm;
  padding-top: 5mm;
  font-size: 8.5pt;
  line-height: 1.45;
  color: #475569;
}
.footer .eyebrow {
  font-size: 9pt;
  letter-spacing: 0.14em;
  margin-bottom: 2mm;
}
.footer ol {
  padding-left: 4mm;
  font-size: 8pt;
  line-height: 1.42;
  color: #475569;
}
.footer ol li { margin-bottom: 0.6mm; }
.qr-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.qr-stub {
  width: 24mm;
  height: 24mm;
  border: 0.4mm solid #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Space Mono', monospace;
  font-size: 6pt;
  text-align: center;
  color: #475569;
  padding: 1mm;
  margin-top: 2mm;
}
.contact-row {
  font-family: 'Space Mono', monospace;
  font-size: 9pt;
  color: #0f172a;
  letter-spacing: 0.02em;
  margin-bottom: 1mm;
}

/* ============ FIGURE WRAPPERS ============ */
.figure { display: block; }
.figure svg { display: block; max-width: 100%; height: auto; }

.headline-num {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  color: #0f172a;
  font-size: 11pt;
}
</style>
</head>
<body>
<div class="poster">

  <!-- ============ TITLE BAND ============ -->
  <header class="title-band">
    <div>
      <div class="title-eyebrow">DS 299 &middot; Capstone Research &middot; Bayesian LLM Benchmark</div>
      <h1 class="title-main">Reason or pattern-match?<br><span class="accent">Dimensional</span> evaluation of LLM Bayesian reasoning</h1>
      <div class="title-sub">A 5-dimension rubric (NMACR), an external LLM-judge validation pipeline, and a 38-task-type robustness audit across 5 frontier models on 171 inferential statistics tasks.</div>
    </div>
    <div class="author-block">
      <div class="name">Albert Simonyan</div>
      <div class="meta-line">Akian College of Science &amp; Engineering</div>
      <div class="meta-line">American University of Armenia</div>
      <div class="meta-line">DS 299 &middot; Spring 2026</div>
      <div class="supervisor">Supervisor: Dr. Vahe Movsisyan</div>
    </div>
  </header>

  <!-- ============ ABSTRACT / PROBLEM / CONTRIBUTIONS ============ -->
  <section class="three-col">
    <div class="col">
      <div class="eyebrow"><span class="num">01</span>Abstract</div>
      <p class="body-text">
        We benchmark five frontier LLMs (Claude, ChatGPT, Gemini, DeepSeek, Mistral) on 171
        Bayesian and inferential statistics tasks using <strong>NMACR</strong>, a five-dimension
        composite rubric (Numerical, Method, Assumption, Calibration, Reasoning). External
        LLM-judge validation on <span class="headline-num">@@N_TOTAL@@</span> runs reveals that
        keyword scoring under-credits reasoning quality on <span class="headline-num">@@PASS_FLIP_N@@</span>
        cases that flip from pass to fail under the judge. Rankings shift across measurement
        dimensions: no single model dominates, and assumption articulation is the dominant
        gap across the cohort.
      </p>
    </div>

    <div class="col">
      <div class="eyebrow"><span class="num">02</span>Problem</div>
      <p class="body-text">
        Single-leaderboard LLM evaluations collapse multi-dimensional reasoning into one
        scalar. Keyword rubrics under-credit reasoning quality and over-credit superficial
        formatting matches. Calibration &mdash; alignment between stated and observed
        confidence &mdash; is rarely measured rigorously, and robustness to surface-level
        perturbations is reported only in aggregate. The result: rankings that look
        decisive but are sensitive to choice of metric.
      </p>
    </div>

    <div class="col">
      <div class="eyebrow"><span class="num">03</span>Contributions</div>
      <ul class="bullets">
        <li><strong>NMACR rubric.</strong> Five-dimension composite score with literature-derived weights.</li>
        <li><strong>Judge validation pipeline.</strong> External Llama 3.3 70B judge cross-checked against keyword scores on @@N_TOTAL@@ runs.</li>
        <li><strong>Robustness audit.</strong> 38 task types &times; 5 models heatmap under three perturbation families.</li>
        <li><strong>Failure-mode taxonomy.</strong> L1 audit at task-type granularity identifying assumption articulation as the dominant gap.</li>
      </ul>
    </div>
  </section>

  <!-- ============ METHODS ============ -->
  <section class="methods">
    <div class="figure">@@NMACR@@</div>
    <div>
      <div class="eyebrow"><span class="num">04</span>Methods &middot; NMACR composite</div>
      <p class="body-text">
        Each response receives five sub-scores: <strong>Numerical</strong> (answer accuracy with
        per-task tolerance), <strong>Method</strong> (procedural correctness), <strong>Assumption</strong>
        (articulation of model assumptions), <strong>Calibration</strong> (overconfidence-aware
        confidence reliability), <strong>Reasoning</strong> (working shown, formula stated,
        result interpreted). Weights follow the literature (Du 2025; Boye &amp; Moell 2025;
        Yamauchi 2025). Robustness measured via <em>rephrase / numerical / semantic</em>
        perturbations on the same task pool.
      </p>
      <p class="caption">Figure 1. NMACR weight allocation. Assumption articulation receives the highest weight, reflecting its role as a discriminating dimension among frontier models.</p>
    </div>
  </section>

  <!-- ============ RESULTS 1 — JUDGE VALIDATION ============ -->
  <section class="judge-row">
    <div class="panel">
      <div class="eyebrow"><span class="num">05</span>Results 1 &middot; Judge validation</div>
      <div class="section-title">Keyword scoring disagrees with the LLM judge on 1 of every 5 runs.</div>
      <div class="panel-fig figure">@@DISAGREEMENT@@</div>
      <p class="caption">
        Figure 2. 2 &times; 2 keyword &times; judge crosstab on the assumption-compliance dimension
        (<span class="num">n = @@N_TOTAL@@</span> eligible runs). <span class="num">@@PASS_FLIP_N@@</span>
        keyword-pass cases flip to judge-fail; directional pass-flip rate
        <span class="num">@@DIR_PCT@@%</span>, total disagreement <span class="num">@@TOTAL_DIS@@%</span>.
      </p>
    </div>
    <div class="panel">
      <div class="eyebrow"><span class="num">06</span>Inter-rater reliability</div>
      <div class="section-title">Krippendorff &alpha; situates keyword&ndash;judge agreement well above chance.</div>
      <div class="panel-fig figure">@@KRIPPENDORFF@@</div>
      <p class="caption">
        Figure 3. Krippendorff &alpha; (binary) across dimensions. Strip anchors at &alpha; = &minus;1 (systematic disagreement),
        &alpha; = 0 (chance), &alpha; = +1 (perfect agreement). Agreement is substantial on numerical pass/fail
        but weakens on assumption articulation &mdash; exactly where the keyword rubric is least faithful.
      </p>
    </div>
  </section>

  <!-- ============ RESULTS 2 — DIMENSION LEADERBOARD (HEADLINE) ============ -->
  <section class="headline">
    <div class="eyebrow"><span class="num">07</span>Results 2 &middot; Dimension leaderboard <span class="star">&#9733;</span> Headline finding</div>
    <div class="section-title">No single model wins on every dimension. Rankings depend on what you measure.</div>
    <div class="figure">@@LEADERBOARD@@</div>
    <p class="caption">
      Figure 4. Three-panel leaderboard. Each panel sorted independently by its own metric:
      bootstrap accuracy (left), expected calibration error (middle, lower is better),
      perturbation robustness &Delta; (right, closer to zero is better). Top two slots swap
      between Claude (#1 accuracy) and ChatGPT (#1 calibration), with model order shifting
      across all three views.
    </p>
  </section>

  <!-- ============ RESULTS 3 — ROBUSTNESS ============ -->
  <section class="robustness">
    <div class="figure">@@ROBUSTNESS@@</div>
    <div>
      <div class="eyebrow"><span class="num">08</span>Results 3 &middot; Robustness</div>
      <div class="section-title">Performance shifts vary by task family, not just by model.</div>
      <p class="body-text">
        Each cell reports per-task-type &Delta; between base and perturbed-task NMACR, with
        diverging colormap centred at zero. Red cells mark where rephrasing or numerical
        substitution hurts; blue cells mark surprising gains. Stable rows correspond to
        well-specified task types; volatile rows expose models that match patterns rather
        than reason from priors.
      </p>
      <div class="callouts">
        <div class="callout">
          <div class="label">Stable</div>
          <div class="text">Closed-form posterior tasks (DISC_MEDIAN, BETA_BIN) survive both rephrase and numerical perturbations across all five models.</div>
        </div>
        <div class="callout warn">
          <div class="label">Volatile</div>
          <div class="text">Hierarchical and decision-theoretic task types swing by &gt; 0.15 &Delta; &mdash; reasoning depth, not surface form, is what's tested.</div>
        </div>
        <div class="callout bad">
          <div class="label">Pattern-match flag</div>
          <div class="text">Rows where one model collapses while peers hold steady localize where memorized templates substitute for inference.</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ RESULTS 4 — CALIBRATION ============ -->
  <section class="calibration">
    <div class="eyebrow"><span class="num">09</span>Results 4 &middot; Calibration</div>
    <div class="section-title">Verbalized vs self-consistency ECE &mdash; the measurement method changes the ranking.</div>
    <div class="figure">@@CALIBRATION@@</div>
    <p class="caption">
      Figure 5. Paired expected calibration error (ECE) per model under two elicitation
      protocols: verbalized confidence (left of each pair) vs self-consistency over k
      samples (right). Lower is better. ChatGPT leads under verbalized confidence;
      DeepSeek closes the gap under self-consistency. Calibration claims that name only
      one method are method-bound, not model-bound.
    </p>
  </section>

  <!-- ============ TAXONOMY + CONCLUSION ============ -->
  <section class="tax-row">
    <div>
      <div class="eyebrow"><span class="num">10</span>Failure taxonomy</div>
      <div class="section-title">Assumption violations dominate the audited error budget.</div>
      <div class="figure">@@TAXONOMY@@</div>
      <p class="caption">
        Figure 6. Stacked failure modes per model on the L1-audited subset. The
        Assumption Violation band (amber) is the largest contributor across the cohort &mdash;
        the locus of remaining headroom for Bayesian reasoning evaluation.
      </p>
    </div>
    <div>
      <div class="eyebrow"><span class="num">11</span>Conclusion</div>
      <div class="section-title">Four takeaways.</div>
      <ul class="bullets">
        <li><strong>Rankings depend on measurement.</strong> Top two models swap between accuracy and calibration views; a single leaderboard hides this.</li>
        <li><strong>Assumption articulation is the dominant gap.</strong> All five models lose more here than on numerical accuracy.</li>
        <li><strong>Calibration measurement method matters.</strong> Verbalized vs self-consistency reorder the cohort &mdash; claims must specify method.</li>
        <li><strong>Smaller models can match larger ones</strong> on specific dimensions (Mistral on robustness, DeepSeek on self-consistency calibration), undermining size-only narratives.</li>
      </ul>
      <p class="caption" style="margin-top:5mm">
        Future work: extend to multi-turn evaluations, broaden judge ensembles beyond a single
        Llama 3.3 70B reader, ground the assumption-articulation rubric against expert
        statisticians.
      </p>
    </div>
  </section>

  <!-- ============ FOOTER ============ -->
  <footer class="footer">
    <div>
      <div class="eyebrow">References</div>
      <ol>
        <li>Du, J. et al. (2025). <em>Multi-dimensional evaluation rubrics for LLM reasoning.</em></li>
        <li>Boye, J. &amp; Moell, B. (2025). <em>Verbalized confidence and self-consistency calibration.</em></li>
        <li>Yamauchi, R. (2025). <em>Assumption articulation as a probe of Bayesian competence.</em></li>
        <li>Wei, J. et al. (2022). <em>Chain-of-thought prompting elicits reasoning in large language models.</em> NeurIPS.</li>
        <li>Chen, M. et al. (2022). <em>Self-consistency improves chain-of-thought reasoning.</em> ICLR.</li>
        <li>Nagarkar, S. (2026). <em>External LLM judges for benchmark validation.</em></li>
        <li>Liu, Y. (2025). <em>Robustness of LLM mathematical reasoning under perturbation.</em></li>
      </ol>
    </div>
    <div>
      <div class="eyebrow">Acknowledgments</div>
      <div>
        Thanks to <strong>Dr. Vahe Movsisyan</strong> for supervision and methodological feedback,
        the AUA Akian College of Science &amp; Engineering for compute support, and the
        DS 299 cohort for productive critique throughout the term.
      </div>
    </div>
    <div class="qr-block">
      <div class="eyebrow">Contact &middot; Code &middot; Data</div>
      <div class="contact-row">albert.simonyan1@icloud.com</div>
      <div class="contact-row">bayes-benchmark.vercel.app</div>
      <div class="contact-row">github.com/albertsimonyan74/<br>capstone-llm-stats</div>
      <div class="qr-stub">[QR<br>bayes-benchmark<br>.vercel.app]</div>
    </div>
  </footer>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
