# Alimentar Saudável

Aplicação demonstrativa de e-commerce de alimentos saudáveis, desenvolvida para portfólio profissional. O projeto apresenta catálogo dinâmico, carrinho, contas de usuário e persistência de pedidos fictícios. O front-end é servido pelo Flask e os dados são armazenados localmente em SQLite.

## Escopo demonstrativo

Este projeto não é uma loja real, não se destina a produção e não processa clientes, vendas ou pagamentos reais. Nomes, endereços, contas e pedidos usados durante testes ou demonstrações devem ser fictícios. Não há integração com Pix, cartão, boleto ou qualquer serviço financeiro.

O catálogo inicial possui 30 produtos públicos de demonstração. Essa quantidade é apenas o conteúdo inicial do seed e não representa um limite do sistema.

## Evolução tecnológica

A primeira versão do projeto foi criada em PHP como trabalho acadêmico, com páginas e acesso direto a um banco SQLite de produtos. O histórico dessa implementação permanece no repositório para documentar a evolução do projeto e do aprendizado.

A versão atual é uma reconstrução com Python, Flask, SQLite e HTML/CSS/JavaScript. Ela introduz uma arquitetura organizada em backend, API e front-end, catálogo dinâmico, busca, paginação, autenticação, sessões, carrinho, checkout demonstrativo, persistência de pedidos, testes automatizados, práticas básicas de segurança e melhorias de acessibilidade.

## Funcionalidades

- catálogo com paginação, busca e filtro por categoria;
- carrinho com quantidades editáveis;
- cadastro, login, sessão e área da conta;
- checkout demonstrativo com validação no servidor e histórico de pedidos fictícios;
- proteção CSRF, limitação de tentativas de login e cálculo de preços no backend;
- banco e catálogo inicial criados automaticamente.

## Tecnologias

- Python e Flask;
- SQLite;
- HTML semântico, CSS e JavaScript sem framework;
- pytest para testes automatizados.

## Requisitos

- Python 3.11 ou superior;
- `pip`.

## Instalação no Windows

No PowerShell, dentro da pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuração

A aplicação lê as configurações diretamente das variáveis de ambiente. O arquivo `.env.example` documenta os nomes disponíveis, mas não contém segredos reais.

Defina uma chave própria para manter as sessões válidas entre reinicializações:

```powershell
$env:ALIMENTAR_SECRET_KEY = "gere-e-use-uma-chave-longa-e-aleatoria"
```

Configurações opcionais:

- `ALIMENTAR_HTTPS=1`: ativa o atributo `Secure` do cookie quando a aplicação estiver sob HTTPS;
- `ALIMENTAR_RATELIMIT_STORAGE`: define o armazenamento do limitador de requisições. O padrão local é `memory://`.

Nunca versione o `.env` real. Sem `ALIMENTAR_SECRET_KEY`, a aplicação gera uma chave temporária segura a cada inicialização, adequada apenas ao desenvolvimento local.

## Banco de dados e catálogo inicial

Inicialize o banco com:

```powershell
python -m flask --app run init-db
```

O comando cria `instance/alimentar.sqlite3`, aplica tabelas, constraints e índices de `app/schema.sql` e carrega os 30 produtos públicos de demonstração de `app/seed_products.sql` quando o catálogo está vazio. O seed não limita o crescimento: outros produtos podem ser incluídos normalmente no banco.

O diretório `instance/` e todos os arquivos SQLite ficam fora do Git para impedir a publicação de contas, hashes, endereços e pedidos locais.

## Execução

```powershell
python run.py
```

Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000). Os arquivos HTML não devem ser abertos diretamente, pois catálogo, autenticação e pedidos utilizam a API Flask.

## Testes

```powershell
python -m pytest -q
```

Os testes usam bancos temporários e dados claramente fictícios. A suíte também verifica a criação de um banco limpo, o carregamento do catálogo, a busca, a paginação, contas, carrinho e pedidos.

## Acessibilidade

A interface foi desenvolvida considerando navegação por teclado, leitores de tela, semântica HTML, labels associados aos campos e feedback acessível. Os fluxos principais não dependem exclusivamente do mouse. A acessibilidade deve continuar sendo verificada durante a evolução do projeto.

## Estrutura principal

```text
app/                  Aplicação Flask, schema e seed público
site/                 HTML, CSS e JavaScript do front-end
tests/                Testes automatizados
instance/             Banco local ignorado pelo Git
.env.example          Referência de configurações sem segredos
requirements.txt      Dependências Python
run.py                Entrada da aplicação local
```

## Observações de segurança

- senhas são armazenadas somente como hashes gerados pelo Werkzeug;
- preços e totais enviados pelo navegador não são considerados confiáveis;
- operações de escrita usam proteção CSRF;
- o login possui limite de tentativas;
- a chave secreta real e o banco local não devem entrar no repositório.
