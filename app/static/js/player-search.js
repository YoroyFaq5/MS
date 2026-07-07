// Живой поиск игрока по нику — используется там, где раньше был plain
// <select> по всем игрокам (add participant, редактирование игры). Полная
// версия с быстрым созданием игрока/защитой от дублей остаётся только в
// games/new.html (games/new.html:new_game) — там это отдельный, более
// сложный сценарий (создание игрока прямо из форму).
function initPlayerSearchPicker({ input, hidden, results, onSelect, filterFn }) {
  let debounceTimer;

  function close() {
    results.style.display = 'none';
  }

  async function search(query) {
    if (!query || !query.trim()) {
      close();
      return;
    }
    let items = [];
    try {
      const resp = await fetch('/api/players/search?q=' + encodeURIComponent(query));
      const body = await resp.json();
      items = body.data || [];
    } catch (e) {
      return;
    }
    if (filterFn) items = items.filter(filterFn);

    results.innerHTML = '';
    items.forEach(p => {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = 'list-group-item list-group-item-action py-1';
      el.textContent = p.display_name;
      el.addEventListener('mousedown', (e) => {
        e.preventDefault();
        hidden.value = p.id;
        input.value = p.display_name;
        close();
        if (onSelect) onSelect(p);
      });
      results.appendChild(el);
    });
    results.style.display = items.length ? 'block' : 'none';
  }

  input.addEventListener('input', () => {
    hidden.value = '';
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => search(input.value), 250);
  });
  input.addEventListener('focus', () => {
    if (input.value.trim()) search(input.value);
  });
  input.addEventListener('blur', () => {
    setTimeout(close, 200); // даём клику по результату отработать
  });
}
