<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Criação de Perfil - Alimentar Saudável</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>Alimentar Saudável</h1>
    <nav>
      <ul>
        <li><a href="index.php?view=all">Home</a></li>
        <li><a href="sobre.php" target="_blank">Sobre</a></li>
        <li><a href="contato.php" target="_blank">Contato</a></li>
      </ul>
    </nav>
  </header>
  <main>
    <h2>Criação de Perfil</h2>
    <form id="createProfileForm">
      <label for="name">Nome e sobrenome:</label>
      <input type="text" id="name" name="name" required>

      <label for="phone">Telefone:</label>
      <input type="tel" id="phone" name="phone" pattern="\d{10,11}" placeholder="Ex: 11987654321" required>

      <label for="email">Email:</label>
      <input type="email" id="email" name="email" required>

      <label for="profileType">Tipo de Perfil:</label>
      <select id="profileType" name="profileType" required>
        <option value="" disabled selected>Selecione</option>
        <option value="cliente">Cliente</option>
        <option value="vendedor">Vendedor</option>
      </select>

      <label for="password">Senha:</label>
      <input type="password" id="password" name="password" required>

      <label for="confirmPassword">Confirmação de Senha:</label>
      <input type="password" id="confirmPassword" name="confirmPassword" required>

      <button type="submit">Criar Perfil</button>
      <p id="responseMessage" class="error"></p>
    </form>
  </main>
  <footer>
    <p>&copy; 2024 Alimentar Saudável</p>
  </footer>
  <script>
    document.getElementById('createProfileForm').addEventListener('submit', function(event) {
      event.preventDefault();

      // Clear previous message
      document.getElementById('responseMessage').textContent = '';

      // Get form values
      var name = document.getElementById('name').value.trim();
      var phone = document.getElementById('phone').value.trim();
      var email = document.getElementById('email').value.trim();
      var profileType = document.getElementById('profileType').value;
      var password = document.getElementById('password').value;
      var confirmPassword = document.getElementById('confirmPassword').value;

      // Basic validation
      if (name === '' || phone === '' || email === '' || profileType === '' || password === '' || confirmPassword === '') {
        document.getElementById('responseMessage').textContent = 'Por favor, preencha todos os campos.';
        return;
      }

      if (password !== confirmPassword) {
        document.getElementById('responseMessage').textContent = 'As senhas não coincidem.';
        return;
      }

      // Assuming form submission is successful
      document.getElementById('responseMessage').textContent = 'Perfil criado com sucesso!';
      document.getElementById('createProfileForm').reset();
    });
  </script>
</body>
</html>
