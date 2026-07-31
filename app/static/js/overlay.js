// Stream overlay poller — plain vanilla JS, no dependencies.
// Polls the fragment endpoint every few seconds, only replaces the DOM
// when the server-provided data-sig actually changed (so CSS animations
// already in progress aren't interrupted on a no-op poll), and separately
// triggers the last-game results reveal for a limited time whenever
// data-last-finished-id changes.
(function () {
  const root = document.getElementById('overlay-root');
  if (!root) return;

  const FRAGMENT_URL = root.dataset.fragmentUrl;
  const POLL_MS   = parseInt(root.dataset.pollIntervalMs, 10)   || 5000;
  const REVEAL_MS = parseInt(root.dataset.revealDurationMs, 10) || 25000;
  const TICKER_MS = parseInt(root.dataset.tickerIntervalMs, 10) || 8000;

  let currentSig = root.firstElementChild ? root.firstElementChild.dataset.sig : null;
  let lastFinishedId = root.firstElementChild ? root.firstElementChild.dataset.lastFinishedId : '';
  let revealTimeoutHandle = null;
  let tickerHandle = null;

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

  function triggerReveal() {
    const fragmentRoot = root.querySelector('.overlay-fragment');
    if (!fragmentRoot || !fragmentRoot.querySelector('.results-reveal-panel')) return;
    if (revealTimeoutHandle) clearTimeout(revealTimeoutHandle);
    fragmentRoot.classList.add('reveal-active');
    revealTimeoutHandle = setTimeout(() => fragmentRoot.classList.remove('reveal-active'), REVEAL_MS);
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

    if (newSig !== currentSig) {
      root.innerHTML = '';
      root.appendChild(newRoot);
      currentSig = newSig;
      startTicker();
    }

    if (newLastFinishedId !== lastFinishedId) {
      lastFinishedId = newLastFinishedId;
      triggerReveal();
    }
  }

  startTicker();
  setInterval(poll, POLL_MS);
})();
