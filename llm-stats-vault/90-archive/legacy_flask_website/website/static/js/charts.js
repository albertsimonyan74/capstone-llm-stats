/**
 * charts.js — All Chart.js visualizations
 */

// ── Color palette ─────────────────────────────────────────────
const PALETTE = {
  claude:   { primary: '#00CED1', secondary: 'rgba(0,206,209,0.15)', border: '#00CED1' },
  gemini:   { primary: '#00BFFF', secondary: 'rgba(0,191,255,0.15)', border: '#00BFFF' },
  chatgpt:  { primary: '#00FFFF', secondary: 'rgba(0,255,255,0.12)', border: '#00FFFF' },
  deepseek: { primary: '#7FFFD4', secondary: 'rgba(127,255,212,0.12)', border: '#7FFFD4' },
  default:  { primary: '#6699FF', secondary: 'rgba(102,153,255,0.12)', border: '#6699FF' },
};

function getModelColor(model) {
  const key = model.toLowerCase();
  for (const k of Object.keys(PALETTE)) {
    if (key.includes(k)) return PALETTE[k];
  }
  return PALETTE.default;
}

// ── Chart.js defaults ─────────────────────────────────────────
Chart.defaults.color = '#8BB8CC';
Chart.defaults.font.family = "'Space Grotesk', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.borderColor = 'rgba(0, 206, 209, 0.1)';

function baseChartOptions(extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: { color: '#8BB8CC', boxWidth: 12, padding: 14, font: { size: 11 } }
      },
      tooltip: {
        backgroundColor: 'rgba(13, 27, 42, 0.95)',
        borderColor: 'rgba(0, 206, 209, 0.4)',
        borderWidth: 1,
        titleColor: '#00CED1',
        bodyColor: '#E0F7FF',
        padding: 10,
      }
    },
    ...extra
  };
}

// ── Donut: Tasks by Tier ──────────────────────────────────────
function renderTierDonut(canvasId, tierData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  const labels = Object.keys(tierData).map(t => `Tier ${t}`);
  const data   = Object.values(tierData);

  ctx._chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: [
          'rgba(0, 206, 209, 0.7)',
          'rgba(0, 191, 255, 0.7)',
          'rgba(127, 255, 212, 0.65)',
          'rgba(0, 71, 171, 0.7)',
        ],
        borderColor: [
          '#00CED1', '#00BFFF', '#7FFFD4', '#0047AB'
        ],
        borderWidth: 1.5,
      }]
    },
    options: {
      ...baseChartOptions(),
      cutout: '65%',
      plugins: {
        ...baseChartOptions().plugins,
        legend: { position: 'bottom', labels: { color: '#8BB8CC', padding: 12 } }
      }
    }
  });
}

// ── Donut: Tasks by Category ──────────────────────────────────
function renderCategoryDonut(canvasId, numeric, conceptual) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  ctx._chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Numeric', 'Conceptual'],
      datasets: [{
        data: [numeric, conceptual],
        backgroundColor: ['rgba(0, 206, 209, 0.7)', 'rgba(0, 71, 171, 0.7)'],
        borderColor: ['#00CED1', '#6699FF'],
        borderWidth: 1.5,
      }]
    },
    options: {
      ...baseChartOptions(),
      cutout: '65%',
      plugins: {
        ...baseChartOptions().plugins,
        legend: { position: 'bottom', labels: { color: '#8BB8CC', padding: 12 } }
      }
    }
  });
}

// ── Radar: Model comparison ───────────────────────────────────
function renderRadarChart(canvasId, byTypeData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  // Group task types into categories for radar axes
  const radarCategories = {
    'Conjugate Models': ['BETA_BINOM','GAMMA_POISSON','NORMAL_GAMMA','DIRICHLET','BINOM_FLAT'],
    'Decision Theory':  ['MINIMAX','BAYES_RISK','BIAS_VAR','OPT_SCALED','MSE_COMPARE'],
    'Statistical Inf.': ['FISHER_INFO','RC_BOUND','UNIFORM_MLE','MLE_EFFICIENCY'],
    'Markov & Sim.':    ['MARKOV','STATIONARY','GAMBLER','BOX_MULLER'],
    'Order Statistics': ['ORDER_STAT','RANGE_DIST','DISC_MEDIAN'],
    'Bayesian Adv.':    ['HPD','JEFFREYS','PPC','MLE_MAP','LOG_ML','BAYES_FACTOR','BAYES_REG','CI_CREDIBLE'],
    'Regression':       ['REGRESSION'],
    'Conceptual':       ['CONCEPTUAL'],
  };

  const labels  = Object.keys(radarCategories);
  const models  = Object.keys(byTypeData);
  const datasets = models.map(model => {
    const c = getModelColor(model);
    const scores = labels.map(cat => {
      const types = radarCategories[cat];
      const vals  = types.map(t => byTypeData[model]?.[t]).filter(v => v != null);
      return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
    });
    return {
      label: model,
      data: scores,
      backgroundColor: c.secondary,
      borderColor: c.primary,
      borderWidth: 2,
      pointBackgroundColor: c.primary,
      pointRadius: 4,
    };
  });

  ctx._chart = new Chart(ctx, {
    type: 'radar',
    data: { labels, datasets },
    options: {
      ...baseChartOptions(),
      scales: {
        r: {
          min: 0, max: 1,
          ticks: { stepSize: 0.25, color: '#4A6070', backdropColor: 'transparent', font: { size: 9 } },
          grid:  { color: 'rgba(0,206,209,0.1)' },
          pointLabels: { color: '#8BB8CC', font: { size: 10 } },
          angleLines: { color: 'rgba(0,206,209,0.15)' },
        }
      }
    }
  });
}

