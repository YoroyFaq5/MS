// Twitch chat — idle-hero "chat" slot (Live-Commentators only). v1 is
// deliberately text-only: nickname + message, no emote images, no
// badges, no per-user Twitch color, no moderation (CLEARCHAT/CLEARMSG) —
// see the project chat for why (ship something stable fast, richer
// fidelity is a follow-up, not a v1 requirement).
//
// Connects directly from the browser to Twitch's public chat IRC-over-
// WebSocket gateway, anonymously (a "justinfan" login — no OAuth token
// needed to READ a public channel's chat, the same mechanism most
// third-party chat overlays use). Renders everything itself in the
// panel's own typographic system instead of embedding Twitch's official
// iframe widget, which can't be restyled at all (cross-origin — no CSS
// reaches into it).
window.MSOverlayChat = (function () {
  const CHANNEL = 'mafia_style_online';
  const WS_URL = 'wss://irc-ws.chat.twitch.tv:443';
  const MAX_BUFFER = 40;       // in-memory scrollback, survives a full fragment DOM replace
  const MAX_DOM_MESSAGES = 30; // cap actual rendered nodes — this runs for hours unattended
  const RECONNECT_MIN_MS = 2000;
  const RECONNECT_MAX_MS = 30000;

  let ws = null;
  let connected = false;
  let reconnectDelay = RECONNECT_MIN_MS;
  let reconnectTimer = null;
  const buffer = []; // {name, text}, oldest first

  function logEl() { return document.getElementById('ovl-chat-log'); }
  function statusEl() { return document.getElementById('ovl-chat-status'); }

  // Quiet by default (see the .ovl-chat-status CSS comment) — only shown
  // while connecting/reconnecting, cleared once messages are flowing.
  function setStatus(mode, text) {
    const el = statusEl();
    if (!el) return;
    el.className = 'ovl-chat-status' + (mode ? ' is-' + mode : '') + (text ? ' is-visible' : '');
    el.textContent = text || '';
  }

  function renderMessage(msg, animate) {
    const log = logEl();
    if (!log) return;
    const row = document.createElement('div');
    row.className = 'ovl-chat-msg';
    if (!animate) row.style.animation = 'none'; // re-painting scrollback after a remount — no re-entrance flicker for old messages
    const name = document.createElement('span');
    name.className = 'ovl-chat-msg__name';
    name.textContent = msg.name + ':';
    const text = document.createElement('span');
    text.className = 'ovl-chat-msg__text';
    text.textContent = msg.text; // textContent, never innerHTML — this is untrusted third-party chat text
    row.appendChild(name);
    row.appendChild(text);
    log.appendChild(row);
    while (log.children.length > MAX_DOM_MESSAGES) {
      log.removeChild(log.firstElementChild);
    }
  }

  function pushMessage(name, text) {
    const msg = { name: name, text: text };
    buffer.push(msg);
    if (buffer.length > MAX_BUFFER) buffer.shift();
    renderMessage(msg, true);
  }

  // Minimal IRCv3 line parser — just enough for PING/PRIVMSG with tags,
  // not a general-purpose IRC library (this is the only two commands the
  // v1 renderer needs; CLEARCHAT/CLEARMSG moderation is a known
  // simplification, see the file banner comment).
  function parseIRCLine(raw) {
    let rest = raw;
    let tags = {};
    if (rest.charAt(0) === '@') {
      const sp = rest.indexOf(' ');
      const tagStr = rest.slice(1, sp);
      rest = rest.slice(sp + 1);
      tagStr.split(';').forEach(function (pair) {
        const eq = pair.indexOf('=');
        if (eq === -1) return;
        tags[pair.slice(0, eq)] = pair.slice(eq + 1);
      });
    }
    let prefix = '';
    if (rest.charAt(0) === ':') {
      const sp = rest.indexOf(' ');
      prefix = rest.slice(1, sp);
      rest = rest.slice(sp + 1);
    }
    const cmdEnd = rest.indexOf(' ');
    const command = cmdEnd === -1 ? rest : rest.slice(0, cmdEnd);
    rest = cmdEnd === -1 ? '' : rest.slice(cmdEnd + 1);
    let trailing = null;
    const trailIdx = rest.indexOf(':');
    // A leading ':' anywhere before it appears mid-param would be wrong,
    // but IRC trailing params are always introduced by " :" (or the whole
    // remainder starts with ':') — good enough for PRIVMSG/PING, the only
    // two commands handleLine() actually reads .trailing from.
    if (rest.charAt(0) === ':') {
      trailing = rest.slice(1);
    } else if (trailIdx !== -1) {
      trailing = rest.slice(trailIdx + 1);
    }
    return { tags: tags, prefix: prefix, command: command, trailing: trailing };
  }

  function handleLine(raw) {
    if (!raw) return;
    const msg = parseIRCLine(raw);
    if (msg.command === 'PING') {
      if (ws && ws.readyState === WebSocket.OPEN) ws.send('PONG :tmi.twitch.tv');
      return;
    }
    if (msg.command === 'PRIVMSG') {
      const name = msg.tags['display-name'] || msg.prefix.split('!')[0] || '?';
      pushMessage(name, msg.trailing || '');
      return;
    }
    if (!connected && (msg.command === '366' || msg.command === 'JOIN')) {
      // 366 = end-of-NAMES (channel fully joined) — the standard "we're
      // actually live" signal; JOIN-echo catches it a beat earlier.
      connected = true;
      reconnectDelay = RECONNECT_MIN_MS;
      setStatus(null, '');
    }
  }

  function connect() {
    if (ws) { try { ws.close(); } catch (e) { /* already closing/closed */ } }
    setStatus('connecting', 'Подключение…');
    ws = new WebSocket(WS_URL);

    ws.onopen = function () {
      ws.send('CAP REQ :twitch.tv/tags twitch.tv/commands');
      ws.send('NICK justinfan' + Math.floor(10000 + Math.random() * 89999));
      ws.send('JOIN #' + CHANNEL);
    };
    ws.onmessage = function (event) {
      String(event.data).split('\r\n').forEach(handleLine);
    };
    ws.onclose = scheduleReconnect;
    ws.onerror = function () { try { ws.close(); } catch (e) { /* onclose below still fires */ } };
  }

  function scheduleReconnect() {
    connected = false;
    setStatus('connecting', 'Переподключение…');
    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(function () {
      reconnectDelay = Math.min(reconnectDelay * 1.6, RECONNECT_MAX_MS);
      connect();
    }, reconnectDelay);
  }

  // Called by overlay.js both on initial page load and after every full
  // fragment DOM replace (mirrors window.MSBroadcastScenes.init()). The
  // WebSocket itself is independent of the DOM — a replace just means a
  // fresh #ovl-chat-log/#ovl-chat-status pair exists, so this repaints
  // the in-memory buffer into them instead of reconnecting for no reason
  // (which would drop scrollback AND make the connection flap on every
  // single game that finishes).
  function init() {
    if (!logEl()) return; // Live-Game page, or this tournament never rendered the chat slot
    if (ws) {
      const log = logEl();
      log.innerHTML = '';
      buffer.forEach(function (msg) { renderMessage(msg, false); });
      if (!connected) setStatus('connecting', reconnectTimer ? 'Переподключение…' : 'Подключение…');
      return;
    }
    connect();
  }

  return { init: init };
})();
