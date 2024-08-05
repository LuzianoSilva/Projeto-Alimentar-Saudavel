<?php
$db = new SQLite3("produtos.db");

$produtos = [];
if (!$db) {
    echo "<div>Houve um erro ao conectar-se ao banco de dados.</div>";
} else {
    if (isset($_POST['pesquisa'])) {
        $pesquisa = $_POST['pesquisa'];
        $stmt = $db->prepare("SELECT id, nome, preco FROM produtos WHERE nome LIKE :pesquisa");
        $stmt->bindValue(':pesquisa', '%' . $pesquisa . '%', SQLITE3_TEXT);
        $result = $stmt->execute();
    } else if (isset($_GET['view']) && $_GET['view'] == 'all') {
        $result = $db->query("SELECT id, nome, preco FROM produtos");
    } else {
        $result = $db->query("SELECT id, nome, preco FROM produtos");
    }

    while ($row = $result->fetchArray()) {
        $produtos[] = $row;
    }
}
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Alimentar Saudável</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>Alimentar Saudável</h1>
    <nav>
      <ul>
        <li><a href="index.php?view=all">Home</a></li>
<li><a href="novo_perfiu.php" target="_blank">Cadastre-se</a></li>
        <li><a href="sobre.php" target="_blank">Sobre</a></li>
        <li><a href="contato.php" target="_blank">Contato</a></li>
      </ul>
    </nav>
  </header>
  <main>
    <section id="destaque">
      <h2>Bem-vindo ao Alimentar Saudável!</h2>
      <p>Conecte-se com pequenos e médios produtores orgânicos e encontre alimentos frescos e saudáveis para sua família.</p>
    </section>
    <section id="produtos">
      <h2>Nossos Produtos</h2>
      <form method="post" action="">
        <input type="text" name="pesquisa" placeholder="Pesquisar produtos..." required>
        <br>
        <button type="submit">Pesquisar</button>
      </form>
      <div class="card-produto">
        <?php
if(!empty($produtos)){
foreach ($produtos as $produto){
echo "
            <div class='produto-item'>
              <span>" . htmlspecialchars($produto['nome']) . "</span>
              <span>R$" . number_format($produto['preco'], 2, ',', '.') . "</span>
              <br>
      <form method='post' action='compra.php'>
        <input type='hidden' name='campoProduto' value='" . $produto['nome'] . "'>
<input type='hidden' name='campoPreco' value='" . $produto['preco'] . "'>
        <button type='submit'>Comprar</button>
      </form>
            </div>";
}
}
else {
echo "<p>Nenhum produto encontrado.</p>";
}
?>
      </div>
    </section>
  </main>
  <footer>
    <p>&copy; 2024 Alimentar Saudável</p>
  </footer>
</body>
<script>
alert("Bem-vindo ao Alimentar Saudável!");
</script>
</html>
