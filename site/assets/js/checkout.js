(function () {
  'use strict';
  const list = document.querySelector('[data-cart-items]');
  if (!list || !window.Shop) return;

  const total = document.querySelector('[data-total]');
  const form = document.querySelector('#checkout-form');
  const submit = form.querySelector('button[type="submit"]');
  const saveButton = document.querySelector('[data-save-cart]');
  const clearButton = document.querySelector('[data-clear-cart]');
  const status = document.querySelector('#checkout-status');
  const confirmation = document.querySelector('#order-confirmation');
  let products = new Map();
  let submitting = false;
  let idempotencyKey = null;

  const showCartError = message => {
    list.innerHTML = `<li class="empty-state error">${Shop.escapeHTML(message)}</li>`;
    submit.disabled = true;
    saveButton.disabled = true;
    clearButton.disabled = true;
  };

  const isValidQuantity = input => {
    const value = input.valueAsNumber;
    const valid = input.value !== '' && Number.isInteger(value) && value >= 1 && value <= 99;
    input.setCustomValidity(valid ? '' : 'Informe uma quantidade inteira entre 1 e 99.');
    input.setAttribute('aria-invalid', String(!valid));
    return valid;
  };

  const collectDraft = ({ report = false } = {}) => {
    const draft = {};
    const inputs = [...list.querySelectorAll('[data-quantity]')];
    for (const input of inputs) {
      if (!isValidQuantity(input)) {
        if (report) { input.reportValidity(); input.focus(); }
        return null;
      }
      draft[input.dataset.quantity] = input.valueAsNumber;
    }
    return draft;
  };

  const updateDraftTotals = () => {
    const draft = collectDraft();
    if (!draft) return;
    let totalCents = 0;
    Object.entries(draft).forEach(([id, quantity]) => {
      const product = products.get(id);
      if (!product) return;
      const subtotal = product.preco_centavos * quantity;
      totalCents += subtotal;
      const subtotalNode = list.querySelector(`[data-subtotal="${id}"]`);
      if (subtotalNode) subtotalNode.textContent = Shop.cents(subtotal);
    });
    total.textContent = Shop.cents(totalCents);
    Shop.updateCount(draft);
  };

  const render = () => {
    const cart = Shop.readCart();
    const rows = Object.entries(cart).map(([id, quantity]) => ({product: products.get(id), quantity})).filter(row => row.product);
    list.innerHTML = rows.length ? rows.map(({product, quantity}) => `<li class="cart-item"><div><strong>${Shop.escapeHTML(product.nome)}</strong><p>${Shop.cents(product.preco_centavos)} por unidade</p></div><div class="item-controls"><div class="quantity-field"><label for="quantity-${product.id}">Quantidade de ${Shop.escapeHTML(product.nome)}</label><input class="quantity-input" id="quantity-${product.id}" data-quantity="${product.id}" type="number" min="1" max="99" step="1" inputmode="numeric" value="${quantity}" required></div><button class="icon-btn" type="button" data-remove="${product.id}" aria-label="Remover ${Shop.escapeHTML(product.nome)} do carrinho">×</button></div><p class="item-subtotal">Subtotal: <span data-subtotal="${product.id}">${Shop.cents(product.preco_centavos * quantity)}</span></p></li>`).join('') : '<li class="empty-state">Seu carrinho está vazio. <a href="index.html#catalogo">Escolher produtos</a>.</li>';
    total.textContent = Shop.cents(rows.reduce((sum, row) => sum + row.product.preco_centavos * row.quantity, 0));
    const empty = rows.length === 0;
    submit.disabled = empty || submitting;
    saveButton.disabled = empty;
    clearButton.disabled = empty;
    Shop.updateCount(cart);
  };

  const loadCart = async () => {
    const cart = Shop.readCart();
    const ids = Object.keys(cart);
    if (!ids.length) { products = new Map(); render(); return; }
    try {
      const data = await Shop.apiJSON(`/api/produtos/selecionados?ids=${encodeURIComponent(ids.join(','))}`);
      products = new Map(data.produtos.map(product => [String(product.id), product]));
      const missing = ids.filter(id => !products.has(id));
      if (missing.length) {
        missing.forEach(id => delete cart[id]);
        Shop.saveCart(cart);
        Shop.announce('Produtos indisponíveis foram removidos do carrinho.');
      }
      render();
    } catch (error) { showCartError(error.message); }
  };

  list.addEventListener('input', event => {
    if (!event.target.matches('[data-quantity]')) return;
    isValidQuantity(event.target);
    updateDraftTotals();
  });

  list.addEventListener('click', event => {
    const button = event.target.closest('[data-remove]');
    if (!button) return;
    const id = button.dataset.remove;
    const cart = Shop.readCart();
    const product = products.get(id);
    delete cart[id];
    products.delete(id);
    Shop.saveCart(cart);
    render();
    Shop.announce(`${product.nome} removido do carrinho.`);
  });

  saveButton.addEventListener('click', () => {
    const draft = collectDraft({report: true});
    if (!draft) { Shop.announce('Revise as quantidades antes de salvar.'); return; }
    Shop.saveCart(draft);
    render();
    Shop.announce('Alterações do carrinho salvas.');
  });

  clearButton.addEventListener('click', () => {
    if (!window.confirm('Deseja realmente remover todos os produtos do carrinho?')) {
      Shop.announce('Limpeza do carrinho cancelada.');
      return;
    }
    Shop.saveCart({});
    products.clear();
    render();
    Shop.announce('Carrinho limpo.');
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (submitting || !form.reportValidity()) return;
    const draft = collectDraft({report: true});
    if (!draft || !Object.keys(draft).length) return;
    Shop.saveCart(draft);
    const items = Object.entries(draft).map(([id, quantity]) => ({produto_id: Number(id), quantidade: quantity}));
    submitting = true;
    submit.disabled = true;
    submit.textContent = 'Registrando pedido…';
    status.textContent = '';
    idempotencyKey = idempotencyKey || (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`);
    const payload = {bairro: form.elements.neighborhood.value, rua: form.elements.street.value, numero: form.elements.number.value, itens: items};
    try {
      const data = await Shop.apiJSON('/api/pedidos', {method:'POST', headers:{'Content-Type':'application/json','Idempotency-Key':idempotencyKey,'X-CSRFToken':await Shop.getCSRF()}, body:JSON.stringify(payload)});
      const order = data.pedido;
      Shop.saveCart({});
      products.clear();
      render();
      form.hidden = true;
      confirmation.hidden = false;
      confirmation.innerHTML = `<p class="eyebrow">Pedido registrado</p><h2 tabindex="-1">Pedido número ${order.id}</h2><p>Status: <strong>aguardando pagamento</strong>.</p><h3>Itens confirmados</h3><ul>${order.itens.map(item => `<li>${item.quantidade} × ${Shop.escapeHTML(item.nome_produto)} — ${Shop.cents(item.subtotal_centavos)}</li>`).join('')}</ul><p class="total">Total oficial: ${Shop.cents(order.total_centavos)}</p><p>Entrega: ${Shop.escapeHTML(order.entrega.rua)}, ${Shop.escapeHTML(order.entrega.numero)} — ${Shop.escapeHTML(order.entrega.bairro)}</p><a class="btn" href="index.html#catalogo">Voltar ao catálogo</a>`;
      confirmation.querySelector('h2').focus();
    } catch (error) {
      status.textContent = error.message;
      status.classList.add('error');
      Object.entries(error.data?.campos || {}).forEach(([name, message]) => {
        const field = form.elements[name === 'bairro' ? 'neighborhood' : name === 'rua' ? 'street' : 'number'];
        if (field) {
          field.setAttribute('aria-invalid','true');
          field.setAttribute('aria-describedby',`${field.id}-error`);
          const node = document.querySelector(`#${field.id}-error`);
          if (node) node.textContent = message;
        }
      });
      status.focus();
    } finally {
      submitting = false;
      if (!form.hidden) { submit.disabled = false; submit.textContent = 'Finalizar pedido'; }
    }
  });

  form.addEventListener('input', event => {
    if (!event.target.matches('input')) return;
    event.target.removeAttribute('aria-invalid');
    event.target.removeAttribute('aria-describedby');
    const node = document.querySelector(`#${event.target.id}-error`);
    if (node) node.textContent = '';
  });

  loadCart();
})();