// ── Grouped Bar: Score by Task Type ──────────────────────────
function renderBarByType(canvasId, byTypeData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  const allTypes = new Set();
  Object.values(byTypeData).forEach(m => Object.keys(m).forEach(t => allTypes.add(t)));
  const labels  = [...allTypes].sort();
  const models  = Object.keys(byTypeData);

  const datasets = models.map(model => {
    const c = getModelColor(model);
    return {
      label: model,
      data:  labels.map(t => byTypeData[model]?.[t] ?? null),
      backgroundColor: c.secondary,
      borderColor: c.primary,
      borderWidth: 1.5,
      borderRadius: 4,
    };
  });

  ctx._chart = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      ...baseChartOptions(),
      scales: {
        x: {
          ticks: { color: '#4A6070', maxRotation: 60, font: { size: 9 } },
          grid:  { color: 'rgba(0,206,209,0.05)' },
        },
        y: {
          min: 0, max: 1,
          ticks: { color: '#4A6070', stepSize: 0.25 },
          grid:  { color: 'rgba(0,206,209,0.08)' },
        }
      }
    }
  });
}

// ── Box / Score Distribution (simulated with bar) ─────────────
function renderScoreDistribution(canvasId, summaryData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  const models = Object.keys(summaryData);
  const scores = models.map(m => summaryData[m].avg_score);
  const colors = models.map(m => getModelColor(m));

  ctx._chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: models,
      datasets: [{
        label: 'Avg Score',
        data: scores,
        backgroundColor: colors.map(c => c.secondary),
        borderColor: colors.map(c => c.primary),
        borderWidth: 2,
        borderRadius: 6,
      }]
    },
    options: {
      ...baseChartOptions(),
      indexAxis: 'y',
      scales: {
        x: { min: 0, max: 1, grid: { color: 'rgba(0,206,209,0.08)' }, ticks: { color: '#4A6070' } },
        y: { grid: { display: false }, ticks: { color: '#8BB8CC' } },
      },
      plugins: { ...baseChartOptions().plugins, legend: { display: false } }
    }
  });
}

// ── Scatter: Latency vs Accuracy ──────────────────────────────
function renderScatterLatency(canvasId, summaryData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  const datasets = Object.entries(summaryData).map(([model, d]) => {
    const c = getModelColor(model);
    return {
      label: model,
      data: [{ x: d.avg_latency_ms || 0, y: d.avg_score || 0 }],
      backgroundColor: c.secondary,
      borderColor: c.primary,
      borderWidth: 2,
      pointRadius: 10,
      pointHoverRadius: 14,
    };
  });

  ctx._chart = new Chart(ctx, {
    type: 'scatter',
    data: { datasets },
    options: {
      ...baseChartOptions(),
      scales: {
        x: {
          title: { display: true, text: 'Avg Latency (ms)', color: '#4A6070' },
          grid: { color: 'rgba(0,206,209,0.08)' },
          ticks: { color: '#4A6070' },
        },
        y: {
          title: { display: true, text: 'Avg Score', color: '#4A6070' },
          min: 0, max: 1,
          grid: { color: 'rgba(0,206,209,0.08)' },
          ticks: { color: '#4A6070' },
        }
      }
    }
  });
}

// ── Export ────────────────────────────────────────────────────
window.Charts = {
  renderTierDonut,
  renderCategoryDonut,
  renderRadarChart,
  renderBarByType,
  renderScoreDistribution,
  renderScatterLatency,
  getModelColor,
};
