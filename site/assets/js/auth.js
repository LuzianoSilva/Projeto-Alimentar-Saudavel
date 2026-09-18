(function () {
  'use strict';
  const form = document.querySelector('#register-form, #login-form');
  if (!form || !window.Shop) return;
  const status = form.querySelector('[role="alert"]');

  const clearErrors = () => {
    status.textContent = '';
    status.classList.remove('error');
    form.querySelectorAll('[aria-invalid="true"]').forEach(field => field.removeAttribute('aria-invalid'));
    form.querySelectorAll('.field-error').forEach(node => { node.textContent = ''; });
  };
  const showError = (message, fields = {}) => {
    status.textContent = message;
    status.classList.add('error');
    let first = null;
    Object.entries(fields).forEach(([name, text]) => {
      const field = form.elements[name];
      const node = document.querySelector(`#${name === 'nome' ? 'name' : name === 'senha' ? 'password' : name === 'confirmacao' ? 'confirmation' : name}-error`);
      if (field) { field.setAttribute('aria-invalid', 'true'); first ||= field; }
      if (node) node.textContent = text;
    });
    (first || status).focus();
  };

  document.querySelectorAll('[data-toggle-password]').forEach(button => {
    button.addEventListener('click', () => {
      const field = document.getElementById(button.dataset.togglePassword);
      const showing = field.type === 'text';
      field.type = showing ? 'password' : 'text';
      const action = showing ? 'Mostrar' : 'Ocultar';
      button.textContent = action;
      button.setAttribute('aria-label', `${action} ${field.id === 'confirmation' ? 'confirmação da senha' : 'senha'}`);
      field.focus();
    });
  });

  if (form.id === 'login-form' && new URLSearchParams(location.search).get('cadastro') === 'sucesso') {
    status.textContent = 'Conta criada. Entre com seu e-mail e senha.';
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    clearErrors();
    if (!form.reportValidity()) { showError('Revise os campos indicados.'); return; }
    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    const registering = form.id === 'register-form';
    const payload = registering
      ? {nome: form.elements.nome.value, email: form.elements.email.value, senha: form.elements.senha.value, confirmacao: form.elements.confirmacao.value}
      : {email: form.elements.email.value, senha: form.elements.senha.value};
    try {
      await Shop.apiJSON(registering ? '/api/auth/cadastro' : '/api/auth/login', {method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken':await Shop.getCSRF()}, body:JSON.stringify(payload)});
      location.href = registering ? 'login.html?cadastro=sucesso' : 'conta.html';
    } catch (error) {
      form.querySelectorAll('input[type="password"], input[type="text"][name="senha"], input[name="confirmacao"]').forEach(field => { if (field.name === 'senha' || field.name === 'confirmacao') field.value = ''; });
      showError(error.message, error.data?.campos || {});
      submit.disabled = false;
    }
  });
})();
