# Função para inserir dados na tabela de Preço de Compra
def inserir_preco_compra(csv_file):
    conn = sqlite3.connect('smart_pricing.db')
    cursor = conn.cursor()

    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Pular cabeçalho
        for row in reader:
            cursor.execute('''
            INSERT INTO preco_compra (nome_produto, sku, preco_venda_concorrente, frete, impostos_percentual, margem_lucro_percentual, preco_max_compra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row[0], row[1], float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6])))

    conn.commit()
    conn.close()

# Função para inserir dados na tabela de Preço de Venda
def inserir_preco_venda(csv_file):
    conn = sqlite3.connect('smart_pricing.db')
    cursor = conn.cursor()

    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Pular cabeçalho
        for row in reader:
            cursor.execute('''
            INSERT INTO preco_venda (nome_produto, sku, custo_produto, frete, impostos_percentual, margem_lucro_percentual, preco_venda)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row[0], row[1], float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6])))

    conn.commit()
    conn.close()