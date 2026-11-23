(() => {
  const lang = document.documentElement.lang;
  const localeKey = 'instman.language';
  if (document.body.dataset.entry === 'true') {
    let preferred = 'ru';
    try {
      if (localStorage.getItem(localeKey) === 'en') preferred = 'en';
    } catch { /* Explicit language links still work if storage is unavailable. */ }
    const destination = document.querySelector('[hreflang="' + preferred + '"][data-entry]');
    if (destination) window.location.replace(destination.href);
    return;
  }

  try { localStorage.setItem(localeKey, lang); } catch { /* Storage is optional. */ }
  function pairLanguageLinks() {
    document.querySelectorAll('.language a').forEach(link => {
      link.hash = location.hash;
      const route = new URLSearchParams(location.search).get('scenario');
      if (document.querySelector('.worksheet') && ['join', 'idea', 'challenge', 'question'].includes(route)) {
        const target = new URL(link.href);
        target.searchParams.set('scenario', route);
        link.href = target.href;
      }
    });
  }
  pairLanguageLinks();
  window.addEventListener('hashchange', pairLanguageLinks);

  const menu = document.querySelector('.mobile-nav');
  if (menu) {
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
    document.addEventListener('click', event => {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
  }

  const worksheet = document.querySelector('.worksheet');
  if (!worksheet) return;
  const select = worksheet.querySelector('select');
  const draft = worksheet.querySelector('textarea');
  const hint = worksheet.querySelector('.scenario-prompt');
  const save = worksheet.querySelector('button');
  const result = worksheet.querySelector('[role="status"]');
  function showPrompt() {
    hint.textContent = select.selectedOptions[0].dataset.prompt;
    result.textContent = '';
  }
  function readScenario() {
    const scenario = new URLSearchParams(location.search).get('scenario');
    if ([...select.options].some(option => option.value === scenario)) select.value = scenario;
    showPrompt();
  }
  readScenario();
  window.addEventListener('hashchange', readScenario);
  select.addEventListener('change', () => {
    history.replaceState(null, '', '?scenario=' + select.value + '#worksheet');
    pairLanguageLinks();
    showPrompt();
  });
  save.hidden = false;
  save.addEventListener('click', () => {
    if (!draft.value.trim()) {
      draft.setCustomValidity(draft.dataset.required);
      draft.reportValidity();
      return;
    }
    const text = [select.selectedOptions[0].text, hint.textContent, '', draft.value.trim()].join('\n');
    const file = URL.createObjectURL(new Blob([text + '\n'], {type: 'text/plain;charset=utf-8'}));
    const link = document.createElement('a');
    link.href = file;
    link.download = 'instman-' + lang + '-' + select.value + '.txt';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(file), 1000);
    result.textContent = result.dataset.saved;
  });
  draft.addEventListener('input', () => {
    draft.setCustomValidity('');
    result.textContent = '';
  });
})();
