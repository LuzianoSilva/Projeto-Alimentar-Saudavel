(async function () {
  'use strict';
  const container = document.querySelector('[data-account]');
  if (!container || !window.Shop) return;
  try {
    const data = await Shop.apiJSON('/api/conta');
    const user = data.usuario;
    container.innerHTML = `<h2>${Shop.escapeHTML(user.nome)}</h2><dl><dt>E-mail</dt><dd>${Shop.escapeHTML(user.email)}</dd></dl><div class="account-actions"><a class="btn" href="pedidos.html">Meus pedidos</a><button class="btn btn-secondary" type="button" data-logout>Sair</button></div>`;
    container.removeAttribute('aria-busy');
  } catch (error) {
    if (error.status === 401) { location.href = 'login.html'; return; }
    container.innerHTML = `<p class="status error">${Shop.escapeHTML(error.message)}</p>`;
  }
})();
