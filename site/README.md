# Alimentar Saudável — Flask + SQLite

O site é servido pelo Flask porque catálogo e pedidos utilizam a API e o SQLite. Consulte o `README.md` da raiz para instalação e execução.

## Limites intencionais

- O catálogo é carregado dinamicamente do backend.
- O carrinho salva somente IDs e quantidades no `localStorage`.
- Pedidos são persistidos no SQLite e podem ser associados à conta autenticada. Visitantes continuam podendo finalizar pedidos. Pagamentos ainda não fazem parte desta etapa.
- Nenhuma credencial ou informação privada é incluída.
