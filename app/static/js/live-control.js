// Live-пульт ведущего — отмечает убитых/выгнанных и опционально роли по
// ходу ещё не завершённой игры, ведёт протокол. Тот же "мутация -> отдать
// свежий снапшот -> paint(state)" паттерн, что и obs-control.js, просто
// поверх /overlay/<id>/live-control/* эндпоинтов вместо /obs-control/*.
(function () {
  const root = document.getElementById('lc-root');
  if (!root) return;

  const STATE_URL = root.dataset.stateUrl;
  const ACTION_BASE = root.dataset.actionBase;
  const POLL_MS = 5000;

  const statusEl = document.getElementById('lc-status');
  const tournamentNameEl = document.getElementById('lc-tournament-name');
  const noActiveEl = document.getElementById('lc-noactive');   // /current/* и вообще ничего не активно
  const noGameEl = document.getElementById('lc-nogame');       // турнир есть, но нет текущей игры
  const dashboardEl = document.getElementById('lc-dashboard');
  const seatsEl = document.getElementById('lc-seats');
  const protocolEl = document.getElementById('lc-protocol');
  const phaseStateEl = document.getElementById('lc-phase-state');
  const turnInput = document.getElementById('lc-turn');
  const applyPhaseBtn = document.getElementById('lc-apply-phase');
  const phaseButtons = Array.from(document.querySelectorAll('[data-phase]'));

  const ROLE_LABELS = { civilian: '👤 Мирный', mafia: '🔫 Мафия', don: '🎩 Дон', sheriff: '🔍 Шериф' };

  let consecutiveFailures = 0;
  let inFlight = false;
  let selectedPhase = null; // локальный выбор кнопки Ночь/День, пока не нажали "Применить"

  function setStatus(mode) {
    statusEl.className = `dock-status is-${mode}`;
  }

  function paintSeats(slots) {
    seatsEl.innerHTML = slots.map((s) => {
      const stateClass = s.elimination_type === 'killed' ? 'is-killed'
        : s.elimination_type === 'voted' ? 'is-voted' : '';
      const statusLabel = s.elimination_type === 'killed' ? '☠ Убит'
        : s.elimination_type === 'voted' ? '🗳 Выгнан' : 'Жив';
      const actions = s.is_eliminated
        ? `<button type="button" class="dock-btn" data-action="revive" data-slot="${s.slot_id}">↩ Вернуть</button>`
        : `<button type="button" class="dock-btn dock-btn--danger" data-action="kill" data-slot="${s.slot_id}">☠ Убит</button>
           <button type="button" class="dock-btn dock-btn--warn" data-action="vote" data-slot="${s.slot_id}">🗳 Выгнан</button>`;
      const roleOptions = ['', 'civilian', 'mafia', 'don', 'sheriff'].map((r) => {
        const label = r === '' ? 'Роль…' : ROLE_LABELS[r];
        const selected = (s.live_role || '') === r ? 'selected' : '';
        return `<option value="${r}" ${selected}>${label}</option>`;
      }).join('');
      return `
        <div class="lc-seat ${stateClass}" data-slot-id="${s.slot_id}">
          <div class="lc-seat__top">
            <span class="lc-seat__num">${s.seat_number}</span>
            <span class="lc-seat__name" title="${s.player_name}">${s.player_name}</span>
          </div>
          <div class="lc-seat__status">${statusLabel}</div>
          <div class="lc-seat__actions">${actions}</div>
          <div class="lc-seat__role-row">
            <select data-role-select data-slot="${s.slot_id}">${roleOptions}</select>
            <button type="button" class="dock-btn" data-action="reveal-role" data-slot="${s.slot_id}">Раскрыть</button>
          </div>
        </div>`;
    }).join('');
  }

  function paintProtocol(events) {
    if (!events.length) {
      protocolEl.innerHTML = '<div class="dock-section__hint">Пока пусто.</div>';
      return;
    }
    const TYPE_LABELS = {
      killed: '☠ Убит', voted: '🗳 Выгнан', revived: '↩ Возвращён',
      role_revealed: '🎭 Роль раскрыта', phase_changed: '🔄 Смена хода',
    };
    protocolEl.innerHTML = events.map((e) => {
      const phase = e.phase ? (e.phase === 'night' ? 'Ночь' : 'День') + ' ' + (e.turn_number || '') : '';
      const who = e.player_name ? ` — ${e.player_name}` : '';
      const revokeBtn = e.is_revoked ? ''
        : `<button type="button" class="dock-btn" data-action="revoke-event" data-event="${e.id}">Отменить</button>`;
      return `
        <div class="lc-protocol__row ${e.is_revoked ? 'is-revoked' : ''}">
          <span>${phase}</span>
          <span>${TYPE_LABELS[e.event_type] || e.event_type}${who}</span>
          ${revokeBtn}
        </div>`;
    }).join('');
  }

  function paint(state) {
    setStatus('connected');
    consecutiveFailures = 0;

    if (state.active === false) {
      // Только /current/live-control с ничем не активным — нет вообще
      // никакого турнира, к которому можно было бы привязаться.
      tournamentNameEl.textContent = '—';
      noActiveEl.hidden = false;
      noGameEl.hidden = true;
      dashboardEl.style.display = 'none';
      return;
    }
    noActiveEl.hidden = true;
    tournamentNameEl.textContent = state.tournament_name || tournamentNameEl.textContent;

    if (state.has_game === false) {
      // Турнир резолвлен, но прямо сейчас нет незавершённой игры — нечего
      // отмечать до следующего раунда.
      noGameEl.hidden = false;
      dashboardEl.style.display = 'none';
      return;
    }
    noGameEl.hidden = true;
    dashboardEl.style.display = '';

    paintSeats(state.slots || []);
    paintProtocol(state.events || []);

    selectedPhase = state.live_phase || selectedPhase;
    phaseButtons.forEach((btn) => btn.classList.toggle('dock-btn--on', btn.dataset.phase === selectedPhase));
    if (state.live_turn) turnInput.value = state.live_turn;
    phaseStateEl.textContent = state.live_phase
      ? (state.live_phase === 'night' ? 'Ночь' : 'День') + ' ' + (state.live_turn || 1)
      : '—';
  }

  async function refresh() {
    try {
      const resp = await fetch(STATE_URL, { cache: 'no-store' });
      if (!resp.ok) throw new Error('bad status');
      paint(await resp.json());
    } catch (e) {
      consecutiveFailures += 1;
      if (consecutiveFailures >= 2) setStatus('disconnected');
    }
  }

  async function act(path, body) {
    if (inFlight) return;
    inFlight = true;
    try {
      const resp = await fetch(ACTION_BASE + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {}),
      });
      if (resp.status === 400) {
        // Validation error (e.g. bad role/phase value) — the response
        // body is just {ok:false, message}, not a full state snapshot,
        // so re-fetch the real state instead of painting a partial one.
        const err = await resp.json().catch(() => null);
        if (err && err.message) window.alert(err.message);
        await refresh();
        return;
      }
      if (!resp.ok) throw new Error('bad status');
      const state = await resp.json();
      if (state.ok === false && state.message) window.alert(state.message);
      paint(state);
    } catch (e) {
      consecutiveFailures += 1;
      if (consecutiveFailures >= 2) setStatus('disconnected');
    } finally {
      inFlight = false;
    }
  }

  seatsEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const slotId = btn.dataset.slot;
    if (btn.dataset.action === 'kill') act(`/${slotId}/eliminate`, { kind: 'killed' });
    else if (btn.dataset.action === 'vote') act(`/${slotId}/eliminate`, { kind: 'voted' });
    else if (btn.dataset.action === 'revive') act(`/${slotId}/revive`, {});
    else if (btn.dataset.action === 'reveal-role') {
      const select = seatsEl.querySelector(`select[data-role-select][data-slot="${slotId}"]`);
      const role = select ? select.value : '';
      if (role) act(`/${slotId}/reveal-role`, { role });
    }
  });

  protocolEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action="revoke-event"]');
    if (!btn) return;
    act(`/event/${btn.dataset.event}/revoke`, {});
  });

  phaseButtons.forEach((btn) => btn.addEventListener('click', () => {
    selectedPhase = btn.dataset.phase;
    phaseButtons.forEach((b) => b.classList.toggle('dock-btn--on', b === btn));
  }));

  applyPhaseBtn.addEventListener('click', () => {
    const turn = parseInt(turnInput.value, 10) || 1;
    if (!selectedPhase) return;
    act('/phase', { phase: selectedPhase, turn });
  });

  refresh();
  setInterval(refresh, POLL_MS);
})();
