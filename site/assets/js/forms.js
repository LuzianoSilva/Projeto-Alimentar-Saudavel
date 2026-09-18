(function () {
  'use strict';
  document.querySelectorAll('[data-form]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const status = form.querySelector('[role="status"]');
      status.classList.remove('error');
      if (!form.checkValidity()) { form.reportValidity(); status.textContent = 'Revise os campos indicados antes de continuar.'; status.classList.add('error'); status.focus(); return; }
      const password = form.querySelector('#password');
      const confirmation = form.querySelector('#confirm-password');
      if (password && confirmation && password.value !== confirmation.value) { confirmation.setCustomValidity('As senhas não coincidem.'); confirmation.reportValidity(); status.textContent = 'As senhas não coincidem.'; status.classList.add('error'); confirmation.focus(); return; }
      if (confirmation) confirmation.setCustomValidity('');
      status.textContent = form.dataset.success;
      status.focus();
    });
  });
})();
