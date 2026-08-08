// broadcast-scenes.js — Starting Soon / BRB / Ending full-screen overlay
// scenes: aurora canvas backgrounds + the Starting Soon countdown. Each
// scene is its own Browser Source page (see app/routes/overlay.py) — no
// in-page scene switching here, `init()` just (re)starts whatever aurora
// canvases/timer exist in the current page's DOM. Starting Soon's timer
// state lives server-side in BroadcastSceneService (see that module) and
// reaches its page through the same data-ctl string overlay.js already
// polls for ticker/seats/standings on the Live pages (see parseCtl there).
//
// Kept in its own file purely for size/readability — loaded alongside
// overlay.js on the Starting Soon page (and standalone, without overlay.js,
// on the static BRB/Ending pages), plain vanilla JS to match the rest of
// the overlay (no build step, no dependencies).
(function () {
  const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let auroraEngines = [];
  let timerRaf = null;

  // Soft radial blobs, no per-frame ctx.filter blur (expensive at 1080p on
  // every frame) — the gradient's own alpha falloff already reads as soft.
  const DEFAULT_BLOBS = [
    { cx: .3, cy: .4, radiusX: .12, radiusY: .08, speed: .015, pulseSpeed: .05, phase: 0, size: .55, color: 'rgba(199,165,82,.16)', colorMid: 'rgba(199,165,82,.06)' },
    { cx: .72, cy: .58, radiusX: .1, radiusY: .1, speed: .011, pulseSpeed: .04, phase: 2.1, size: .5, color: 'rgba(123,15,15,.14)', colorMid: 'rgba(123,15,15,.05)' },
    { cx: .5, cy: .28, radiusX: .08, radiusY: .06, speed: .009, pulseSpeed: .03, phase: 4.4, size: .4, color: 'rgba(199,165,82,.09)', colorMid: 'rgba(199,165,82,.03)' },
  ];
  const SLOW_BLOBS = [
    { cx: .35, cy: .5, radiusX: .05, radiusY: .04, speed: .004, pulseSpeed: .012, phase: 0, size: .5, color: 'rgba(199,165,82,.1)', colorMid: 'rgba(199,165,82,.04)' },
    { cx: .65, cy: .5, radiusX: .04, radiusY: .05, speed: .003, pulseSpeed: .01, phase: 3, size: .42, color: 'rgba(123,15,15,.09)', colorMid: 'rgba(123,15,15,.03)' },
  ];

  function startAurora(canvas, blobs) {
    const ctx = canvas.getContext('2d');
    let dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = canvas.clientWidth * dpr;
      canvas.height = canvas.clientHeight * dpr;
    }
    resize();
    window.addEventListener('resize', resize);

    const startedAt = performance.now();
    let raf = null;
    function draw() {
      const t = (performance.now() - startedAt) / 1000;
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);
      ctx.globalCompositeOperation = 'lighter';
      blobs.forEach((blob) => {
        const angle = t * blob.speed + blob.phase;
        const x = width * blob.cx + Math.cos(angle) * width * blob.radiusX;
        const y = height * blob.cy + Math.sin(angle * .7) * height * blob.radiusY;
        const pulse = .82 + Math.sin(t * blob.pulseSpeed + blob.phase) * .12;
        const r = width * blob.size * pulse;
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, r);
        gradient.addColorStop(0, blob.color);
        gradient.addColorStop(.6, blob.colorMid);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
      });
      ctx.globalCompositeOperation = 'source-over';
      raf = requestAnimationFrame(draw);
    }
    raf = requestAnimationFrame(draw);

    return {
      stop() {
        if (raf) cancelAnimationFrame(raf);
        window.removeEventListener('resize', resize);
      },
    };
  }

  function stopAllAurora() {
    auroraEngines.forEach((e) => e.stop());
    auroraEngines = [];
  }

  function formatTime(totalSeconds) {
    const s = Math.max(0, Math.round(totalSeconds));
    const mm = Math.floor(s / 60);
    const ss = s % 60;
    return String(mm).padStart(2, '0') + ':' + String(ss).padStart(2, '0');
  }

  function runTimer(durationSeconds, startedAtEpochSeconds) {
    const valueEl = document.querySelector('[data-scene-panel="starting_soon"] [data-timer-value]');
    if (timerRaf) cancelAnimationFrame(timerRaf);
    if (!valueEl) return;

    function tick() {
      let remaining = durationSeconds;
      if (startedAtEpochSeconds) {
        remaining = Math.max(0, durationSeconds - (Date.now() / 1000 - startedAtEpochSeconds));
      }
      valueEl.textContent = formatTime(remaining);
      timerRaf = requestAnimationFrame(tick);
    }
    tick();
  }

  /** (Re)starts every canvas engine currently in the DOM — call after any
   * full DOM swap (sig change) in overlay.js's poll(), same spot as
   * startTicker()/fitSeatNames(). Idempotent. */
  function init() {
    stopAllAurora();
    if (!REDUCED_MOTION) {
      document.querySelectorAll('[data-aurora-canvas]').forEach((canvas) => {
        const panel = canvas.closest('[data-scene-panel]');
        const blobs = panel && panel.dataset.scenePanel === 'brb' ? SLOW_BLOBS : DEFAULT_BLOBS;
        auroraEngines.push(startAurora(canvas, blobs));
      });
    }
    const startingSoon = document.querySelector('[data-scene-panel="starting_soon"]');
    if (startingSoon) {
      const duration = parseFloat(startingSoon.dataset.timerDuration || '0');
      const startedAt = parseFloat(startingSoon.dataset.timerStartedAt || '');
      runTimer(duration, Number.isNaN(startedAt) ? null : startedAt);
    }
  }

  function setTimer(durationSeconds, startedAtEpochSeconds) {
    runTimer(durationSeconds, startedAtEpochSeconds);
  }

  window.MSBroadcastScenes = { init, setTimer };
})();
