// Stream overlay poller — plain vanilla JS, no dependencies.
// Polls the fragment endpoint every few seconds, only replaces the DOM
// when the server-provided data-sig actually changed (so CSS animations
// already in progress aren't interrupted on a no-op poll), separately
// triggers the last-game results reveal for a limited time whenever
// data-last-finished-id changes, and separately again applies the
// admin-controlled panel visibility (data-ctl) as plain class toggles on
// the already-existing elements — so toggling from the control page
// animates instead of snapping, since it doesn't require a DOM replace.
//
// Also drives the two things CSS keyframes can't express on their own:
// a tiny DOM-based particle system (card-lock sparks, reveal-card dust
// convergence, drifting embers — see .ovl-spark in overlay.css) and the
// ticker's split-flap flip + numeric count-up.
(function () {
  const root = document.getElementById('overlay-root');
  if (!root) return;

  const FRAGMENT_URL = root.dataset.fragmentUrl;
  const POLL_MS   = parseInt(root.dataset.pollIntervalMs, 10)   || 5000;
  const REVEAL_MS = parseInt(root.dataset.revealDurationMs, 10) || 25000;
  const TICKER_MS = parseInt(root.dataset.tickerIntervalMs, 10) || 8000;

  const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let currentSig = root.firstElementChild ? root.firstElementChild.dataset.sig : null;
  let lastFinishedId = root.firstElementChild ? root.firstElementChild.dataset.lastFinishedId : '';
  let currentCtl = root.firstElementChild ? parseCtl(root.firstElementChild.dataset.ctl) : null;
  let currentTimerStartedAt = currentCtl ? currentCtl.timerStartedAt : null;
  let revealTimeoutHandle = null;
  let tickerHandle = null;
  let emberHandle = null;

  function parseCtl(str) {
    const parts = {};
    (str || 'tk=1|sh=1|sm=top5|rv=auto|sc=live|td=900|ts=0|ic=logo').split('|').forEach((pair) => {
      const [key, value] = pair.split('=');
      parts[key] = value;
    });
    return {
      ticker: parts.tk === '1',
      showSeats: parts.sh !== '0', // default to visible if the field is ever missing
      standingsMode: parts.sm || 'top5',
      revealOverride: parts.rv || 'auto',
      // Broadcast scene (Starting Soon/Live/BRB/Ending) + its countdown —
      // see app/services/broadcast_scene_service.py and broadcast-scenes.js.
      scene: parts.sc || 'live',
      timerDuration: parseFloat(parts.td || '0'),
      timerStartedAt: parseFloat(parts.ts || '0') || null,
      // Which of the (always-in-DOM) idle-hero center slots is active —
      // see app/routes/overlay.py's effective_idle_content.
      idleContent: parts.ic || 'logo',
    };
  }

  // ── Particle system ───────────────────────────────────────────────────
  // One primitive (.ovl-spark, styled in overlay.css) reused for three
  // jobs by varying which trajectory keyframe class is applied and what
  // --sp-* custom properties get set per spawn. Skips entirely under
  // prefers-reduced-motion (no DOM churn for an effect that's invisible).
  function spawnParticles(container, opts) {
    if (REDUCED_MOTION || !container) return;
    const {
      kind, count,
      size = [2, 4], dur = [500, 800], distance = [16, 34], delay = [0, 120],
    } = opts;
    for (let i = 0; i < count; i++) {
      const ang = Math.random() * Math.PI * 2;
      const dist = distance[0] + Math.random() * (distance[1] - distance[0]);
      const tx = Math.cos(ang) * dist;
      const ty = Math.sin(ang) * dist;
      const sz = size[0] + Math.random() * (size[1] - size[0]);
      const du = dur[0] + Math.random() * (dur[1] - dur[0]);
      const de = delay[0] + Math.random() * (delay[1] - delay[0]);

      const el = document.createElement('span');
      el.className = 'ovl-spark ovl-spark--' + kind;
      el.style.setProperty('--sp-tx', tx.toFixed(1) + 'px');
      el.style.setProperty('--sp-ty', ty.toFixed(1) + 'px');
      el.style.setProperty('--sp-size', sz.toFixed(1) + 'px');
      el.style.setProperty('--sp-dur', du.toFixed(0) + 'ms');
      el.style.setProperty('--sp-delay', de.toFixed(0) + 'ms');
      el.addEventListener('animationend', () => el.remove(), { once: true });
      container.appendChild(el);
    }
  }

  function readDelayMs(el) {
    const raw = getComputedStyle(el).getPropertyValue('--d').trim();
    const n = parseFloat(raw);
    return Number.isNaN(n) ? 0 : n;
  }

  // Fires a small gold burst from each seat card right as its metallic
  // frame ignites (ms-frame-ignite lands ~1.15s into that card's own
  // staggered entrance) — "residual energy" after materialization.
  function spawnCardEntranceBursts() {
    if (REDUCED_MOTION) return;
    root.querySelectorAll('.ms-seat-card').forEach((card) => {
      const d = readDelayMs(card);
      setTimeout(() => {
        spawnParticles(card, { kind: 'burst', count: 4, size: [2, 3.5], dur: [500, 750], distance: [14, 30] });
      }, d + 760);
    });
  }

  // Timed so the converging dust finishes collapsing into each reveal
  // card right as totem-resolve (overlay.css) lands.
  function spawnRevealBursts() {
    if (REDUCED_MOTION) return;
    root.querySelectorAll('.reveal-card').forEach((card) => {
      const particlesEl = card.querySelector('.reveal-card__particles');
      if (!particlesEl) return;
      const d = readDelayMs(card);
      setTimeout(() => {
        spawnParticles(particlesEl, { kind: 'converge', count: 5, size: [2, 3.5], dur: [400, 600], distance: [20, 46] });
      }, d + 880);
    });
  }

  // Sparse ember stream drifting up out of roughly where the reveal panel
  // sits, for as long as .reveal-active holds — the panel's "still hot"
  // residual life, distinct from the one-shot bursts above.
  function startEmbers() {
    if (REDUCED_MOTION || emberHandle) return;
    const container = root.querySelector('.ovl-embers');
    if (!container) return;
    emberHandle = setInterval(() => {
      const el = document.createElement('span');
      el.className = 'ovl-spark ovl-spark--ember';
      el.style.left = (42 + Math.random() * 16) + 'vw';
      el.style.top = (58 + Math.random() * 14) + 'vh';
      el.style.setProperty('--sp-tx', ((Math.random() - 0.5) * 40).toFixed(1) + 'px');
      el.style.setProperty('--sp-ty', (-(60 + Math.random() * 60)).toFixed(1) + 'px');
      el.style.setProperty('--sp-size', (2 + Math.random() * 2).toFixed(1) + 'px');
      el.style.setProperty('--sp-dur', (1800 + Math.random() * 1200).toFixed(0) + 'ms');
      el.addEventListener('animationend', () => el.remove(), { once: true });
      container.appendChild(el);
    }, 650);
  }
  function stopEmbers() {
    if (emberHandle) { clearInterval(emberHandle); emberHandle = null; }
  }

  // Nameplate fit strategy, in order — rather than jumping straight to
  // an ellipsis or a tiny shrunk font for every long nickname:
  //   1. One line at normal size (the common case — leave it alone).
  //   2. Doesn't fit AND the name has a space ("Опасный Малый")? Wrap to
  //      2 lines at normal size — clean break at the word boundary.
  //   3. Doesn't fit and has NO space ("Непридумал", "Интеграл") — a
  //      single word wrapped mid-word just produces an orphaned letter
  //      or two on the second line, which reads worse than a smaller
  //      single line. Skip wrapping entirely for these and shrink the
  //      font (single line) down to a readable floor instead.
  //   4. Still doesn't fit at the floor size (2-line case) or floor width
  //      (1-line case)? Ellipsis is the last-resort safety net, not the
  //      first response to a long name.
  // Cheap (≤10 elements, a few reflow reads each) and only runs right
  // after a DOM swap, not on every poll.
  function fitSeatNames() {
    const names = root.querySelectorAll('.ms-seat-card__name');
    const minPx = 8;
    names.forEach((el) => {
      el.style.fontSize = '';
      el.classList.remove('ms-seat-card__name--wrap');

      if (el.scrollWidth <= el.clientWidth) return; // fits on one line already

      const hasNaturalBreak = /\s/.test(el.textContent || '');
      if (hasNaturalBreak) {
        el.classList.add('ms-seat-card__name--wrap');
        if (el.scrollHeight <= el.clientHeight + 1) return; // fits wrapped over 2 lines
      }

      const overflows = () => (hasNaturalBreak
        ? el.scrollHeight > el.clientHeight + 1
        : el.scrollWidth > el.clientWidth);

      let size = parseFloat(getComputedStyle(el).fontSize);
      let guard = 0;
      while (overflows() && size > minPx && guard < 20) {
        size -= 1;
        el.style.fontSize = size + 'px';
        guard++;
      }
    });
  }

  // ── Ticker: split-flap flip + numeric count-up ──────────────────────────
  function animateTickerValue(factEl) {
    const el = factEl.querySelector('[data-count-to]');
    if (!el) return;
    const target = parseFloat(el.dataset.countTo);
    if (Number.isNaN(target)) return;
    const decimals = (el.dataset.countTo.split('.')[1] || '').length;

    if (REDUCED_MOTION) { el.textContent = target.toFixed(decimals); return; }

    const DUR = 700;
    const startTime = performance.now();
    function tick(now) {
      const t = Math.min(1, (now - startTime) / DUR);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = target.toFixed(decimals);
    }
    requestAnimationFrame(tick);
  }

  function startTicker() {
    if (tickerHandle) clearInterval(tickerHandle);
    const facts = Array.from(root.querySelectorAll('.ticker-fact'));
    if (facts.length === 0) return;
    let idx = Math.max(0, facts.findIndex((f) => f.classList.contains('active')));
    facts.forEach((f, i) => {
      f.classList.toggle('active', i === idx);
      f.classList.remove('is-leaving', 'is-entering');
    });
    animateTickerValue(facts[idx]);
    if (facts.length <= 1) return;
    tickerHandle = setInterval(() => {
      const outgoing = facts[idx];
      idx = (idx + 1) % facts.length;
      const incoming = facts[idx];
      outgoing.classList.remove('active');
      outgoing.classList.add('is-leaving');
      incoming.classList.add('active', 'is-entering');
      animateTickerValue(incoming);
      setTimeout(() => outgoing.classList.remove('is-leaving'), 520);
      setTimeout(() => incoming.classList.remove('is-entering'), 620);
    }, TICKER_MS);
  }

  function triggerReveal(pin) {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot || !fragmentRoot.querySelector('.results-reveal-panel')) return;
    if (revealTimeoutHandle) { clearTimeout(revealTimeoutHandle); revealTimeoutHandle = null; }
    const wasActive = fragmentRoot.classList.contains('reveal-active');
    fragmentRoot.classList.add('reveal-active');
    if (!wasActive) {
      spawnRevealBursts();
      startEmbers();
    }
    if (!pin) {
      revealTimeoutHandle = setTimeout(() => {
        fragmentRoot.classList.remove('reveal-active');
        stopEmbers();
      }, REVEAL_MS);
    }
  }

  function hideReveal() {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot) return;
    if (revealTimeoutHandle) { clearTimeout(revealTimeoutHandle); revealTimeoutHandle = null; }
    fragmentRoot.classList.remove('reveal-active');
    stopEmbers();
  }

  // Applies the admin-controlled ticker/standings-mode/reveal-override
  // state to whatever's currently in the DOM (old or freshly swapped-in —
  // called after any sig-triggered replace, same ordering as the reveal
  // trigger below) via plain class toggles, so CSS transitions animate it.
  function applyCtl(ctl) {
    const ticker = root.querySelector('.overlay-ticker');
    if (ticker) ticker.classList.toggle('is-hidden', !ctl.ticker);

    const seats = root.querySelector('.overlay-seat-strip');
    if (seats) seats.classList.toggle('is-hidden', !ctl.showSeats);

    const top5 = root.querySelector('.overlay-mini-standings');
    if (top5) top5.classList.toggle('is-hidden', ctl.standingsMode !== 'top5');

    const full = root.querySelector('.overlay-full-standings');
    if (full) full.classList.toggle('is-hidden', ctl.standingsMode !== 'full');

    root.querySelectorAll('[data-idle-slot]').forEach((slot) => {
      slot.classList.toggle('is-active', slot.dataset.idleSlot === ctl.idleContent);
    });

    if (ctl.revealOverride === 'on') triggerReveal(true);
    else if (ctl.revealOverride === 'off') hideReveal();
    // 'auto' — leave whatever the lastFinishedId-driven trigger already set.

    if (window.MSBroadcastScenes) window.MSBroadcastScenes.setActive(ctl.scene);
  }

  async function poll() {
    let resp;
    try {
      resp = await fetch(FRAGMENT_URL, { cache: 'no-store' });
    } catch (e) {
      return; // network hiccup — just retry next tick, this runs unattended for hours
    }
    if (!resp.ok) return;

    const html = await resp.text();
    const tpl = document.createElement('template');
    tpl.innerHTML = html.trim();
    const newRoot = tpl.content.firstElementChild;
    if (!newRoot) return;

    const newSig = newRoot.dataset.sig;
    const newLastFinishedId = newRoot.dataset.lastFinishedId || '';
    const newCtl = parseCtl(newRoot.dataset.ctl);

    if (newSig !== currentSig) {
      root.innerHTML = '';
      root.appendChild(newRoot);
      currentSig = newSig;
      startTicker();
      fitSeatNames();
      spawnCardEntranceBursts();
      if (window.MSBroadcastScenes) window.MSBroadcastScenes.init();
    }

    if (newLastFinishedId !== lastFinishedId) {
      lastFinishedId = newLastFinishedId;
      if (newCtl.revealOverride !== 'off') triggerReveal(newCtl.revealOverride === 'on');
    }

    if (!currentCtl || currentCtl.ticker !== newCtl.ticker
        || currentCtl.showSeats !== newCtl.showSeats
        || currentCtl.standingsMode !== newCtl.standingsMode
        || currentCtl.revealOverride !== newCtl.revealOverride
        || currentCtl.scene !== newCtl.scene
        || currentCtl.idleContent !== newCtl.idleContent) {
      applyCtl(newCtl);
      currentCtl = newCtl;
    }

    if (window.MSBroadcastScenes && currentTimerStartedAt !== newCtl.timerStartedAt) {
      window.MSBroadcastScenes.setTimer(newCtl.timerDuration, newCtl.timerStartedAt);
      currentTimerStartedAt = newCtl.timerStartedAt;
    }
  }

  startTicker();
  fitSeatNames();
  spawnCardEntranceBursts();
  if (window.MSBroadcastScenes) window.MSBroadcastScenes.init();
  setInterval(poll, POLL_MS);
})();
