def test_catalog_is_paginated(client):
    response = client.get("/api/produtos?page=1&limit=2")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data["produtos"]) == 2
    assert data["paginacao"] == {"pagina": 1, "por_pagina": 2, "total_resultados": 3, "total_paginas": 2}


def test_catalog_rejects_invalid_parameters(client):
    assert client.get("/api/produtos?page=0").status_code == 400
    assert client.get("/api/produtos?limit=999999999").status_code == 400
    assert client.get("/api/produtos?page=texto").status_code == 400


def test_search_and_category_work_together(client):
    response = client.get("/api/produtos?q=ma&categoria=Fruta")
    data = response.get_json()
    assert data["paginacao"]["total_resultados"] == 1
    assert data["produtos"][0]["nome"] == "Maçã"


def test_no_results(client):
    data = client.get("/api/produtos?q=inexistente").get_json()
    assert data["produtos"] == []
    assert data["paginacao"]["total_resultados"] == 0


def test_selected_products_accepts_arbitrary_ids(client, db):
    cursor = db.execute("INSERT INTO produtos (nome, categoria, preco_centavos) VALUES ('Produto 100', 'Teste', 999)")
    db.commit()
    product_id = cursor.lastrowid
    response = client.get(f"/api/produtos/selecionados?ids={product_id}")
    assert response.status_code == 200
    assert response.get_json()["produtos"][0]["id"] == product_id


def test_catalog_with_500_temporary_products(client, db):
    db.executemany(
        "INSERT INTO produtos (nome, categoria, preco_centavos) VALUES (?, 'Teste', 100)",
        [(f"Produto temporário {number:03d}",) for number in range(1, 501)],
    )
    db.commit()
    first = client.get("/api/produtos?page=1&limit=20&categoria=Teste").get_json()
    page_25 = client.get("/api/produtos?page=25&limit=20&categoria=Teste").get_json()
    search = client.get("/api/produtos?q=temporário 500").get_json()
    assert first["paginacao"]["total_resultados"] == 500
    assert first["paginacao"]["total_paginas"] == 25
    assert len(first["produtos"]) == 20
    assert len(page_25["produtos"]) == 20
    assert search["produtos"][0]["nome"] == "Produto temporário 500"
