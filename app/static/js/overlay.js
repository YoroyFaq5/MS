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
// ticker's numeric count-up.
(function () {
  const root = document.getElementById('overlay-root');
  if (!root) return;

  const FRAGMENT_URL = root.dataset.fragmentUrl;
  const POLL_MS   = parseInt(root.dataset.pollIntervalMs, 10)   || 5000;
  const REVEAL_MS = parseInt(root.dataset.revealDurationMs, 10) || 25000;
  const TICKER_MS = parseInt(root.dataset.tickerIntervalMs, 10) || 8000;
  // How long the results-reveal banner's staged CLOSE sequence takes
  // (rows dissolve → callouts pop away → header un-wipes → cloth+frame
  // retract → crest → finials → crossbar) — see the .is-hiding rules in
  // overlay.css's SECTION 2. Keep in step with the LAST close there (the
  // crossbar: 1.5s delay + .32s duration = 1.82s), plus a small buffer.
  const REVEAL_CLOSE_MS = 1900;

  const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let currentSig = root.firstElementChild ? root.firstElementChild.dataset.sig : null;
  let lastFinishedId = root.firstElementChild ? root.firstElementChild.dataset.lastFinishedId : '';
  let currentCtl = root.firstElementChild ? parseCtl(root.firstElementChild.dataset.ctl) : null;
  let currentTimerStartedAt = currentCtl ? currentCtl.timerStartedAt : null;
  let revealTimeoutHandle = null;
  let revealCloseTimeoutHandle = null;
  let tickerHandle = null;
  let emberHandle = null;

  function parseCtl(str) {
    const parts = {};
    (str || 'tk=1|sh=1|sm=top5|rv=auto|td=900|ts=0|ic=logo').split('|').forEach((pair) => {
      const [key, value] = pair.split('=');
      parts[key] = value;
    });
    return {
      ticker: parts.tk === '1',
      showSeats: parts.sh !== '0', // default to visible if the field is ever missing
      showMarquee: parts.mq !== '0', // bottom stats marquee (Live-Commentators only) — same default-visible convention
      standingsMode: parts.sm || 'top5',
      revealOverride: parts.rv || 'auto',
      // Starting Soon countdown — only present on that page's ctl string
      // (see app/services/broadcast_scene_service.py and
      // broadcast-scenes.js); harmlessly absent/default elsewhere.
      timerDuration: parseFloat(parts.td || '0'),
      timerStartedAt: parseFloat(parts.ts || '0') || null,
      // Which of the (always-in-DOM) idle-hero center slots is active —
      // see app/routes/overlay.py's effective_idle_content.
      idleContent: parts.ic || 'logo',
      // Admin-pinned "show this specific past tour" for the last_game
      // slot (see OverlayControlService.set_pinned_game) — '0' means
      // "auto" (no pin). Only the id, just to detect a change; see
      // poll()'s pinnedGame handling for what actually happens with it.
      pinnedGame: parts.pg || '0',
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
  // card right as totem-resolve (overlay.css) lands — that animation's
  // own delay is `--d + 1.6s` with a .75s duration landing at ~55%
  // (.41s in), so dust spawned ~500ms (its own average duration) before
  // that arrives right on cue.
  function spawnRevealBursts() {
    if (REDUCED_MOTION) return;
    root.querySelectorAll('.reveal-card').forEach((card) => {
      const particlesEl = card.querySelector('.reveal-card__particles');
      if (!particlesEl) return;
      const d = readDelayMs(card);
      setTimeout(() => {
        spawnParticles(particlesEl, { kind: 'converge', count: 5, size: [2, 3.5], dur: [400, 600], distance: [20, 46] });
      }, d + 1510);
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

  // ── Idle-hero info panel: rare red edge energy pulse (Live-Commentators
  // only) — Level 2 of the panel's motion hierarchy, see the "Ambient
  // motion" comment on .overlay-idle-hero__info in overlay.css. A slow
  // CSS @keyframes loop only ever produces a fixed period, which reads as
  // "there's a loop" exactly as fast as this was designed not to — so the
  // irregular interval is scheduled here instead. Re-queries the edge
  // element fresh on every fire (rather than holding a stale reference),
  // so it keeps working across a full fragment DOM swap (data-sig change)
  // without needing its own re-init hook.
  function scheduleInfoPulse() {
    if (REDUCED_MOTION) return;
    const delay = 13000 + Math.random() * 11000; // ~13-24s, deliberately irregular
    setTimeout(() => {
      const edge = root.querySelector('.overlay-idle-hero__info-edge-pulse');
      if (edge && !edge.classList.contains('is-pulsing')) {
        edge.classList.add('is-pulsing');
        edge.addEventListener('animationend', () => edge.classList.remove('is-pulsing'), { once: true });
      }
      scheduleInfoPulse();
    }, delay);
  }

  // ── Idle-hero panel: "THE SHIELD REASSEMBLY" ─────────────────────────
  // The signature transition for switching which content the idle-hero
  // panel shows (logo/standings/last_game/ticker — the caster's button
  // on the OBS dock, see obs-control.js's #dock-idle-content). Never a
  // plain crossfade: old content BREAKS APART (.is-shield-out), the
  // panel's own shield silhouette FLASHES once (.is-scanning/.is-flashing
  // on the two dedicated elements in _live_fragment.html), then the new
  // content REASSEMBLES headline-first (.is-shield-in) — see the
  // "SECTION 7: THE SHIELD REASSEMBLY" block in overlay.css for what each
  // class actually looks like. This function only ever toggles classes on
  // elements that already exist in the DOM — no re-render, no innerHTML
  // churn — so it works equally well right after a full sig-replace or
  // after 100 quiet polls in a row.
  //
  // Durations here are the single source of truth the CSS phase lengths
  // (ovl-shield-shatter-out .26s, ovl-shield-flash-pop .28s, the .is-
  // shield-in delay ladder topping out around 200ms + stagger + .3s) were
  // tuned against — keep them in step if either side changes.
  const SHIELD_TIMING = { out: 300, flash: 170, settle: 560 };
  let shieldBusy = false;
  let shieldPendingTarget = null;
  let activeIdleContent = currentCtl ? currentCtl.idleContent : 'logo';

  function shieldKindFor(target) {
    // Destination decides the "flavor" (brief's variants A-D) — going TO
    // last_game is the sharper "game result" beat, TO standings leans on
    // the table's own list-sweep, TO logo is the quieter "reverse
    // assembly", everything else is the standard scan/break/reassemble.
    if (target === 'last_game') return 'result';
    if (target === 'standings') return 'table';
    if (target === 'logo') return 'idle';
    return 'standard';
  }

  function snapIdleContent(target) {
    root.querySelectorAll('[data-idle-slot]').forEach((slot) => {
      slot.classList.toggle('is-active', slot.dataset.idleSlot === target);
    });
    activeIdleContent = target;
  }

  function transitionIdleContent(target) {
    if (target === activeIdleContent) return;
    if (REDUCED_MOTION) { snapIdleContent(target); return; }
    if (shieldBusy) { shieldPendingTarget = target; return; } // latest click wins, no backlog
    runShieldTransition(target);
  }

  function runShieldTransition(target) {
    const panel = root.querySelector('.overlay-idle-hero__info');
    const oldSlot = root.querySelector('.overlay-idle-hero__slot.is-active');
    const newSlot = root.querySelector('[data-idle-slot="' + target + '"]');
    if (!panel || !newSlot) { snapIdleContent(target); return; } // defensive — should never happen, all 4 slots are always in the DOM

    shieldBusy = true;
    const kind = shieldKindFor(target);
    const scan = panel.querySelector('.overlay-idle-hero__shield-scan');
    const flash = panel.querySelector('.overlay-idle-hero__shield-flash');

    // Phase 1 — SCAN + BREAK APART.
    panel.dataset.shieldKind = kind;
    panel.classList.add('is-shield-transition');
    if (oldSlot) oldSlot.classList.add('is-shield-out');
    if (scan) {
      scan.classList.remove('is-scanning');
      void scan.offsetWidth; // force reflow so a re-add mid-cycle still restarts the animation
      scan.classList.add('is-scanning');
    }

    // Phase 2 — SHIELD FLASH. Old content is fully gone by now; briefly
    // nothing but the panel's own silhouette flashing.
    setTimeout(() => {
      if (oldSlot) oldSlot.classList.remove('is-active', 'is-shield-out');
      if (flash) {
        flash.classList.remove('is-flashing');
        void flash.offsetWidth;
        flash.classList.add('is-flashing');
      }
    }, SHIELD_TIMING.out);

    // Phase 3 — REASSEMBLY. New slot mounts active with the punchier
    // .is-shield-in entrance. Re-add via remove+reflow+add (same trick as
    // the scan/flash elements above) since this slot may still be
    // carrying .is-shield-in from an EARLIER visit (see the cleanup
    // comment below for why that class is never removed) — without the
    // forced reflow, re-adding an already-present class is a no-op and
    // the piece-in animation simply wouldn't play at all.
    setTimeout(() => {
      if (flash) flash.classList.remove('is-flashing');
      newSlot.classList.add('is-active');
      newSlot.classList.remove('is-shield-in');
      void newSlot.offsetWidth;
      newSlot.classList.add('is-shield-in');
      activeIdleContent = target;
    }, SHIELD_TIMING.out + SHIELD_TIMING.flash);

    // Cleanup — hand back to the panel's idle/ambient rules, then either
    // settle or immediately chase whatever target arrived while this was
    // running. Deliberately does NOT remove .is-shield-in: that class and
    // the plain LEVEL-3 .is-active-only rules (overlay.css) both provide
    // an `animation` for the same elements (headline/value/rows/etc) under
    // different keyframe names — the moment .is-shield-in stops matching,
    // the cascade falls back to the .is-active-only rule, which counts as
    // a BRAND NEW animation (different animation-name) and restarts it
    // from its 0% keyframe. That's what "the content appears, then blinks
    // again like it's refreshing" was: the punchy entrance finishing,
    // immediately followed by every piece silently re-playing the plain
    // page-load fade-in-up from scratch. Leaving .is-shield-in on
    // permanently once a slot has been through a shield transition avoids
    // that fallback entirely — .is-shield-in's own rules keep winning
    // (same specificity, later in the stylesheet) for as long as the
    // class stays put, so there's nothing left to fall back to.
    setTimeout(() => {
      panel.classList.remove('is-shield-transition');
      delete panel.dataset.shieldKind;
      shieldBusy = false;
      const next = shieldPendingTarget;
      shieldPendingTarget = null;
      if (next && next !== activeIdleContent) runShieldTransition(next);
    }, SHIELD_TIMING.out + SHIELD_TIMING.flash + SHIELD_TIMING.settle);
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

  // ── Standings auto-scroll ────────────────────────────────────────────────
  // The full-standings panels (.overlay-full-standings on Live-Game,
  // the idle-hero "standings" slot's .ovl-info-list on Live-Commentators)
  // are fixed-height, non-interactive broadcast surfaces — nobody watching
  // a stream can scroll them, so a roster that doesn't fit used to just
  // silently truncate past the fold. Slowly ping-pongs scrollTop between
  // top and bottom instead so every row eventually shows. Re-run after
  // every full DOM replace (new elements each time — any earlier loop
  // notices its element is no longer in the document and stops itself, no
  // explicit teardown needed) and left inert under prefers-reduced-motion.
  const AUTOSCROLL_PX_PER_SEC = 26;
  const AUTOSCROLL_HOLD_MS = 2200;

  function easeInOutSine(t) { return 0.5 - 0.5 * Math.cos(Math.PI * t); }

  function autoScrollPanel(el) {
    const distance = el.scrollHeight - el.clientHeight;
    if (distance <= 4) { el.scrollTop = 0; return; } // fits already, nothing to do
    if (REDUCED_MOTION) { el.scrollTop = 0; return; }

    const travelMs = Math.max(3000, (distance / AUTOSCROLL_PX_PER_SEC) * 1000);
    let phase = 'hold-top';
    let phaseStart = performance.now();

    function step(now) {
      if (!el.isConnected) return; // replaced by a newer poll — let this loop die
      const elapsed = now - phaseStart;
      if (phase === 'hold-top') {
        if (elapsed >= AUTOSCROLL_HOLD_MS) { phase = 'down'; phaseStart = now; }
      } else if (phase === 'down') {
        const t = Math.min(1, elapsed / travelMs);
        el.scrollTop = easeInOutSine(t) * distance;
        if (t >= 1) { phase = 'hold-bottom'; phaseStart = now; }
      } else if (phase === 'hold-bottom') {
        if (elapsed >= AUTOSCROLL_HOLD_MS) { phase = 'up'; phaseStart = now; }
      } else { // 'up'
        const t = Math.min(1, elapsed / travelMs);
        el.scrollTop = (1 - easeInOutSine(t)) * distance;
        if (t >= 1) { phase = 'hold-top'; phaseStart = now; }
      }
      requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function autoScrollStandings() {
    root.querySelectorAll('.overlay-full-standings, [data-idle-slot="standings"] .ovl-info-list')
      .forEach(autoScrollPanel);
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
      // Match the CSS: is-leaving's own signal+collapse finishes at .07s+.18s
      // = 250ms, is-entering's longest child (metric, .16s delay + .2s
      // duration = 360ms) — both with a small buffer so the class isn't
      // pulled out from under a still-running animation. See overlay.css's
      // "ИНТЕРЕСНЫЕ ФАКТЫ" section for the full timing breakdown.
      setTimeout(() => outgoing.classList.remove('is-leaving'), 300);
      setTimeout(() => incoming.classList.remove('is-entering'), 420);
    }, TICKER_MS);
  }

  // Staged CLOSE — mirrors THE STANDARD's entrance backwards (rows →
  // callouts → header → cloth+frame → crest → finials → crossbar) via
  // real @keyframes on .is-hiding (see overlay.css SECTION 2's CLOSE
  // comments for why a plain `transition` falling back from the entrance
  // `animation` doesn't work: a CSS transition only fires when an
  // element's own SPECIFIED value changes, and these elements' specified
  // opacity/transform/clip-path never did — only what the entrance
  // animation was computing on top of them did). `.reveal-active` comes
  // off immediately (so nothing re-triggers the entrance mid-close) and
  // `.is-hiding` rides along for exactly as long as that reverse sequence
  // takes, then both are cleared for a clean slate before the next reveal.
  function closeReveal(fragmentRoot) {
    if (revealCloseTimeoutHandle) { clearTimeout(revealCloseTimeoutHandle); revealCloseTimeoutHandle = null; }
    fragmentRoot.classList.remove('reveal-active');
    fragmentRoot.classList.add('is-hiding');
    stopEmbers();
    revealCloseTimeoutHandle = setTimeout(() => {
      fragmentRoot.classList.remove('is-hiding');
      revealCloseTimeoutHandle = null;
    }, REVEAL_CLOSE_MS);
  }

  function triggerReveal(pin) {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot || !fragmentRoot.querySelector('.results-reveal-panel')) return;
    if (revealTimeoutHandle) { clearTimeout(revealTimeoutHandle); revealTimeoutHandle = null; }
    if (revealCloseTimeoutHandle) { clearTimeout(revealCloseTimeoutHandle); revealCloseTimeoutHandle = null; }
    fragmentRoot.classList.remove('is-hiding'); // cancel any close still mid-flight — re-opening wins
    const wasActive = fragmentRoot.classList.contains('reveal-active');
    fragmentRoot.classList.add('reveal-active');
    if (!wasActive) {
      spawnRevealBursts();
      startEmbers();
    }
    if (!pin) {
      revealTimeoutHandle = setTimeout(() => closeReveal(fragmentRoot), REVEAL_MS);
    }
  }

  function hideReveal() {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot) return;
    if (revealTimeoutHandle) { clearTimeout(revealTimeoutHandle); revealTimeoutHandle = null; }
    // Nothing open (already fully closed, or a previous close is already
    // mid-flight) — closeReveal() already removed 'reveal-active' as its
    // first step, so this guard also stops a repeat call (e.g. the next
    // poll while revealOverride stays 'off') from restarting the close
    // timer before the current one ever finishes.
    if (!fragmentRoot.classList.contains('reveal-active')) return;
    closeReveal(fragmentRoot);
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

    const marquee = root.querySelector('.overlay-marquee');
    if (marquee) marquee.classList.toggle('is-hidden', !ctl.showMarquee);

    const top5 = root.querySelector('.overlay-mini-standings');
    if (top5) top5.classList.toggle('is-hidden', ctl.standingsMode !== 'top5');

    const full = root.querySelector('.overlay-full-standings');
    if (full) full.classList.toggle('is-hidden', ctl.standingsMode !== 'full');

    transitionIdleContent(ctl.idleContent);

    if (ctl.revealOverride === 'on') triggerReveal(true);
    else if (ctl.revealOverride === 'off') hideReveal();
    // 'auto' — leave whatever the lastFinishedId-driven trigger already set.
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
      // Fresh DOM — the server already rendered the correct slot as
      // .is-active (see effective_idle_content in overlay.py), and any
      // shield transition mid-flight against the OLD elements is now
      // moot (they're gone). Just resync the tracking state to match.
      activeIdleContent = newCtl.idleContent;
      shieldBusy = false;
      shieldPendingTarget = null;
      startTicker();
      fitSeatNames();
      spawnCardEntranceBursts();
      autoScrollStandings();
      if (window.MSBroadcastScenes) window.MSBroadcastScenes.init();
      if (window.MSOverlayMarquee) window.MSOverlayMarquee.init();
      if (window.MSOverlayChat) window.MSOverlayChat.init();
    } else if (currentCtl && currentCtl.pinnedGame !== newCtl.pinnedGame) {
      // Admin pinned/unpinned a specific past tour (see
      // OverlayControlService.set_pinned_game) — the last_game slot's
      // actual CONTENT changed (names/roles/scores), not just which slot
      // is visible, so applyCtl's class toggles below can't handle it.
      // Splice in fresh innerHTML for just that one slot from the
      // fragment HTML this poll already fetched (newRoot), instead of
      // replacing the whole page the way a genuine cg/lg change does —
      // that used to also replay the camera frame/broadcast bar/seat
      // strip/ambient-motion entrances for what should be a small, quiet
      // update inside one panel.
      const freshSlot = newRoot.querySelector('[data-idle-slot="last_game"]');
      const liveSlot = root.querySelector('[data-idle-slot="last_game"]');
      if (freshSlot && liveSlot) liveSlot.innerHTML = freshSlot.innerHTML;
    }

    if (newLastFinishedId !== lastFinishedId) {
      lastFinishedId = newLastFinishedId;
      if (newCtl.revealOverride !== 'off') triggerReveal(newCtl.revealOverride === 'on');
    }

    if (!currentCtl || currentCtl.ticker !== newCtl.ticker
        || currentCtl.showSeats !== newCtl.showSeats
        || currentCtl.showMarquee !== newCtl.showMarquee
        || currentCtl.standingsMode !== newCtl.standingsMode
        || currentCtl.revealOverride !== newCtl.revealOverride
        || currentCtl.idleContent !== newCtl.idleContent
        || currentCtl.pinnedGame !== newCtl.pinnedGame) {
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
  autoScrollStandings();
  scheduleInfoPulse();
  if (window.MSBroadcastScenes) window.MSBroadcastScenes.init();
  if (window.MSOverlayMarquee) window.MSOverlayMarquee.init();
  if (window.MSOverlayChat) window.MSOverlayChat.init();
  setInterval(poll, POLL_MS);
})();
