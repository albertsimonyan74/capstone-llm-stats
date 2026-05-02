/**
 * main.js — Page routing, initialization, and section rendering
 */

// ── State ─────────────────────────────────────────────────────
const State = {
  status:    null,
  taskTypes: null,
  tasks:     [],
  filters: {
    type: '', tier: '', category: '', search: ''
  },
  refreshInterval: null,
};

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  initScanLine();
  initFadeIns();
  initNavHighlight();
  initModal();
  initNavSmoothScroll();

  // Particle background
  new ParticleSystem('particle-canvas');

  // Load static data
  await Promise.all([
    loadStatus(),
    loadTaskTypes(),
  ]);

  // Render all sections
  renderOverview();
  renderBenchmarkSection();
  renderModelsSection();
  await renderTasksSection();
  await renderResultsSection();

  // Auto-refresh results every 30 seconds
  State.refreshInterval = setInterval(async () => {
    await loadStatus();
    await renderResultsSection();
    showRefreshPing();
  }, 30000);
});

// ── Data loaders ──────────────────────────────────────────────
async function loadStatus() {
  try {
    State.status = await API.status();
  } catch (e) {
    console.warn('Could not load status:', e);
    State.status = { total_tasks: 136, tasks_by_tier: {1:9,2:45,3:69,4:13}, total_runs: 0, benchmark_ready: false };
  }
}

async function loadTaskTypes() {
  try {
    State.taskTypes = await API.taskTypes();
  } catch (e) {
    console.warn('Could not load task types:', e);
    State.taskTypes = [];
  }
}

// ── Section 1: Overview ───────────────────────────────────────
function renderOverview() {
  const s = State.status || {};

  // Animate counters
  const counterEls = document.querySelectorAll('[data-counter]');
  counterEls.forEach(el => {
    const target = parseFloat(el.dataset.counter);
    animateCounter(el, target);
  });
}

// ── Section 2: Benchmark Framework ───────────────────────────
function renderBenchmarkSection() {
  const s = State.status || {};
  const tierData = s.tasks_by_tier || { '1': 9, '2': 45, '3': 69, '4': 13 };

  Charts.renderTierDonut('chart-tier', tierData);
  Charts.renderCategoryDonut('chart-category', 126, 10);
}

// ── Section 3: Models — static render via HTML ────────────────
// (Already in HTML, nothing dynamic needed)

// ── Section 4: Task Explorer ──────────────────────────────────

// Task filter state
const TaskFilters = { tiers: [], category: 'all', search_id: '', search_topic: '' };

async function renderTasksSection() {
  // Wire up tier checkboxes
  document.querySelectorAll('.tier-checkbox').forEach(cb => {
    cb.addEventListener('change', function () {
      const tier = parseInt(this.value);
      if (this.checked) {
        if (!TaskFilters.tiers.includes(tier)) TaskFilters.tiers.push(tier);
      } else {
        TaskFilters.tiers = TaskFilters.tiers.filter(t => t !== tier);
      }
      loadTasks();
    });
  });

  // Wire up category buttons
  document.querySelectorAll('.category-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      TaskFilters.category = this.dataset.category || 'all';
      loadTasks();
    });
  });

  // Wire up Task ID search
  const searchTaskId  = document.getElementById('search-task-id');
  const searchIdBtn   = document.getElementById('search-id-btn');
  const searchTopic   = document.getElementById('search-topic');
  const searchTopicBtn = document.getElementById('search-topic-btn');
  const clearBtn      = document.getElementById('clear-filters');

  const doSearchId = () => { TaskFilters.search_id = searchTaskId?.value.trim() || ''; loadTasks(); };
  const doSearchTopic = () => { TaskFilters.search_topic = searchTopic?.value.trim() || ''; loadTasks(); };

  if (searchTaskId)  searchTaskId.addEventListener('input',  debounce(doSearchId, 300));
  if (searchIdBtn)   searchIdBtn.addEventListener('click',   doSearchId);
  if (searchTaskId)  searchTaskId.addEventListener('keydown', e => { if (e.key === 'Enter') doSearchId(); });

  if (searchTopic)   searchTopic.addEventListener('input',   debounce(doSearchTopic, 300));
  if (searchTopicBtn) searchTopicBtn.addEventListener('click', doSearchTopic);
  if (searchTopic)   searchTopic.addEventListener('keydown',  e => { if (e.key === 'Enter') doSearchTopic(); });

  // Clear all
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      TaskFilters.tiers = []; TaskFilters.category = 'all';
      TaskFilters.search_id = ''; TaskFilters.search_topic = '';
      document.querySelectorAll('.tier-checkbox').forEach(cb => cb.checked = false);
      document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
      document.querySelector('.category-btn[data-category="all"]')?.classList.add('active');
      if (searchTaskId)  searchTaskId.value  = '';
      if (searchTopic)   searchTopic.value   = '';
      loadTasks();
    });
  }

  await loadTasks();
}

