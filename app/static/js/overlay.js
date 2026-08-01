// Stream overlay poller — plain vanilla JS, no dependencies.
// Polls the fragment endpoint every few seconds, only replaces the DOM
// when the server-provided data-sig actually changed (so CSS animations
// already in progress aren't interrupted on a no-op poll), separately
// triggers the last-game results reveal for a limited time whenever
// data-last-finished-id changes, and separately again applies the
// admin-controlled panel visibility (data-ctl) as plain class toggles on
// the already-existing elements — so toggling from the control page
// animates instead of snapping, since it doesn't require a DOM replace.
(function () {
  const root = document.getElementById('overlay-root');
  if (!root) return;

  const FRAGMENT_URL = root.dataset.fragmentUrl;
  const POLL_MS   = parseInt(root.dataset.pollIntervalMs, 10)   || 5000;
  const REVEAL_MS = parseInt(root.dataset.revealDurationMs, 10) || 25000;
  const TICKER_MS = parseInt(root.dataset.tickerIntervalMs, 10) || 8000;

  let currentSig = root.firstElementChild ? root.firstElementChild.dataset.sig : null;
  let lastFinishedId = root.firstElementChild ? root.firstElementChild.dataset.lastFinishedId : '';
  let currentCtl = root.firstElementChild ? parseCtl(root.firstElementChild.dataset.ctl) : null;
  let revealTimeoutHandle = null;
  let tickerHandle = null;

  function parseCtl(str) {
    const parts = {};
    (str || 'tk=1|sh=1|sm=top5|rv=auto').split('|').forEach((pair) => {
      const [key, value] = pair.split('=');
      parts[key] = value;
    });
    return {
      ticker: parts.tk === '1',
      showSeats: parts.sh !== '0', // default to visible if the field is ever missing
      standingsMode: parts.sm || 'top5',
      revealOverride: parts.rv || 'auto',
    };
  }

  // Nameplate fit strategy, in order — rather than jumping straight to
  // an ellipsis or a tiny shrunk font for every long nickname:
  //   1. One line at normal size (the common case — leave it alone).
  //   2. Doesn't fit? Allow wrapping to 2 lines at normal size — handles
  //      names with a natural break ("Опасный Малый") cleanly.
  //   3. Still doesn't fit in 2 lines (a long single word like
  //      "Непридумал", or just a very long name)? Shrink the font down
  //      to a readable floor. Ellipsis only kicks in if it's still too
  //      long at the floor size.
  // Cheap (≤10 elements, a few reflow reads each) and only runs right
  // after a DOM swap, not on every poll.
  function fitSeatNames() {
    const names = root.querySelectorAll('.ms-seat-card__name');
    const minPx = 8;
    names.forEach((el) => {
      el.style.fontSize = '';
      el.classList.remove('ms-seat-card__name--wrap');

      if (el.scrollWidth <= el.clientWidth) return; // fits on one line already

      el.classList.add('ms-seat-card__name--wrap');
      if (el.scrollHeight <= el.clientHeight + 1) return; // fits wrapped over 2 lines

      let size = parseFloat(getComputedStyle(el).fontSize);
      let guard = 0;
      while (el.scrollHeight > el.clientHeight + 1 && size > minPx && guard < 20) {
        size -= 1;
        el.style.fontSize = size + 'px';
        guard++;
      }
    });
  }

  function startTicker() {
    if (tickerHandle) clearInterval(tickerHandle);
    const facts = Array.from(root.querySelectorAll('.ticker-fact'));
    if (facts.length <= 1) return;
    let idx = Math.max(0, facts.findIndex((f) => f.classList.contains('active')));
    tickerHandle = setInterval(() => {
      facts[idx].classList.remove('active');
      idx = (idx + 1) % facts.length;
      facts[idx].classList.add('active');
    }, TICKER_MS);
  }

  function triggerReveal(pin) {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot || !fragmentRoot.querySelector('.results-reveal-panel')) return;
    if (revealTimeoutHandle) { clearTimeout(revealTimeoutHandle); revealTimeoutHandle = null; }
    fragmentRoot.classList.add('reveal-active');
    if (!pin) {
      revealTimeoutHandle = setTimeout(() => fragmentRoot.classList.remove('reveal-active'), REVEAL_MS);
    }
  }

  function hideReveal() {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot) return;
    if (revealTimeoutHandle) { clearTimeout(revealTimeoutHandle); revealTimeoutHandle = null; }
    fragmentRoot.classList.remove('reveal-active');
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
      startTicker();
      fitSeatNames();
    }

    if (newLastFinishedId !== lastFinishedId) {
      lastFinishedId = newLastFinishedId;
      if (newCtl.revealOverride !== 'off') triggerReveal(newCtl.revealOverride === 'on');
    }

    if (!currentCtl || currentCtl.ticker !== newCtl.ticker
        || currentCtl.showSeats !== newCtl.showSeats
        || currentCtl.standingsMode !== newCtl.standingsMode
        || currentCtl.revealOverride !== newCtl.revealOverride) {
      applyCtl(newCtl);
      currentCtl = newCtl;
    }
  }

  startTicker();
  fitSeatNames();
  setInterval(poll, POLL_MS);
})();
