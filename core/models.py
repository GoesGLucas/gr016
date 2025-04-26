#models
from django.db import models
from django.utils.translation import gettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey
from django.utils import timezone

class Funcionario(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    razao_social = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.razao_social


class Transportadora(models.Model):
    razao_social = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.razao_social


class TipoProduto(models.Model):
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class DescricaoProduto(models.Model):
    tipo_produto = models.ForeignKey(TipoProduto, on_delete=models.CASCADE)
    descricao = models.TextField()

    def __str__(self):
        return f'{self.tipo_produto.nome} - {self.descricao}'


class Setor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Localizacao(models.Model):
    local = models.CharField(max_length=100)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.setor.nome} - {self.local}"


class Recebimento(models.Model):
    data_recebimento = models.DateField(default=timezone.now)
    numero_nf = models.CharField(max_length=50)
    numero_contrato = models.CharField(max_length=50, blank=True)
    tecnico_responsavel = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, related_name='tecnico_responsavel')
    tecnico_recebimento = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, related_name='tecnico_recebimento')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True)
    transportadora = models.ForeignKey(Transportadora, on_delete=models.SET_NULL, null=True)
    entregador = models.CharField(max_length=100, blank=True)
    documento_entregador = models.CharField(max_length=50, blank=True)
    volumes_recebidos = models.PositiveIntegerField()
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Recebimento {self.id} - NF: {self.numero_nf}"


def upload_anexo_recebimento(instance, filename):
    return f"recebimentos/{instance.recebimento.id}/{filename}"


class AnexoRecebimento(models.Model):
    recebimento = models.ForeignKey('Recebimento', on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to=upload_anexo_recebimento)
    data_upload = models.DateTimeField(auto_now_add=True)  # Adicione este campo

    def __str__(self):
        return self.arquivo.name


class ProdutoRecebido(models.Model):
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE, related_name='produtos')
    tipo_produto = models.ForeignKey(TipoProduto, on_delete=models.SET_NULL, null=True)
    quantidade_recebida = models.PositiveIntegerField()
    quantidade_nf = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.tipo_produto.nome} - {self.recebimento}"

class TipoPreservacao(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class ItemInspecao(models.Model):
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE)
    produto_recebido = models.ForeignKey(ProdutoRecebido, on_delete=models.CASCADE)
    codigo_produto = models.CharField(max_length=100, unique=True)  # Garantindo unicidade
    serial_produto = models.CharField(max_length=100, blank=True)
    descricao = models.ForeignKey(DescricaoProduto, on_delete=models.SET_NULL, null=True, blank=True)
    dimensao = models.CharField(max_length=100, help_text="Formato: Altura x Largura x Comprimento (cm)", blank=True)
    peso = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    patrimonio = models.BooleanField(default=False)
    preservacao = models.BooleanField(default=False)
    tipo_preservacao = models.ForeignKey(TipoPreservacao, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Item {self.codigo_produto} - {self.produto_recebido.tipo_produto}"


class Preservacao(models.Model):
    class StatusPreservacao(models.TextChoices):
        OK = 'OK', _('Preservação OK')
        RESTRICAO = 'RESTRICAO', _('Preservação com Restrições')

    item = models.ForeignKey(ItemInspecao, on_delete=models.CASCADE, related_name='preservacoes')
    data_preservacao = models.DateField()
    proxima_preservacao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusPreservacao.choices)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.item.codigo_produto} - {self.status}"


def upload_anexo_preservacao(instance, filename):
    return f"preservacoes/{instance.preservacao.id}/{filename}"


class AnexoPreservacao(models.Model):
    preservacao = models.ForeignKey(Preservacao, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to=upload_anexo_preservacao)
    data_upload = models.DateTimeField(auto_now_add=True)  # Adicione este campo

    def __str__(self):
        return f"Anexo - {self.preservacao.item.codigo_produto}"

class Movimentacao(models.Model):
    item = models.ForeignKey(ItemInspecao, on_delete=models.CASCADE, related_name='movimentacoes')
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    local = ChainedForeignKey(
        Localizacao,
        chained_field="setor",
        chained_model_field="setor",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.codigo_produto} -> {self.setor.nome}/{self.local.local}"

class SolicitacaoUso(models.Model):
    item = models.ForeignKey(ItemInspecao, on_delete=models.CASCADE, related_name='solicitacoes')
    solicitante = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True)
    motivo = models.CharField(max_length=255)
    observacoes = models.TextField(blank=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.codigo_produto} - {self.solicitante.nome}"


def upload_anexo_solicitacao(instance, filename):
    return f"solicitacoes/{instance.solicitacao.id}/{filename}"

class AnexoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoUso, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to=upload_anexo_solicitacao)
    data_upload = models.DateTimeField(auto_now_add=True)  # Adicione este campo

    def __str__(self):
        return f"Anexo - {self.solicitacao.item.codigo_produto}"
