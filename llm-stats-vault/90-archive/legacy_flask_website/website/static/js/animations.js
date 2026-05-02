/**
 * animations.js — Particle background + glow effects
 */

// ── Particle System ───────────────────────────────────────────
class ParticleSystem {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.numParticles = 80;
    this.maxDistance = 150;
    this.colors = ['#00CED1', '#00FFFF', '#7FFFD4', '#00BFFF', '#0047AB'];
    this.animFrame = null;
    this.resize();
    this.init();
    this.animate();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    const parent = this.canvas.parentElement;
    this.canvas.width  = parent ? parent.offsetWidth  : window.innerWidth;
    this.canvas.height = parent ? parent.offsetHeight : window.innerHeight;
  }

  init() {
    this.particles = [];
    for (let i = 0; i < this.numParticles; i++) {
      this.particles.push({
        x:     Math.random() * this.canvas.width,
        y:     Math.random() * this.canvas.height,
        vx:    (Math.random() - 0.5) * 0.4,
        vy:    (Math.random() - 0.5) * 0.4,
        r:     Math.random() * 2 + 1,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        alpha: Math.random() * 0.6 + 0.2,
      });
    }
  }

  update() {
    for (const p of this.particles) {
      p.x += p.vx;
      p.y += p.vy;
      // Wrap around edges
      if (p.x < 0)  p.x = this.canvas.width;
      if (p.x > this.canvas.width)  p.x = 0;
      if (p.y < 0)  p.y = this.canvas.height;
      if (p.y > this.canvas.height) p.y = 0;
    }
  }

  draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw connecting lines
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const a = this.particles[i];
        const b = this.particles[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < this.maxDistance) {
          const alpha = (1 - dist / this.maxDistance) * 0.25;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(0, 206, 209, ${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    // Draw particles
    for (const p of this.particles) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
      // Glow
      ctx.shadowColor = p.color;
      ctx.shadowBlur = 6;
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.globalAlpha = 1;
    }
  }

  animate() {
    this.update();
    this.draw();
    this.animFrame = requestAnimationFrame(() => this.animate());
  }

  destroy() {
    if (this.animFrame) cancelAnimationFrame(this.animFrame);
  }
}

// ── Counter Animation ─────────────────────────────────────────
function animateCounter(el, target, duration = 1800) {
  const start = performance.now();
  const isFloat = String(target).includes('.');
  const decimals = isFloat ? String(target).split('.')[1].length : 0;

  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = eased * target;
    el.textContent = isFloat ? current.toFixed(decimals) : Math.floor(current);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── Intersection Observer for fade-ins ────────────────────────
function initFadeIns() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// ── Navbar active link on scroll ─────────────────────────────
function initNavHighlight() {
  const sections = document.querySelectorAll('.section');
  const navLinks = document.querySelectorAll('.nav-links a');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navLinks.forEach(a => {
          a.classList.toggle('active', a.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(s => observer.observe(s));
}

// ── Typing animation ─────────────────────────────────────────
function typeText(el, text, speed = 50) {
  el.textContent = '';
  let i = 0;
  const cursor = document.createElement('span');
  cursor.className = 'typing-cursor';
  el.parentElement.appendChild(cursor);

  function type() {
    if (i < text.length) {
      el.textContent += text[i++];
      setTimeout(type, speed);
    } else {
      cursor.remove();
    }
  }
  type();
}

// ── Scan line ─────────────────────────────────────────────────
function initScanLine() {
  const el = document.createElement('div');
  el.className = 'scan-line';
  document.body.appendChild(el);
}

// ── Export ────────────────────────────────────────────────────
window.ParticleSystem  = ParticleSystem;
window.animateCounter  = animateCounter;
window.initFadeIns     = initFadeIns;
window.initNavHighlight = initNavHighlight;
window.typeText        = typeText;
window.initScanLine    = initScanLine;
