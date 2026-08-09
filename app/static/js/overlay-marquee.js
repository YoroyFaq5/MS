// Bottom stats marquee (Live-Commentators only) — a real horizontally-
// scrolling strip, not the split-flap "Интересные факты" ticker. Content
// is rendered once server-side (see .overlay-marquee__set in
// _live_fragment.html); this module's only job is the two things Jinja
// can't do on its own: clone that content once so the CSS translateX
// loop wraps seamlessly, and set the scroll duration from the measured
// width so a block with more entries doesn't visibly crawl slower/
// faster than a shorter one would at a fixed animation-duration.
//
// Mirrors the window.MSBroadcastScenes pattern already used by
// broadcast-scenes.js — a small global with an idempotent init(), called
// by overlay.js both on initial page load and after every full fragment
// replace (a fresh DOM each time, so there's nothing to double-clone).
window.MSOverlayMarquee = (function () {
  const PX_PER_SECOND = 65; // tunable: constant scroll speed regardless of content length
  const MIN_DURATION_S = 10; // floor so a very short/empty strip never whips past

  function init() {
    const track = document.getElementById('overlay-marquee-track');
    if (!track) return; // not on this page, or nothing to show (see the template's has-data guard)

    const content = document.getElementById('overlay-marquee-content');
    const set = content ? content.querySelector('.overlay-marquee__set') : null;
    if (!content || !set) return;

    if (!content.dataset.marqueeReady) {
      const clone = set.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      content.appendChild(clone);
      content.dataset.marqueeReady = '1';
    }

    // One .set's width == half of .content's total now that it holds two —
    // that's the actual distance translateX(-50%) covers per lap.
    const lapWidth = content.scrollWidth / 2;
    const duration = Math.max(MIN_DURATION_S, lapWidth / PX_PER_SECOND);
    content.style.animationDuration = duration + 's';
  }

  return { init };
})();
