(function () {
  'use strict';
  const CART_KEY = 'alimentar-saudavel-carrinho-v3';
  const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
  const cents = value => money.format(value / 100);
  const readCart = () => { try { const value = JSON.parse(localStorage.getItem(CART_KEY)); return value && typeof value === 'object' && !Array.isArray(value) ? value : {}; } catch (_) { return {}; } };
  const cleanCart = cart => Object.fromEntries(Object.entries(cart).filter(([id, qty]) => /^\d+$/.test(id) && Number.isInteger(qty) && qty >= 1 && qty <= 99));
  const saveCart = cart => { localStorage.setItem(CART_KEY, JSON.stringify(cleanCart(cart))); updateCount(); };
  const updateCount = (cart = readCart()) => { const count = Object.values(cart).reduce((sum, qty) => sum + qty, 0); document.querySelectorAll('[data-cart-count]').forEach(el => { el.textContent = count; el.setAttribute('aria-label', `${count} ${count === 1 ? 'item' : 'itens'} no carrinho`); }); };
  const announce = message => { const live = document.querySelector('[data-live]'); if (live) live.textContent = message; };
  const escapeHTML = value => String(value).replace(/[&<>'\"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[char]));
  const apiJSON = async (url, options) => { const response = await fetch(url, options); const data = await response.json().catch(() => ({})); if (!response.ok) throw Object.assign(new Error(data.erro || 'Não foi possível concluir a solicitação.'), {data, status: response.status}); return data; };
  let csrfToken = null;
  const getCSRF = async () => { if (!csrfToken) csrfToken = (await apiJSON('/api/auth/csrf')).csrf_token; return csrfToken; };

  const renderAuthNavigation = async () => {
    const current = document.querySelector('[data-auth-nav]') || document.querySelector('a[href="perfil.html"]')?.closest('li');
    if (!current) return;
    try {
      const data = await apiJSON('/api/auth/sessao');
      const markup = data.autenticado
        ? '<li><a href="conta.html">Minha conta</a></li><li><button class="nav-button" type="button" data-logout>Sair</button></li>'
        : '<li><a href="login.html">Entrar</a></li><li><a href="perfil.html">Cadastre-se</a></li>';
      current.insertAdjacentHTML('beforebegin', markup);
      current.remove();
    } catch (_) { /* A navegação principal continua utilizável. */ }
  };

  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => { const open = toggle.getAttribute('aria-expanded') === 'true'; toggle.setAttribute('aria-expanded', String(!open)); nav.hidden = open; });
    addEventListener('resize', () => { if (innerWidth > 800) { nav.hidden = false; toggle.setAttribute('aria-expanded', 'false'); } else if (toggle.getAttribute('aria-expanded') === 'false') nav.hidden = true; });
  }

  const welcomeDialog = document.querySelector('#welcome-dialog');
  if (welcomeDialog) {
    const closeWelcome = welcomeDialog.querySelector('[data-close-welcome]');
    closeWelcome.addEventListener('click', () => welcomeDialog.close());
    if (typeof welcomeDialog.showModal === 'function') welcomeDialog.showModal();
    else welcomeDialog.setAttribute('open', '');
  }

  const grid = document.querySelector('[data-products]');
  if (grid) {
    const search = document.querySelector('#search');
    const category = document.querySelector('#type');
    const resultCount = document.querySelector('#results-count');
    const pagination = document.querySelector('[data-pagination]');
    const state = {page: 1, limit: 12, totalPages: 1, loading: false};
    const loadCategories = async () => { try { const data = await apiJSON('/api/categorias'); category.innerHTML = '<option value="">Todas</option>' + data.categorias.map(item => `<option value="${escapeHTML(item)}">${escapeHTML(item)}</option>`).join(''); } catch (_) { announce('Não foi possível carregar as categorias.'); } };
    const renderPagination = () => {
      if (state.totalPages <= 1) { pagination.innerHTML = ''; return; }
      const start = Math.max(1, state.page - 2), end = Math.min(state.totalPages, state.page + 2), buttons = [];
      buttons.push(`<button type="button" data-page="${state.page - 1}" ${state.page === 1 ? 'disabled' : ''}>Anterior</button>`);
      for (let page = start; page <= end; page++) buttons.push(`<button type="button" data-page="${page}" ${page === state.page ? 'aria-current="page"' : ''} aria-label="Página ${page}">${page}</button>`);
      buttons.push(`<button type="button" data-page="${state.page + 1}" ${state.page === state.totalPages ? 'disabled' : ''}>Próxima</button>`);
      pagination.innerHTML = buttons.join('');
    };
    const loadProducts = async ({focusCount = false} = {}) => {
      if (state.loading) return; state.loading = true; grid.setAttribute('aria-busy', 'true'); grid.innerHTML = '<p class="loading">Carregando produtos…</p>';
      const params = new URLSearchParams({page: state.page, limit: state.limit});
      if (search.value.trim()) params.set('q', search.value.trim()); if (category.value) params.set('categoria', category.value);
      try {
        const data = await apiJSON(`/api/produtos?${params}`), info = data.paginacao; state.page = info.pagina; state.totalPages = info.total_paginas;
        grid.innerHTML = data.produtos.length ? data.produtos.map(product => `<article class="product-card"><p class="product-type">${escapeHTML(product.categoria)}</p><h3>${escapeHTML(product.nome)}</h3><p class="price">${cents(product.preco_centavos)}</p><button class="btn" type="button" data-add="${product.id}" data-name="${escapeHTML(product.nome)}" aria-label="Adicionar ${escapeHTML(product.nome)} ao carrinho">Adicionar ao carrinho</button></article>`).join('') : '<p class="empty-state">Nenhum produto corresponde à sua busca. Tente outro termo ou categoria.</p>';
        resultCount.textContent = `${info.total_resultados} ${info.total_resultados === 1 ? 'produto encontrado' : 'produtos encontrados'}. Página ${info.pagina} de ${info.total_paginas}.`; renderPagination(); if (focusCount) resultCount.focus();
      } catch (error) { grid.innerHTML = `<p class="empty-state error">${escapeHTML(error.message)}</p>`; resultCount.textContent = 'Falha ao carregar o catálogo.'; }
      finally { state.loading = false; grid.removeAttribute('aria-busy'); }
    };
    document.querySelector('#catalog-form').addEventListener('submit', event => { event.preventDefault(); state.page = 1; loadProducts({focusCount: true}); });
    category.addEventListener('change', () => { state.page = 1; loadProducts({focusCount: true}); });
    pagination.addEventListener('click', event => { const button = event.target.closest('[data-page]'); if (!button || button.disabled) return; state.page = Number(button.dataset.page); loadProducts({focusCount: true}); });
    grid.addEventListener('click', event => { const button = event.target.closest('[data-add]'); if (!button) return; const id = button.dataset.add, cart = readCart(); cart[id] = Math.min(99, (cart[id] || 0) + 1); saveCart(cart); announce(`${button.dataset.name} adicionado ao carrinho. Quantidade: ${cart[id]}.`); });
    loadCategories(); loadProducts();
  }
  document.addEventListener('click', async event => {
    const button = event.target.closest('[data-logout]');
    if (!button) return;
    button.disabled = true;
    try {
      await apiJSON('/api/auth/logout', {method:'POST', headers:{'X-CSRFToken':await getCSRF()}});
      location.href = 'index.html';
    } catch (error) { button.disabled = false; announce(error.message); }
  });
  updateCount(); renderAuthNavigation(); document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
  window.Shop = {readCart, saveCart, updateCount, money, cents, announce, escapeHTML, apiJSON, getCSRF};
})();
