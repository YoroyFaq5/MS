/*
 * Games list — modern filter bar + infinite scroll + Telegram-style
 * "dissolve" animation for cards that leave the filtered result set.
 *
 * Architecture (server stays the single source of truth — nothing here
 * ever filters/trims already-loaded cards client-side):
 *   1. Any filter change re-fetches /games/feed?page=1 for the NEW state.
 *   2. The DOM is reconciled against that result: cards no longer present
 *      dissolve out (Canvas particles, CSS fallback for big batches / for
 *      prefers-reduced-motion), survivors are FLIP-repositioned if their
 *      slot moved, brand-new cards fade in.
 *   3. Infinite scroll (IntersectionObserver on a sentinel element) just
 *      appends further pages of the CURRENT filter state — pure
 *      insertion, no removal, so no dissolve/FLIP needed there.
 */
function initGamesFilters(root) {
  if (!root) return;

  const grid = document.getElementById('matches-grid');
  const sentinel = document.getElementById('games-sentinel');
  const chipsWrap = document.getElementById('games-chips');
  const countValueEl = document.getElementById('games-count-value');
  const countLabelEl = document.getElementById('games-count-label');
  const skeletonTemplate = document.getElementById('games-skeleton-template');
  const searchInput = document.getElementById('games-search-input');
  if (!grid) return;

  const FEED_URL = '/games/feed';
  const EMPTY_STATE_ID = 'games-empty-state';
  const ROLE_LABELS = { civilian: 'Мирный', sheriff: 'Шериф', don: 'Дон', mafia: 'Мафия' };
  const WIN_SIDE_LABELS = { city: 'Победа города', mafia: 'Победа мафии', none: 'Ничья' };
  const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

  const state = {
    q: root.dataset.q || '',
    tournament_id: root.dataset.tournamentId || '',
    tournament_label: root.dataset.tournamentLabel || '',
    month: root.dataset.month || '',
    player_id: root.dataset.playerId || '',
    player_label: root.dataset.playerLabel || '',
    role: root.dataset.role || '',
    win_side: root.dataset.winSide || '',
    ranked_only: root.dataset.rankedOnly === '1',
    hasNext: root.dataset.hasNext === 'true',
    nextPage: root.dataset.nextPage ? parseInt(root.dataset.nextPage, 10) : null,
    isLoading: false,
  };

  // ── small helpers ─────────────────────────────────────────────────────

  function pluralGames(n) {
    const n100 = n % 100, n10 = n % 10;
    if (n10 === 1 && n100 !== 11) return 'игра';
    if (n10 >= 2 && n10 <= 4 && !(n100 >= 12 && n100 <= 14)) return 'игры';
    return 'игр';
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function buildParams(page) {
    const p = new URLSearchParams();
    if (state.q) p.set('q', state.q);
    if (state.tournament_id) p.set('tournament_id', state.tournament_id);
    if (state.month) p.set('month', state.month);
    if (state.player_id) p.set('player_id', state.player_id);
    if (state.role) p.set('role', state.role);
    if (state.win_side) p.set('win_side', state.win_side);
    if (state.ranked_only) p.set('ranked_only', '1');
    p.set('page', String(page || 1));
    return p.toString();
  }

  async function fetchFeed(page) {
    const resp = await fetch(FEED_URL + '?' + buildParams(page));
    if (!resp.ok) throw new Error('feed request failed');
    return resp.json();
  }

  function htmlToNodes(html) {
    const tpl = document.createElement('template');
    tpl.innerHTML = html.trim();
    return Array.from(tpl.content.children);
  }

  function removeEmptyState() {
    const el = document.getElementById(EMPTY_STATE_ID);
    if (el) el.remove();
  }

  function showEmptyStateIfNeeded() {
    if (grid.children.length === 0) {
      const div = document.createElement('div');
      div.className = 'text-center text-muted py-5 games-empty-state';
      div.id = EMPTY_STATE_ID;
      div.innerHTML = '<i class="bi bi-controller fs-1 d-block mb-3 opacity-25"></i>' +
        '<p class="mb-3">Ничего не найдено по этим фильтрам</p>';
      grid.appendChild(div);
    }
  }

  function updateCount(total) {
    if (!countValueEl) return;
    countValueEl.classList.add('is-updating');
    setTimeout(() => {
      countValueEl.textContent = String(total);
      if (countLabelEl) countLabelEl.textContent = pluralGames(total);
      countValueEl.classList.remove('is-updating');
    }, 120);
  }

  function setActiveButton(name, active) {
    const btn = root.querySelector('[data-filter-btn="' + name + '"]');
    if (btn) btn.classList.toggle('has-value', active);
  }

  function syncMoreButtonState() {
    setActiveButton('more', !!(state.win_side || state.ranked_only));
  }

  // ── active-filter chips ──────────────────────────────────────────────

  function renderChips() {
    if (!chipsWrap) return;
    chipsWrap.innerHTML = '';
    const chips = [];
    if (state.tournament_label) chips.push({ key: 'tournament_id', label: state.tournament_label });
    if (state.month) chips.push({ key: 'month', label: state.month });
    if (state.player_label) chips.push({ key: 'player_id', label: state.player_label });
    if (state.role) chips.push({ key: 'role', label: ROLE_LABELS[state.role] || state.role });
    if (state.win_side) chips.push({ key: 'win_side', label: WIN_SIDE_LABELS[state.win_side] || state.win_side });
    if (state.ranked_only) chips.push({ key: 'ranked_only', label: 'Только рейтинговые' });

    chips.forEach(chip => {
      const el = document.createElement('span');
      el.className = 'games-chip';
      const label = document.createElement('span');
      label.textContent = chip.label;
      el.appendChild(label);
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'games-chip__remove';
      btn.setAttribute('aria-label', 'Убрать фильтр');
      btn.textContent = '✕';
      btn.addEventListener('click', () => clearFilter(chip.key));
      el.appendChild(btn);
      chipsWrap.appendChild(el);
    });

    if (chips.length > 0) {
      const reset = document.createElement('button');
      reset.type = 'button';
      reset.className = 'games-chip games-chip--reset';
      reset.textContent = 'Сбросить все';
      reset.addEventListener('click', clearAllFilters);
      chipsWrap.appendChild(reset);
    }
  }

  function clearFilter(key) {
    if (key === 'tournament_id') { state.tournament_id = ''; state.tournament_label = ''; setActiveButton('tournament', false); }
    if (key === 'month') { state.month = ''; setActiveButton('month', false); }
    if (key === 'player_id') { state.player_id = ''; state.player_label = ''; setActiveButton('player', false); }
    if (key === 'role') { state.role = ''; setActiveButton('role', false); }
    if (key === 'win_side') { state.win_side = ''; syncMoreButtonState(); }
    if (key === 'ranked_only') {
      state.ranked_only = false;
      const cb = document.getElementById('games-ranked-only');
      if (cb) cb.checked = false;
      syncMoreButtonState();
    }
    applyFilters();
  }

  function clearAllFilters() {
    state.q = '';
    if (searchInput) searchInput.value = '';
    state.tournament_id = ''; state.tournament_label = '';
    state.month = '';
    state.player_id = ''; state.player_label = '';
    state.role = '';
    state.win_side = '';
    state.ranked_only = false;
    const cb = document.getElementById('games-ranked-only');
    if (cb) cb.checked = false;
    ['tournament', 'month', 'player', 'role'].forEach(k => setActiveButton(k, false));
    syncMoreButtonState();
    applyFilters();
  }

  // ── popovers ─────────────────────────────────────────────────────────

  let openPopoverName = null;

  function closeAllPopovers() {
    root.querySelectorAll('.games-popover.is-open').forEach(p => p.classList.remove('is-open'));
    root.querySelectorAll('.games-filter-btn.is-active').forEach(b => b.classList.remove('is-active'));
    openPopoverName = null;
  }

  function markSelectedItems(popover, currentValue) {
    popover.querySelectorAll('.games-popover__item').forEach(item => {
      item.classList.toggle('is-selected', !!currentValue && item.dataset.value === currentValue);
    });
  }

  function togglePopover(name) {
    const wasOpen = openPopoverName === name;
    closeAllPopovers();
    if (wasOpen) return;
    const popover = root.querySelector('[data-filter-popover="' + name + '"]');
    const btn = root.querySelector('[data-filter-btn="' + name + '"]');
    if (!popover || !btn) return;
    if (name === 'tournament') markSelectedItems(popover, state.tournament_id);
    if (name === 'month') markSelectedItems(popover, state.month);
    if (name === 'role') markSelectedItems(popover, state.role);
    if (name === 'more') markSelectedItems(popover, state.win_side);
    popover.classList.add('is-open');
    btn.classList.add('is-active');
    openPopoverName = name;
    if (name === 'player') {
      const input = document.getElementById('games-player-search');
      if (input) input.focus();
    }
  }

  root.querySelectorAll('[data-filter-btn]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      togglePopover(btn.dataset.filterBtn);
    });
  });

  document.addEventListener('click', (e) => {
    if (!root.contains(e.target)) { closeAllPopovers(); return; }
    if (!e.target.closest('.games-popover') && !e.target.closest('[data-filter-btn]')) {
      closeAllPopovers();
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAllPopovers();
  });

  // Plain-list popovers: tournament / month / role / more
  ['tournament', 'month', 'role', 'more'].forEach(name => {
    const popover = root.querySelector('[data-filter-popover="' + name + '"]');
    if (!popover) return;
    popover.querySelectorAll('.games-popover__item[data-value]').forEach(item => {
      item.addEventListener('click', () => {
        const value = item.dataset.value;
        const label = item.dataset.label;
        if (name === 'tournament') { state.tournament_id = value; state.tournament_label = label; setActiveButton('tournament', true); }
        if (name === 'month') { state.month = value; setActiveButton('month', true); }
        if (name === 'role') { state.role = value; setActiveButton('role', true); }
        if (name === 'more') { state.win_side = value; syncMoreButtonState(); }
        closeAllPopovers();
        applyFilters();
      });
    });
  });

  const rankedCheckbox = document.getElementById('games-ranked-only');
  if (rankedCheckbox) {
    rankedCheckbox.addEventListener('change', () => {
      state.ranked_only = rankedCheckbox.checked;
      syncMoreButtonState();
      applyFilters();
    });
  }

  // Player search popover — same debounced-fetch pattern as player-search.js
  const playerInput = document.getElementById('games-player-search');
  const playerResults = document.getElementById('games-player-results');
  if (playerInput && playerResults) {
    let debounceTimer;
    async function searchPlayers(query) {
      if (!query || !query.trim()) { playerResults.innerHTML = ''; return; }
      let items = [];
      try {
        const resp = await fetch('/api/players/search?q=' + encodeURIComponent(query));
        const body = await resp.json();
        items = body.data || [];
      } catch (e) { return; }
      playerResults.innerHTML = '';
      if (!items.length) {
        playerResults.innerHTML = '<div class="games-popover__empty">Никого не найдено</div>';
        return;
      }
      items.forEach(p => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'games-popover__item';
        btn.textContent = p.display_name;
        btn.addEventListener('mousedown', (e) => {
          e.preventDefault();
          state.player_id = String(p.id);
          state.player_label = p.display_name;
          setActiveButton('player', true);
          closeAllPopovers();
          applyFilters();
        });
        playerResults.appendChild(btn);
      });
    }
    playerInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => searchPlayers(playerInput.value), 250);
    });
  }

  // Free-text search box — debounced, applies as a regular filter
  if (searchInput) {
    let searchDebounce;
    searchInput.addEventListener('input', () => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        state.q = searchInput.value.trim();
        applyFilters();
      }, 300);
    });
  }

  // ── initial state from SSR (bookmarked/shared filtered URL) ─────────

  if (state.tournament_id) setActiveButton('tournament', true);
  if (state.month) setActiveButton('month', true);
  if (state.player_id) setActiveButton('player', true);
  if (state.role) setActiveButton('role', true);
  syncMoreButtonState();
  renderChips();

  // ── core: apply filters (reset to page 1, diff, reconcile DOM) ──────

  async function applyFilters() {
    if (state.isLoading) return;
    state.isLoading = true;
    renderChips();

    const oldCards = Array.from(grid.querySelectorAll('.match-card[data-game-id]'));
    const oldRects = new Map(oldCards.map(el => [el.dataset.gameId, el.getBoundingClientRect()]));

    let data;
    try {
      data = await fetchFeed(1);
    } catch (e) {
      state.isLoading = false;
      return;
    }

    const newIds = data.game_ids.map(String);
    const newIdSet = new Set(newIds);
    const oldIdSet = new Set(oldCards.map(el => el.dataset.gameId));

    const toRemove = oldCards.filter(el => !newIdSet.has(el.dataset.gameId));
    const heavy = toRemove.length > 6;
    toRemove.forEach(el => dissolveCard(el, { heavy }));

    const newNodes = htmlToNodes(data.html);
    const nodeById = new Map(newNodes.map(n => [n.dataset.gameId, n]));
    const survivorEls = new Map(oldCards.map(el => [el.dataset.gameId, el]));
    const survivorIds = newIds.filter(id => oldIdSet.has(id));
    const brandNewIds = newIds.filter(id => !oldIdSet.has(id));

    removeEmptyState();
    const frag = document.createDocumentFragment();
    newIds.forEach(id => {
      const el = survivorEls.get(id) || nodeById.get(id);
      if (el) frag.appendChild(el); // moves survivors out of `grid` into `frag`
    });

    // Detach removal-candidates from grid flow immediately (their own
    // dissolve animation is drawn via an independent fixed-position
    // overlay — see dissolveCard) so the grid doesn't wait on them.
    toRemove.forEach(el => {
      if (el.isConnected && el.parentNode === grid) grid.removeChild(el);
    });

    grid.innerHTML = '';
    grid.appendChild(frag);
    if (newIds.length === 0) showEmptyStateIfNeeded();

    requestAnimationFrame(() => {
      survivorIds.forEach(id => {
        const el = survivorEls.get(id);
        if (!el) return;
        const oldRect = oldRects.get(id);
        if (!oldRect) return;
        const newRect = el.getBoundingClientRect();
        const dx = oldRect.left - newRect.left;
        const dy = oldRect.top - newRect.top;
        if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
        flipAnimate(el, dx, dy);
      });
    });

    state.hasNext = data.has_next;
    state.nextPage = data.next_page;
    updateCount(data.total);
    state.isLoading = false;
  }

  // ── infinite scroll ──────────────────────────────────────────────────

  async function loadMore() {
    if (state.isLoading || !state.hasNext) return;
    state.isLoading = true;

    const skeletons = [];
    if (skeletonTemplate) {
      for (let i = 0; i < 4; i++) {
        const node = skeletonTemplate.content.firstElementChild.cloneNode(true);
        grid.appendChild(node);
        skeletons.push(node);
      }
    }

    let data;
    try {
      data = await fetchFeed(state.nextPage);
    } catch (e) {
      skeletons.forEach(s => s.remove());
      state.isLoading = false;
      return;
    }

    skeletons.forEach(s => s.remove());
    htmlToNodes(data.html).forEach(el => grid.appendChild(el));

    state.hasNext = data.has_next;
    state.nextPage = data.next_page;
    state.isLoading = false;
  }

  if ('IntersectionObserver' in window && sentinel) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) loadMore();
      });
    }, { rootMargin: '500px 0px 500px 0px' });
    observer.observe(sentinel);
  }

  // ── FLIP reposition ──────────────────────────────────────────────────

  function flipAnimate(el, dx, dy) {
    el.style.transition = 'none';
    el.style.transform = 'translate(' + dx + 'px, ' + dy + 'px)';
    requestAnimationFrame(() => {
      el.style.transition = 'transform .32s cubic-bezier(.4,0,.2,1)';
      el.style.transform = '';
      const cleanup = () => { el.style.transition = ''; el.removeEventListener('transitionend', cleanup); };
      el.addEventListener('transitionend', cleanup);
    });
  }

  // ── dissolve: Canvas particles, CSS fallback for big batches / RM ────

  function dissolveCard(el, opts) {
    const heavy = opts && opts.heavy;
    if (reduceMotionQuery.matches || heavy || !supportsCanvasDissolve()) {
      dissolveCardCss(el);
    } else {
      dissolveCardCanvas(el);
    }
  }

  function supportsCanvasDissolve() {
    return typeof document.createElement('canvas').getContext === 'function';
  }

  function dissolveCardCss(el) {
    // Card is already detached from grid flow by the caller — animate it
    // in place (fixed at its last on-screen rect) so removal doesn't snap.
    const rect = el.getBoundingClientRect();
    el.style.position = 'fixed';
    el.style.left = rect.left + 'px';
    el.style.top = rect.top + 'px';
    el.style.width = rect.width + 'px';
    el.style.margin = '0';
    el.style.zIndex = '5';
    document.body.appendChild(el);
    // Reparenting + a style change in the SAME tick can get coalesced by
    // the browser into one paint with no interpolated "from" state, so
    // the transition never visibly runs — a single synchronous
    // `offsetWidth` reflow isn't reliably enough of a commit point for
    // that case. Deferring the class-add two animation frames out is the
    // standard robust pattern for "JS-triggered CSS transition" here.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.classList.add('match-card--dissolving-fallback');
      });
    });
    let done = false;
    const finish = () => { if (done) return; done = true; el.remove(); };
    el.addEventListener('transitionend', finish, { once: true });
    setTimeout(finish, 700); // safety net if transitionend doesn't fire
  }

  function dissolveCardCanvas(el) {
    const rect = el.getBoundingClientRect();
    const canvas = document.createElement('canvas');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.max(1, rect.width * dpr);
    canvas.height = Math.max(1, rect.height * dpr);
    canvas.style.position = 'fixed';
    canvas.style.left = rect.left + 'px';
    canvas.style.top = rect.top + 'px';
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '6';
    document.body.appendChild(canvas);
    el.remove(); // card itself is gone the instant its particle burst appears

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    // Cheap stand-in "snapshot" — a grid of small gold/dark tiles sampled
    // from the card's own palette, not a real pixel capture (an
    // html2canvas-style approach would be too heavy to justify per-card,
    // per the "не создавать тяжёлые DOM-анимации" constraint).
    const cols = 14, rows = 8;
    const cellW = rect.width / cols, cellH = rect.height / rows;
    const particles = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        particles.push({
          x: c * cellW, y: r * cellH,
          w: cellW * 0.82, h: cellH * 0.82,
          vx: (Math.random() - 0.5) * 5.5,
          vy: (Math.random() - 0.9) * 5.5,
          rot: (Math.random() - 0.5) * 0.3,
          vr: (Math.random() - 0.5) * 0.25,
          color: Math.random() > 0.5 ? 'rgba(199,165,82,' : 'rgba(36,36,36,',
        });
      }
    }

    const duration = 520;
    const start = performance.now();

    function frame(now) {
      const t = (now - start) / duration;
      if (t >= 1) { canvas.remove(); return; }
      ctx.clearRect(0, 0, rect.width, rect.height);
      const alpha = 1 - t;
      particles.forEach(p => {
        const px = p.x + p.vx * t * 34;
        const py = p.y + p.vy * t * 34 + 60 * t * t; // gentle gravity
        ctx.save();
        ctx.globalAlpha = Math.max(0, alpha);
        ctx.translate(px + p.w / 2, py + p.h / 2);
        ctx.rotate(p.rot + p.vr * t * 6);
        ctx.fillStyle = p.color + Math.max(0, alpha) + ')';
        ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
        ctx.restore();
      });
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
}