async function loadTasks() {
  const container = document.getElementById('tasks-grid');
  if (!container) { console.error('[TASKS] #tasks-grid not found'); return; }

  container.innerHTML = '<div class="task-list-placeholder" style="opacity:0.5">Loading…</div>';

  const params = new URLSearchParams({ limit: '50' });
  if (TaskFilters.tiers.length)          params.set('tier',         TaskFilters.tiers.join(','));
  if (TaskFilters.category !== 'all')    params.set('category',     TaskFilters.category);
  if (TaskFilters.search_id)             params.set('search_id',    TaskFilters.search_id);
  if (TaskFilters.search_topic)          params.set('search_topic', TaskFilters.search_topic);

  console.log('[TASKS] GET /api/tasks?' + params.toString());

  try {
    const resp = await fetch('/api/tasks?' + params.toString());
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data  = await resp.json();
    if (data.error) throw new Error(data.error);

    const tasks = data.tasks || (Array.isArray(data) ? data : []);
    State.tasks = tasks;

    const countEl = document.getElementById('tasks-count');
    if (countEl) countEl.textContent = `Showing ${tasks.length} of ${data.total_all || tasks.length} tasks`;

    renderTaskCards(tasks);
  } catch (e) {
    console.error('[TASKS]', e);
    container.innerHTML = `<div class="task-list-placeholder" style="color:#E24B4A">Failed to load tasks: ${e.message}</div>`;
  }
}

const TIER_LABELS = { 1: 'BASIC', 2: 'INTERMEDIATE', 3: 'ADVANCED', 4: 'EXPERT' };
const TIER_COLORS = { 1: '#7FFFD4', 2: '#00CED1', 3: '#00BFFF', 4: '#0047AB' };

function renderTaskCard(t) {
  const tierColor = TIER_COLORS[t.tier] || '#00CED1';
  const tierLbl   = TIER_LABELS[t.tier] || 'UNKNOWN';

  // Description: prefer explicit description, then notes.topic, then task_type
  const rawDesc = t.description
    || (t.notes && typeof t.notes === 'object' ? t.notes.topic : t.notes)
    || t.task_type
    || '';
  const descText = rawDesc.replace(/_/g, ' ');

  // Bottom target/rubric pill
  const nNum    = t.n_numeric || (Array.isArray(t.numeric_targets) ? t.numeric_targets.length : 0);
  const nRubric = t.n_rubric  || (Array.isArray(t.rubric_keys)     ? t.rubric_keys.length     : 0);
  let targetsHtml = '';
  if (t.category === 'conceptual' && nRubric) {
    targetsHtml = `<div class="task-targets"><span class="target-label">RUBRIC</span><span class="target-value">${nRubric} key${nRubric !== 1 ? 's' : ''}</span></div>`;
  } else if (nNum) {
    targetsHtml = `<div class="task-targets"><span class="target-label">TARGETS</span><span class="target-value">${nNum} numeric</span></div>`;
  }

  return `
    <div class="task-card" onclick="openTaskModal('${t.task_id}')">
      <div class="task-card-header">
        <span class="task-id">${escHtml(t.task_id)}</span>
        <span class="task-tier-badge" style="color:${tierColor};border-color:${tierColor}60">
          T${t.tier} · ${tierLbl}
        </span>
      </div>
      <div class="task-type-label">${escHtml(t.task_type || '')}</div>
      <p class="task-desc">${escHtml(descText.substring(0, 110))}${descText.length > 110 ? '…' : ''}</p>
      ${targetsHtml}
      <div class="task-card-footer">
        <span class="task-cat-tag task-cat-${t.category || 'numeric'}">${(t.category || 'numeric').toUpperCase()}</span>
        <span class="view-task-arrow">VIEW →</span>
      </div>
    </div>`;
}

