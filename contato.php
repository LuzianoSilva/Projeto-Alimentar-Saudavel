<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Contato - Alimentar Saudável</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>Alimentar Saudável</h1>
    <nav>
      <ul>
        <li><a href="index.php?view=all" style="color: #fff; text-decoration: none;">Home</a></li>
        <li><a href="sobre.php" style="color: #fff; text-decoration: none;">Sobre</a></li>
        <li><a href="contato.php" style="color: #fff; text-decoration: none;">Contato</a></li>
      </ul>
    </nav>
  </header>
  <main>
    <h2>Formulário de Contato</h2>
    <form id="contactForm">
      <label for="name">Nome:</label>
      <input type="text" id="name" name="name" required>

      <label for="email">Email:</label>
      <input type="email" id="email" name="email" required>

      <label for="message">Mensagem:</label>
      <textarea id="message" name="message" rows="5" required></textarea>

      <button type="submit">Enviar</button>
    </form>
    <p id="responseMessage" style="color: red; margin-top: 10px;"></p>
  </main>
  <footer>
    <p>&copy; 2024 Alimentar Saudável</p>
  </footer>
  <script>
    document.getElementById('contactForm').addEventListener('submit', function(event) {
      event.preventDefault();

      // Clear previous message
      document.getElementById('responseMessage').textContent = '';

      // Get form values
      var name = document.getElementById('name').value.trim();
      var email = document.getElementById('email').value.trim();
      var message = document.getElementById('message').value.trim();

      // Basic validation
      if (name === '' || email === '' || message === '') {
        document.getElementById('responseMessage').textContent = 'Por favor, preencha todos os campos.';
        return;
      }

      // Assuming form submission is successful
      document.getElementById('responseMessage').textContent = 'Mensagem enviada com sucesso!';
      document.getElementById('contactForm').reset();
    });
  </script>
</body>
</html>
