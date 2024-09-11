function calcularPrecoCompra() {
    const nome_produto = document.getElementById("nome_produto").value;
    const sku = document.getElementById("sku").value;
    const preco_venda_concorrente = parseFloat(document.getElementById("preco_venda_concorrente").value);
    const frete = parseFloat(document.getElementById("frete").value);
    const impostos_percentual = parseFloat(document.getElementById("impostos_percentual").value);
    const margem_lucro_percentual = parseFloat(document.getElementById("margem_lucro_percentual").value);

    const data = {
        nome_produto: nome_produto,
        sku: sku,
        preco_venda_concorrente: preco_venda_concorrente,
        frete: frete,
        impostos_percentual: impostos_percentual,
        margem_lucro_percentual: margem_lucro_percentual
    };

    fetch('/calcular', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        const resultadoDiv = document.getElementById("resultado");
        resultadoDiv.innerHTML = `
            <h3>Resultado</h3>
            <p><strong>Produto:</strong> ${nome_produto} (SKU: ${sku})</p>
            <p><strong>Preço Máximo de Compra:</strong> R$ ${result.preco_max_compra.toFixed(2)}</p>
        `;
        document.getElementById("formulario").reset();  // Limpar os campos do formulário
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}
