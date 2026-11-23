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
    const scenario = document.querySelector('.worksheet select');
    const route = new URLSearchParams(location.search).get('scenario');
    document.querySelectorAll('.language a').forEach(link => {
      const target = new URL(link.href);
      target.hash = location.hash;
      if (scenario) {
        if ([...scenario.options].some(option => option.value === route)) {
          target.searchParams.set('scenario', route);
        } else {
          target.searchParams.delete('scenario');
        }
      }
      link.href = target.href;
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
  const prompt = worksheet.querySelector('.scenario-prompt');
  const compose = worksheet.querySelector('#compose');
  const copy = worksheet.querySelector('#copy-message');
  const save = worksheet.querySelector('#save-draft');
  const status = worksheet.querySelector('[role="status"]');

  function updateMessage() {
    const choice = select.selectedOptions[0];
    const subject = encodeURIComponent(choice.dataset.subject);
    const body = encodeURIComponent(draft.value.replace(/\r\n|\r|\n/g, '\r\n'));
    compose.href = compose.dataset.mailto + '?subject=' + subject + '&body=' + body;
    status.textContent = '';
  }
  function showScenario() {
    const route = new URLSearchParams(location.search).get('scenario');
    const known = [...select.options].some(option => option.value === route);
    select.value = known ? route : select.options[0].value;
    prompt.textContent = select.selectedOptions[0].dataset.prompt;
    updateMessage();
    pairLanguageLinks();
  }

  showScenario();
  window.addEventListener('popstate', showScenario);
  select.addEventListener('change', () => {
    const url = new URL(location.href);
    url.searchParams.set('scenario', select.value);
    url.hash = 'worksheet';
    history.replaceState(null, '', url);
    showScenario();
  });
  draft.addEventListener('input', () => {
    draft.setCustomValidity('');
    updateMessage();
  });
  // Read again on activation for text restored by the browser or a password manager.
  compose.addEventListener('click', updateMessage);

  function hasMessage() {
    if (draft.value.trim()) return true;
    draft.setCustomValidity(draft.dataset.required);
    draft.reportValidity();
    return false;
  }
  copy.hidden = false;
  copy.addEventListener('click', async () => {
    if (!hasMessage()) return;
    try {
      await navigator.clipboard.writeText(draft.value);
      status.textContent = status.dataset.copied;
    } catch {
      draft.focus();
      draft.select();
      status.textContent = status.dataset.copyFallback;
    }
  });

  save.hidden = false;
  save.addEventListener('click', () => {
    if (!hasMessage()) return;
    const text = select.selectedOptions[0].dataset.subject + '\n\n' + draft.value.trim() + '\n';
    const file = URL.createObjectURL(new Blob([text], {type: 'text/plain;charset=utf-8'}));
    const link = document.createElement('a');
    link.href = file;
    link.download = 'instman-' + lang + '-' + select.value + '.txt';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(file), 1000);
    status.textContent = status.dataset.saved;
  });
})();
