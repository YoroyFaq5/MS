/**
 * Themed replacement for window.confirm() — see .msc-* styles in main.css.
 * Declarative usage: add data-confirm="message" to a <form> or a
 * <button>/<a> (whichever previously held onsubmit/onclick="return
 * confirm(...)"), optionally with data-confirm-tone="danger" for
 * irreversible actions (defaults to "neutral"), data-confirm-title="...",
 * data-confirm-label="...". Programmatic usage: await window.msConfirm(msg, opts).
 */
(function () {
  const TONES = {
    danger: { icon: "⚠", confirmLabel: "Удалить", title: "Подтвердите удаление", focus: "cancel" },
    neutral: { icon: "✓", confirmLabel: "Подтвердить", title: "Подтвердите действие", focus: "confirm" },
  };

  let backdrop, card, iconEl, titleEl, msgEl, cancelBtn, confirmBtn;
  let resolver = null;

  function ensureDom() {
    if (backdrop) return;
    backdrop = document.createElement("div");
    backdrop.className = "msc-backdrop";
    backdrop.innerHTML =
      '<div class="msc-card" role="alertdialog" aria-modal="true" aria-labelledby="mscTitle" aria-describedby="mscMessage">' +
      '<div class="msc-icon"></div>' +
      '<h3 class="msc-title" id="mscTitle"></h3>' +
      '<p class="msc-message" id="mscMessage"></p>' +
      '<div class="msc-actions">' +
      '<button type="button" class="msc-btn msc-btn-cancel">Отмена</button>' +
      '<button type="button" class="msc-btn msc-btn-confirm">Подтвердить</button>' +
      "</div></div>";
    document.body.appendChild(backdrop);

    card = backdrop.querySelector(".msc-card");
    iconEl = backdrop.querySelector(".msc-icon");
    titleEl = backdrop.querySelector(".msc-title");
    msgEl = backdrop.querySelector(".msc-message");
    cancelBtn = backdrop.querySelector(".msc-btn-cancel");
    confirmBtn = backdrop.querySelector(".msc-btn-confirm");

    cancelBtn.addEventListener("click", () => close(false));
    confirmBtn.addEventListener("click", () => close(true));
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) close(false);
    });
    document.addEventListener("keydown", (e) => {
      if (!backdrop.classList.contains("is-open")) return;
      if (e.key === "Escape") close(false);
    });
  }

  function close(result) {
    backdrop.classList.remove("is-open");
    const r = resolver;
    resolver = null;
    if (r) r(result);
  }

  function msConfirm(message, opts) {
    opts = opts || {};
    ensureDom();
    const tone = opts.tone === "danger" ? "danger" : "neutral";
    const t = TONES[tone];

    card.classList.remove("tone-danger", "tone-neutral");
    card.classList.add("tone-" + tone);
    iconEl.textContent = opts.icon || t.icon;
    titleEl.textContent = opts.title || t.title;
    msgEl.textContent = message;
    confirmBtn.textContent = opts.confirmLabel || t.confirmLabel;
    confirmBtn.className = "msc-btn msc-btn-confirm tone-" + tone;
    cancelBtn.textContent = opts.cancelLabel || "Отмена";

    backdrop.classList.add("is-open");
    (t.focus === "cancel" ? cancelBtn : confirmBtn).focus();

    return new Promise((resolve) => {
      resolver = resolve;
    });
  }

  window.msConfirm = msConfirm;

  function readAttrs(el) {
    return {
      message: el.getAttribute("data-confirm"),
      tone: el.getAttribute("data-confirm-tone") || "neutral",
      title: el.getAttribute("data-confirm-title") || undefined,
      confirmLabel: el.getAttribute("data-confirm-label") || undefined,
    };
  }

  // Forms: <form data-confirm="...">
  document.addEventListener("submit", function (e) {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (!form.hasAttribute("data-confirm")) return;
    if (form.dataset.mscBypass === "1") {
      delete form.dataset.mscBypass;
      return;
    }
    e.preventDefault();
    const opts = readAttrs(form);
    msConfirm(opts.message, opts).then(function (ok) {
      if (!ok) return;
      form.dataset.mscBypass = "1";
      if (form.requestSubmit) form.requestSubmit();
      else form.submit();
    });
  });

  // Buttons/links: <button data-confirm="..."> or <a data-confirm="...">
  document.addEventListener("click", function (e) {
    const el = e.target.closest("button[data-confirm], a[data-confirm]");
    if (!el) return;
    if (el.dataset.mscBypass === "1") {
      delete el.dataset.mscBypass;
      return;
    }
    e.preventDefault();
    const opts = readAttrs(el);
    msConfirm(opts.message, opts).then(function (ok) {
      if (!ok) return;
      el.dataset.mscBypass = "1";
      if (el.tagName === "A") {
        window.location.href = el.href;
      } else if (el.form) {
        if (el.form.requestSubmit) el.form.requestSubmit(el);
        else el.form.submit();
      } else {
        el.click();
      }
    });
  });
})();
