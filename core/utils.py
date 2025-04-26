#utils
from .models import ItemInspecao, ProdutoRecebido

def gerar_itens_inspecao_para_recebimento(recebimento):
    contador = 1

    # Apaga qualquer item anterior (se quiser começar do zero sempre)
    ItemInspecao.objects.filter(recebimento=recebimento).delete()

    for produto in recebimento.produtos.all():
        print(f"Produto: {produto.tipo_produto.nome} - Qtd: {produto.quantidade_recebida}")
        for i in range(produto.quantidade_recebida):
            codigo = f"R{recebimento.id:03d}-{contador:03d}"
            print(f"  Criando item: {codigo}")
            ItemInspecao.objects.create(
                recebimento=recebimento,
                produto_recebido=produto,
                codigo_produto=codigo
            )
            contador += 1

