<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
$nomeProduto = $_POST["campoProduto"];
$precoProduto = $_POST["campoPreco"];

?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Compra - Alimentar Saudável</title>
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
    <section id="compra">
      <h2>Detalhes da Compra</h2>
        <form method="post" action="finalizar_compra.php">
<?php
echo "
        <input type='hidden' name='nome' value='" . htmlspecialchars($nomeProduto) . "'>
<input type='hidden' name='preco' value='" . $precoProduto . "'>

<p>Produto: " . htmlspecialchars($nomeProduto) . "</p>
<p>Preço: R$" . number_format($precoProduto, 2, ',', '.') . "</p>
";
}
?>
          <label for="quantidade">Quantidade:</label>
          <input type="number" id="quantidade" name="quantidade" min="1" value="1" required>
          <br>
          <label for="bairro">Bairro:</label>
          <input type="text" id="bairro" name="bairro" required>
          <br>
          <label for="rua">Rua:</label>
          <input type="text" id="rua" name="rua" required>
          <br>
          <label for="numero">Número:</label>
          <input type="text" id="numero" name="numero" required>
          <br>
          <button type="submit">Comprar</button>
        </form>
<a href="index.php">Voltar</a>
    </section>
  </main>
  <footer>
    <p>&copy; 2024 Alimentar Saudável</p>
  </footer>
</body>
</html>
