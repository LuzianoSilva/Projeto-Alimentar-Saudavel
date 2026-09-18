(async function () {
  'use strict';
  if (!window.Shop) return;
  const formatDate = value => new Intl.DateTimeFormat('pt-BR', {dateStyle:'long', timeStyle:'short'}).format(new Date(`${value.replace(' ', 'T')}Z`));
  const list = document.querySelector('[data-orders]');
  const detail = document.querySelector('[data-order-detail]');
  try {
    if (list) {
      const data = await Shop.apiJSON('/api/conta/pedidos');
      list.innerHTML = data.pedidos.length ? `<ol class="orders-list">${data.pedidos.map(order => `<li class="order-card"><h2>Pedido ${order.id}</h2><p>${formatDate(order.criado_em)} — ${Shop.cents(order.total_centavos)} — ${Shop.escapeHTML(order.status.replaceAll('_', ' '))}</p><a href="pedido.html?id=${order.id}">Ver detalhes do pedido ${order.id}</a></li>`).join('')}</ol>` : '<p>Você ainda não possui pedidos associados à sua conta.</p>';
      list.removeAttribute('aria-busy');
    }
    if (detail) {
      const id = Number(new URLSearchParams(location.search).get('id'));
      if (!Number.isInteger(id) || id < 1) throw Object.assign(new Error('Pedido não encontrado.'), {status:404});
      const data = await Shop.apiJSON(`/api/pedidos/${id}`);
      const order = data.pedido;
      detail.innerHTML = `<h2>Pedido ${order.id}</h2><p>${formatDate(order.criado_em)}</p><p>Status: <strong>${Shop.escapeHTML(order.status.replaceAll('_', ' '))}</strong></p><h3>Itens</h3><ul>${order.itens.map(item => `<li><strong>${item.quantidade} × ${Shop.escapeHTML(item.nome_produto)}</strong><br>Preço unitário: ${Shop.cents(item.preco_unitario_centavos)}<br>Subtotal: ${Shop.cents(item.subtotal_centavos)}</li>`).join('')}</ul><p class="total">Total: ${Shop.cents(order.total_centavos)}</p><a class="btn btn-secondary" href="pedidos.html">Voltar aos meus pedidos</a>`;
      detail.removeAttribute('aria-busy');
      detail.querySelector('h2').setAttribute('tabindex', '-1');
      detail.querySelector('h2').focus();
    }
  } catch (error) {
    if (error.status === 401) { location.href = 'login.html'; return; }
    const target = list || detail;
    target.innerHTML = `<p class="status error">${Shop.escapeHTML(error.message)}</p>`;
    target.removeAttribute('aria-busy');
  }
})();
