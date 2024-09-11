from flask import Flask, render_template, request, jsonify
import csv
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)