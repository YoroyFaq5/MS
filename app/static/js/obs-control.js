// OBS Custom Browser Dock — compact remote for the overlay control state.
// Talks to /overlay/<id>/obs-control/* JSON endpoints ONLY — those are new
// routes added specifically for this page (see app/routes/overlay.py); the
// classic /overlay/<id>/control/* form endpoints (used by the existing
// full admin page, including anyone's current OBS Custom Dock pointed at
// it) are never called from here and are untouched by this file existing.
// Every action below just calls the same OverlayControlService/
// BroadcastSceneService/ActiveBroadcastService methods the old page uses —
// this is a second INTERFACE, not a second state system.
(function () {
  const root = document.getElementById('dock-root');
  if (!root) return;

  const tournamentId = root.dataset.tournamentId;
  const STATE_URL = root.dataset.stateUrl;
  const base = `/overlay/${tournamentId}/obs-control`;
  const POLL_MS = 5000;

  const statusEl = document.getElementById('dock-status');
  const tourEl = document.getElementById('dock-tour');
  const activeSection = document.getElementById('dock-active-section');
  const idleButtons = Array.from(document.querySelectorAll('#dock-idle-content [data-idle]'));
  const seatsBtn = document.getElementById('dock-seats');
  const tickerBtn = document.getElementById('dock-ticker');
  const standingsButtons = Array.from(document.querySelectorAll('#dock-standings-mode [data-mode]'));
  const revealButtons = Array.from(document.querySelectorAll('#dock-reveal [data-reveal]'));
  const scopeButtons = Array.from(document.querySelectorAll('#dock-scope [data-scope]'));
  const timerMinutesInput = document.getElementById('dock-timer-minutes');
  const timerStartBtn = document.getElementById('dock-timer-start');
  const timerStateEl = document.getElementById('dock-timer-state');
  const hideAllBtn = document.getElementById('dock-hide-all');
  const resetBtn = document.getElementById('dock-reset');

  let latestState = null;
  let consecutiveFailures = 0;
  let inFlight = false;

  function setStatus(mode) {
    // mode: 'connecting' | 'connected' | 'disconnected'
    statusEl.className = `dock-status is-${mode}`;
  }

  function paint(state) {
    latestState = state;
    setStatus('connected');
    consecutiveFailures = 0;

    if (state.has_current_game) {
      tourEl.hidden = false;
      tourEl.textContent = `Тур №${state.current_game_number}` + (state.current_round ? ` · Раунд ${String(state.current_round).padStart(2, '0')}` : '');
    } else if (state.has_last_game) {
      tourEl.hidden = false;
      tourEl.textContent = `Последний: Тур №${state.last_game_number}`;
    } else {
      tourEl.hidden = true;
    }

    activeSection.innerHTML = '';
    if (state.is_active_broadcast) {
      const b = document.createElement('div');
      b.className = 'dock-active-banner dock-active-banner--ok';
      b.innerHTML = '<span>✓ Активен для /overlay/current/*</span>';
      activeSection.appendChild(b);
    } else {
      const b = document.createElement('div');
      b.className = 'dock-active-banner dock-active-banner--warn';
      b.innerHTML = '<span>⚠ Не активен в OBS</span>';
      const btn = document.createElement('button');
      btn.className = 'dock-btn dock-btn--warn';
      btn.style.minHeight = '32px';
      btn.textContent = 'Сделать активным';
      btn.addEventListener('click', () => act('/set-active', {}));
      b.appendChild(btn);
      activeSection.appendChild(b);
    }

    idleButtons.forEach((btn) => btn.classList.toggle('dock-btn--active', btn.dataset.idle === state.idle_content));

    paintToggle(seatsBtn, state.show_seats);
    paintToggle(tickerBtn, state.show_ticker);

    standingsButtons.forEach((btn) => btn.classList.toggle('dock-btn--on', btn.dataset.mode === state.standings_mode));
    revealButtons.forEach((btn) => {
      const val = btn.dataset.reveal || null;
      btn.classList.toggle('dock-btn--on', val === state.reveal_override);
    });
    scopeButtons.forEach((btn) => btn.classList.toggle('dock-btn--on', btn.dataset.scope === state.standings_scope));

    paintTimer(state);
  }

  function paintToggle(btn, isOn) {
    if (!btn) return;
    btn.classList.toggle('dock-btn--on', isOn);
    const pill = btn.querySelector('.dock-toggle-pill');
    if (pill) pill.textContent = isOn ? 'ВИДНО' : 'СКРЫТО';
  }

  function paintTimer(state) {
    if (!timerStateEl) return;
    if (!state.timer_started_at) {
      timerStateEl.textContent = 'Не запущен';
      return;
    }
    const elapsed = Date.now() / 1000 - state.timer_started_at;
    const remaining = Math.max(0, Math.round(state.timer_duration - elapsed));
    const mm = Math.floor(remaining / 60);
    const ss = remaining % 60;
    timerStateEl.textContent = remaining > 0
      ? `Осталось: ${mm}:${String(ss).padStart(2, '0')}`
      : 'Время вышло';
  }

  async function refresh() {
    try {
      const resp = await fetch(STATE_URL, { cache: 'no-store' });
      if (!resp.ok) throw new Error('bad status');
      const state = await resp.json();
      paint(state);
    } catch (e) {
      consecutiveFailures += 1;
      if (consecutiveFailures >= 2) setStatus('disconnected');
    }
  }

  async function act(path, body) {
    if (inFlight) return; // avoid pile-ups if a click lands mid-request
    inFlight = true;
    try {
      const resp = await fetch(base + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!resp.ok) throw new Error('bad status');
      const state = await resp.json();
      paint(state);
    } catch (e) {
      consecutiveFailures += 1;
      if (consecutiveFailures >= 2) setStatus('disconnected');
    } finally {
      inFlight = false;
    }
  }

  idleButtons.forEach((btn) => btn.addEventListener('click', () => act('/idle-content', { mode: btn.dataset.idle })));
  if (seatsBtn) seatsBtn.addEventListener('click', () => act('/seats', {}));
  if (tickerBtn) tickerBtn.addEventListener('click', () => act('/ticker', {}));
  standingsButtons.forEach((btn) => btn.addEventListener('click', () => act('/standings', { mode: btn.dataset.mode })));
  revealButtons.forEach((btn) => btn.addEventListener('click', () => act('/reveal', { override: btn.dataset.reveal || '' })));
  scopeButtons.forEach((btn) => btn.addEventListener('click', () => act('/standings-scope', { scope: btn.dataset.scope })));

  if (timerStartBtn) {
    timerStartBtn.addEventListener('click', () => {
      const minutes = parseFloat(timerMinutesInput.value) || 15;
      act('/timer', { minutes });
    });
  }

  if (hideAllBtn) hideAllBtn.addEventListener('click', () => act('/hide-all', {}));

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      // Explicit confirm — this undoes manual choices (ticker/seats/
      // standings/reveal/idle-content all snap back to defaults), so a
      // stray click during a live show shouldn't be able to fire it.
      if (window.confirm('Сбросить оверлей в безопасное состояние по умолчанию?\n\nТикер/игроки — видны, таблица — топ-5, реванш — авто, экран ожидания — лого.')) {
        act('/reset', {});
      }
    });
  }

  // ── Hotkeys ──────────────────────────────────────────────────────────
  // Only fire when this dock's own view has focus and the user isn't
  // typing into the timer-minutes field. No hotkey for Reset on purpose
  // (mouse + confirm() only) or Hide All is decided fast without a second
  // dialog — reserving that one keyboard slot for the recoverable action.
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;

    const idleByKey = { '1': 'logo', '2': 'standings', '3': 'last_game', '4': 'ticker' };
    if (idleByKey[e.key]) { act('/idle-content', { mode: idleByKey[e.key] }); return; }
    if (e.key === 's' || e.key === 'S') { act('/seats', {}); return; }
    if (e.key === 't' || e.key === 'T') { act('/ticker', {}); return; }
    if (e.key === 'h' || e.key === 'H') { act('/hide-all', {}); return; }
  });

  refresh();
  setInterval(refresh, POLL_MS);
  setInterval(() => { if (latestState) paintTimer(latestState); }, 1000);
})();