function renderTaskCards(tasks) {
  const container = document.getElementById('tasks-grid');
  if (!container) return;

  if (!tasks || !tasks.length) {
    container.innerHTML = '<div class="task-list-placeholder">No tasks match the current filters.</div>';
    return;
  }

  container.innerHTML = tasks.map(renderTaskCard).join('');

  // Stagger fade-in
  container.querySelectorAll('.task-card').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    setTimeout(() => {
      el.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, i * 25);
  });
}

// ── Section 5: Results Dashboard ──────────────────────────────
async function renderResultsSection() {
  const container = document.getElementById('results-container');
  if (!container) return;

  let summary, byType, leaderboard;
  try {
    [summary, byType, leaderboard] = await Promise.all([
      API.resultsSummary(),
      API.resultsByType(),
      API.leaderboard(),
    ]);
  } catch (e) {
    console.warn('Failed to load results:', e);
    return;
  }

  const totalRuns = summary.total_runs || 0;
  const models    = summary.models || {};
  const hasRealResults = totalRuns > 1 || Object.keys(models).length > 1;

  // Show awaiting or results
  const awaitingEl  = document.getElementById('results-awaiting');
  const dashboardEl = document.getElementById('results-dashboard');

  if (!hasRealResults && totalRuns <= 1) {
    if (awaitingEl)  awaitingEl.style.display = 'block';
    if (dashboardEl) dashboardEl.style.display = 'none';
  } else {
    if (awaitingEl)  awaitingEl.style.display = 'none';
    if (dashboardEl) dashboardEl.style.display = 'block';

    renderLeaderboard(leaderboard);
    Charts.renderRadarChart('chart-radar', byType);
    Charts.renderBarByType('chart-bar-type', byType);
    Charts.renderScoreDistribution('chart-dist', models);
    Charts.renderScatterLatency('chart-scatter', models);
  }

  // Always update stub leaderboard if we have at least 1 run
  if (leaderboard.length > 0) {
    if (awaitingEl)  awaitingEl.style.display = 'none';
    if (dashboardEl) dashboardEl.style.display = 'block';
    renderLeaderboard(leaderboard);

    if (Object.keys(byType).length > 0) {
      Charts.renderRadarChart('chart-radar', byType);
      Charts.renderBarByType('chart-bar-type', byType);
    }
    Charts.renderScoreDistribution('chart-dist', models);
    Charts.renderScatterLatency('chart-scatter', models);
  }
}

function renderLeaderboard(leaderboard) {
  const el = document.getElementById('leaderboard-list');
  if (!el) return;

  const rankClass = (rank) => rank === 1 ? 'gold' : rank === 2 ? 'silver' : rank === 3 ? 'bronze' : '';
  const modelMeta = {
    claude:   { full: 'Claude Sonnet 4.5', provider: 'Anthropic' },
    gemini:   { full: 'Gemini 1.5 Flash',  provider: 'Google' },
    chatgpt:  { full: 'GPT-4o Mini',       provider: 'OpenAI' },
    deepseek: { full: 'DeepSeek Chat',      provider: 'DeepSeek AI' },
  };

  el.innerHTML = leaderboard.map(entry => {
    const meta  = modelMeta[entry.model.toLowerCase()] || { full: entry.model, provider: '—' };
    const rc    = rankClass(entry.rank);
    const score = (entry.avg_score * 100).toFixed(1);
    const pass  = (entry.pass_rate * 100).toFixed(0);
    const lat   = entry.avg_latency_ms > 0 ? `${entry.avg_latency_ms.toFixed(0)}ms` : '—';

    return `
      <div class="lb-card fade-in visible">
        <div class="lb-rank ${rc}">#${entry.rank}</div>
        <div>
          <div class="lb-model">${meta.full}</div>
          <div class="lb-model-sub">${entry.model} · ${meta.provider}</div>
          <div class="score-bar">
            <div class="score-bar-track">
              <div class="score-bar-fill" style="width:${score}%"></div>
            </div>
          </div>
        </div>
        <div class="lb-metric">
          <div class="metric-val">${score}%</div>
          <div class="metric-lbl">Avg Score</div>
        </div>
        <div class="lb-metric">
          <div class="metric-val">${pass}%</div>
          <div class="metric-lbl">Pass Rate</div>
        </div>
        <div class="lb-metric">
          <div class="metric-val">${entry.n_tasks}</div>
          <div class="metric-lbl">Tasks Run</div>
        </div>
        <div class="lb-metric">
          <div class="metric-val">${lat}</div>
          <div class="metric-lbl">Avg Latency</div>
        </div>
      </div>`;
  }).join('');
}

