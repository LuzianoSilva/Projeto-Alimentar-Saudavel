<?php
$total = 0;
$nome = '';
$preco = 0;
$quantidade = 0;
$bairro = '';
$rua = '';
$numero = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['nome'], $_POST['preco'], $_POST['quantidade'], $_POST['bairro'], $_POST['rua'], $_POST['numero'])) {
        $nome = $_POST['nome'];
        $preco = $_POST['preco'];
        $quantidade = $_POST['quantidade'];
        $bairro = $_POST['bairro'];
        $rua = $_POST['rua'];
        $numero = $_POST['numero'];

        $total = $preco * $quantidade;
    } else {
        $error_message = "Dados incompletos para processar o pedido.";
    }
}
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Finalizar Compra - Alimentar Saudável</title>
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
    <section id="finalizar_compra">
      <h2>Compra Finalizada</h2>
      <?php
      if (isset($error_message)) {
          echo "<p>Houve um problema ao processar seu pedido: " . htmlspecialchars($error_message) . "</p>";
      } else {
          echo "
          <p>Seu pedido de <strong>" . htmlspecialchars($nome) . "</strong> foi realizado com sucesso!</p>
          <p>Quantidade: " . htmlspecialchars($quantidade) . "</p>
          <p>Preço unitário: R$ " . number_format($preco, 2, ',', '.') . "</p>
          <p><strong>Valor total: R$ " . number_format($total, 2, ',', '.') . "</strong></p>
          <p>Endereço de entrega: " . htmlspecialchars($rua) . ", " . htmlspecialchars($numero) . ", " . htmlspecialchars($bairro) . "</p>";
      }
      ?>

<a href="index.php">Voltar</a>
    </section>
  </main>
  <footer>
    <p>&copy; 2024 Alimentar Saudável</p>
  </footer>
</body>
</html>
