from flask import Flask, render_template, request, jsonify
import csv
import os
import sqlite3

# Função para criar as tabelas no banco de dados
def criar_banco_e_tabelas():
    conn = sqlite3.connect('smart_pricing.db')
    cursor = conn.cursor()

    # Criar a tabela de Preços de Compra
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS preco_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_produto TEXT NOT NULL,
        sku TEXT NOT NULL,
        preco_venda_concorrente REAL NOT NULL,
        frete REAL NOT NULL,
        impostos_percentual REAL NOT NULL,
        margem_lucro_percentual REAL NOT NULL,
        preco_max_compra REAL NOT NULL
    )
    ''')

    # Criar a tabela de Preços de Venda
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS preco_venda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_produto TEXT NOT NULL,
        sku TEXT NOT NULL,
        custo_produto REAL NOT NULL,
        frete REAL NOT NULL,
        impostos_percentual REAL NOT NULL,
        margem_lucro_percentual REAL NOT NULL,
        preco_venda REAL NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

# Função para calcular o preço de compra
def calcular_preco_compra(preco_venda_concorrente, frete, impostos_percentual, margem_lucro_percentual):
    impostos_valor = (impostos_percentual / 100) * preco_venda_concorrente
    preco_max_compra = (preco_venda_concorrente - frete - impostos_valor) / (1 + (margem_lucro_percentual / 100))
    return round(preco_max_compra, 2)

# Função para calcular o preço de venda com impostos
def calcular_preco_venda_func(custo_produto, frete, margem_lucro_percentual, impostos_percentual):
    margem_lucro = (margem_lucro_percentual / 100) * (custo_produto + frete)
    preco_venda_sem_impostos = custo_produto + frete + margem_lucro
    impostos_valor = (impostos_percentual / 100) * preco_venda_sem_impostos
    preco_venda_final = preco_venda_sem_impostos + impostos_valor
    return round(preco_venda_final, 2)

# Função para salvar os dados em um CSV e garantir o cabeçalho
def salvar_dados_csv(nome_arquivo, dados, colunas):
    arquivo_existe = os.path.isfile(nome_arquivo)

    with open(nome_arquivo, mode='a', newline='') as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        # Escrever o cabeçalho se o arquivo for criado agora
        if not arquivo_existe:
            writer.writerow(colunas)
        writer.writerow(dados)

# Função para obter dados da tabela de histórico de compra com paginação
def get_historico_compra(pagina, por_pagina):
    conn = sqlite3.connect('smart_pricing.db')
    cursor = conn.cursor()
    offset = (pagina - 1) * por_pagina  # Cálculo para o deslocamento
    cursor.execute(f"SELECT * FROM preco_compra LIMIT {por_pagina} OFFSET {offset}")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Função para obter dados da tabela de histórico de venda com paginação
def get_historico_venda(pagina, por_pagina):
    conn = sqlite3.connect('smart_pricing.db')
    cursor = conn.cursor()
    offset = (pagina - 1) * por_pagina  # Cálculo para o deslocamento
    cursor.execute(f"SELECT * FROM preco_venda LIMIT {por_pagina} OFFSET {offset}")
    rows = cursor.fetchall()
    conn.close()
    return rows

app = Flask(__name__)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de cálculo de preço de compra
@app.route('/calcular_compra', methods=['GET'])
def calcular_compra():
    return render_template('calcular_compra.html')

# Rota para a página de cálculo de preço de venda
@app.route('/calcular_venda', methods=['GET'])
def calcular_venda():
    return render_template('calcular_venda.html')

# Rota para processar o cálculo de preço de compra
@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    nome_produto = data['nome_produto']
    sku = data['sku']
    preco_venda_concorrente = float(data['preco_venda_concorrente'])
    frete = float(data['frete'])
    impostos_percentual = float(data['impostos_percentual'])
    margem_lucro_percentual = float(data['margem_lucro_percentual'])

    preco_max_compra = calcular_preco_compra(preco_venda_concorrente, frete, impostos_percentual, margem_lucro_percentual)

    # Salvar os dados em um CSV
    salvar_dados_csv('dados_compra_precificacao.csv',
                     [nome_produto, sku, preco_venda_concorrente, frete, impostos_percentual, margem_lucro_percentual, preco_max_compra],
                     ['Nome do Produto', 'SKU', 'Preço Venda Concorrente', 'Frete', 'Impostos (%)', 'Margem de Lucro (%)', 'Preço Máximo de Compra'])

    return jsonify({
        'preco_max_compra': preco_max_compra
    })

# Rota para processar o cálculo de preço de venda
@app.route('/calcular_preco_venda', methods=['POST'])
def calcular_preco_venda():
    data = request.json
    nome_produto = data['nome_produto']
    sku = data['sku']
    custo_produto = float(data['custo_produto'])
    frete = float(data['frete'])
    margem_lucro_percentual = float(data['margem_lucro_percentual'])
    impostos_percentual = float(data['impostos_percentual'])

    # Salvar os dados em um CSV
    preco_venda = calcular_preco_venda_func(custo_produto, frete, margem_lucro_percentual, impostos_percentual)

    salvar_dados_csv('dados_venda_precificacao.csv',
                     [nome_produto, sku, custo_produto, frete, margem_lucro_percentual, impostos_percentual, preco_venda],
                     ['Nome do Produto', 'SKU', 'Custo do Produto', 'Frete', 'Margem de Lucro (%)', 'Impostos (%)', 'Preço de Venda'])

    return jsonify({
        'preco_venda': preco_venda
    })

# Rota para o histórico de preços de compra com paginação
@app.route('/ver_preco_compra')
def ver_preco_compra():
    pagina = request.args.get('pagina', 1, type=int)  # Obter o número da página atual
    por_pagina = 10  # Definir quantos registros por página
    rows = get_historico_compra(pagina, por_pagina)
    
    return render_template('ver_preco_compra.html', rows=rows, pagina=pagina)

# Rota para o histórico de preços de venda com paginação
@app.route('/ver_preco_venda')
def ver_preco_venda():
    pagina = request.args.get('pagina', 1, type=int)  # Obter o número da página atual
    por_pagina = 10  # Definir quantos registros por página
    rows = get_historico_venda(pagina, por_pagina)
    
    return render_template('ver_preco_venda.html', rows=rows, pagina=pagina)

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

# Exemplo de como usar para carregar dados dos CSVs
inserir_preco_compra('dados_compra_precificacao.csv')
inserir_preco_venda('dados_venda_precificacao.csv')

if __name__ == '__main__':
    criar_banco_e_tabelas()
    inserir_preco_compra('dados_compra_precificacao.csv')
    inserir_preco_venda('dados_venda_precificacao.csv')
    app.run()
