function calcularPrecoVenda() {
    const nome_produto = document.getElementById("nome_produto").value;
    const sku = document.getElementById("sku").value;
    const custo_produto = parseFloat(document.getElementById("custo_produto").value);
    const frete = parseFloat(document.getElementById("frete").value);
    const margem_lucro_percentual = parseFloat(document.getElementById("margem_lucro_percentual").value);
    const impostos_percentual = parseFloat(document.getElementById("impostos_percentual").value);

    const data = {
        nome_produto: nome_produto,
        sku: sku,
        custo_produto: custo_produto,
        frete: frete,
        margem_lucro_percentual: margem_lucro_percentual,
        impostos_percentual: impostos_percentual
    };

    fetch('/calcular_preco_venda', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        const resultadoDiv = document.getElementById("resultado_venda");
        resultadoDiv.innerHTML = `
            <h3>Resultado</h3>
            <p><strong>Produto:</strong> ${nome_produto} (SKU: ${sku})</p>
            <p><strong>Preço de Venda:</strong> R$ ${result.preco_venda.toFixed(2)}</p>
        `;
        document.getElementById("formulario_venda").reset();  // Limpar os campos do formulário
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}