// ── Modal ─────────────────────────────────────────────────────
function initModal() {
  // Legacy overlay (if present)
  const legacyOverlay = document.getElementById('modal-overlay');
  if (legacyOverlay) {
    legacyOverlay.addEventListener('click', e => {
      if (e.target === legacyOverlay) closeTaskModal();
    });
  }
  // New task modal
  const taskModal = document.getElementById('task-modal');
  if (taskModal) {
    taskModal.addEventListener('click', e => {
      if (e.target === taskModal) closeTaskModal();
    });
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeTaskModal();
  });
}

async function openTaskModal(taskId) {
  const modal = document.getElementById('task-modal');
  if (!modal) return;

  // Show modal with loading state
  modal.style.display = 'flex';
  document.getElementById('modal-task-id').textContent  = taskId;
  document.getElementById('modal-question').textContent = 'Loading…';
  document.getElementById('modal-targets-section').style.display = 'none';
  document.getElementById('modal-rubric-section').style.display  = 'none';

  try {
    const task = await API.task(taskId);

    document.getElementById('modal-task-id').textContent = task.task_id;

    // Prompt / question text
    const promptEl = document.getElementById('modal-question');
    promptEl.textContent = task.question || task.prompt || '(No prompt generated)';

    // Numeric targets
    const numTargets = task.numeric_targets || [];
    const targetsSection = document.getElementById('modal-targets-section');
    const targetsEl      = document.getElementById('modal-targets');
    if (numTargets.length > 0) {
      targetsEl.innerHTML = numTargets.map(nt => `
        <div class="target-row">
          <span class="target-key">${escHtml(nt.key)}</span>
          <span class="target-val">${typeof nt.true_value === 'number' ? nt.true_value.toFixed(6) : nt.true_value}</span>
        </div>`).join('');
      targetsSection.style.display = 'block';
    }

    // Rubric keys
    const rubricKeys    = task.rubric_keys || [];
    const rubricSection = document.getElementById('modal-rubric-section');
    const rubricEl      = document.getElementById('modal-rubric');
    if (rubricKeys.length > 0) {
      rubricEl.innerHTML = rubricKeys.map(k => `<div class="rubric-key">&#9670; ${escHtml(k)}</div>`).join('');
      rubricSection.style.display = 'block';
    }

    // Reference answer
    const refSection = document.getElementById('modal-ref-section');
    const refEl      = document.getElementById('modal-ref');
    if (refSection && refEl) {
      if (task.reference_answer) {
        refEl.textContent = task.reference_answer;
        refSection.style.display = 'block';
      } else {
        refSection.style.display = 'none';
      }
    }
  } catch (e) {
    document.getElementById('modal-question').textContent = `Failed to load task: ${e.message}`;
  }
}

function closeTaskModal() {
  const modal = document.getElementById('task-modal');
  if (modal) modal.style.display = 'none';
  // legacy
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.classList.remove('open');
}

// ── Refresh indicator ─────────────────────────────────────────
function showRefreshPing() {
  const badge = document.getElementById('refresh-badge');
  if (!badge) return;
  const now = new Date();
  badge.querySelector('.refresh-time').textContent =
    `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`;
}

// ── Nav smooth scroll ─────────────────────────────────────────
function initNavSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// ── Utilities ─────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

window.openTaskModal  = openTaskModal;
window.closeTaskModal = closeTaskModal;
// legacy alias
window.closeModal     = closeTaskModal;
