#admin
from django.contrib import admin
from .models import (
    Funcionario, Fornecedor, Transportadora, TipoProduto,
    DescricaoProduto, Setor, Localizacao, Recebimento,
    ProdutoRecebido, AnexoRecebimento, ItemInspecao,
    TipoPreservacao, Preservacao, AnexoPreservacao, Movimentacao,
    SolicitacaoUso, AnexoSolicitacao,
)
from django.contrib import messages
from .utils import gerar_itens_inspecao_para_recebimento
from .forms import ItemInspecaoForm, MovimentacaoForm

class ProdutoRecebidoInline(admin.TabularInline):
    model = ProdutoRecebido
    extra = 1

class AnexoRecebimentoInline(admin.TabularInline):
    model = AnexoRecebimento
    extra = 1

@admin.register(Recebimento)
class RecebimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_nf', 'data_recebimento', 'fornecedor')
    inlines = [ProdutoRecebidoInline, AnexoRecebimentoInline]
    actions = ['gerar_itens_inspecao']

    def gerar_itens_inspecao(self, request, queryset):
        for recebimento in queryset:
            gerar_itens_inspecao_para_recebimento(recebimento)
        self.message_user(request, "Itens de inspeção gerados com sucesso.", level=messages.SUCCESS)
    gerar_itens_inspecao.short_description = "Gerar Itens de Inspeção"

@admin.register(ItemInspecao)
class ItemInspecaoAdmin(admin.ModelAdmin):
    form = ItemInspecaoForm
    list_display = ('codigo_produto', 'produto_recebido', 'serial_produto', 'descricao')

class AnexoPreservacaoInline(admin.TabularInline):
    model = AnexoPreservacao
    extra = 1

@admin.register(Preservacao)
class PreservacaoAdmin(admin.ModelAdmin):
    list_display = ('item', 'data_preservacao', 'proxima_preservacao', 'status')
    inlines = [AnexoPreservacaoInline]

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    form = MovimentacaoForm
    list_display = ('item', 'tipo_produto', 'setor', 'local', 'data_movimentacao')

    def tipo_produto(self, obj):
        return obj.item.produto.tipo_produto  # Exemplo, altere conforme seu modelo
    tipo_produto.admin_order_field = 'item__produto__tipo_produto'  # Permite ordenar por esse campo
    tipo_produto.short_description = 'Tipo de Produto'

class AnexoSolicitacaoInline(admin.TabularInline):
    model = AnexoSolicitacao
    extra = 1

@admin.register(SolicitacaoUso)
class SolicitacaoUsoAdmin(admin.ModelAdmin):
    list_display = ('item', 'solicitante', 'motivo', 'data_solicitacao')
    inlines = [AnexoSolicitacaoInline]

admin.site.register(Funcionario)
admin.site.register(Fornecedor)
admin.site.register(Transportadora)
admin.site.register(TipoProduto)
admin.site.register(DescricaoProduto)
admin.site.register(Setor)
admin.site.register(Localizacao)
admin.site.register(TipoPreservacao)