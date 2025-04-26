#forms
from django import forms
from .models import (ItemInspecao, DescricaoProduto, Movimentacao, Localizacao,
                    Funcionario, Fornecedor, Transportadora, TipoProduto,
                    Recebimento, ProdutoRecebido, Preservacao, SolicitacaoUso,
                     TipoPreservacao, Setor)
from django.contrib import admin
from .widgets import ItemAutocompleteWidget
from django.forms import DateInput


class ItemInspecaoForm(forms.ModelForm):
    class Meta:
        model = ItemInspecao
        fields = '__all__'
        widgets = {
            'serial_produto': forms.TextInput(attrs={'class': 'form-control'}),
            'dimensao': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'patrimonio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preservacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'descricao': forms.Select(attrs={'class': 'form-control'}),
            'tipo_preservacao': forms.Select(attrs={'class': 'form-control'}),
            'recebimento': forms.Select(attrs={'class': 'form-control'}),
            'produto_recebido': forms.Select(attrs={'class': 'form-control'}),
            'codigo_produto': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        admin_site = kwargs.pop('admin_site', admin.site)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.produto_recebido:
            tipo_produto = self.instance.produto_recebido.tipo_produto
            self.fields['descricao'].queryset = DescricaoProduto.objects.filter(tipo_produto=tipo_produto)
        else:
            self.fields['descricao'].queryset = DescricaoProduto.objects.none()

        # Não aplique o RelatedFieldWidgetWrapper para evitar os botões do admin
        # self.fields['descricao'].widget = RelatedFieldWidgetWrapper(
        #     self.fields['descricao'].widget,
        #     ItemInspecao._meta.get_field('descricao').remote_field,
        #     admin_site,
        #     can_add_related=True,
        #     can_change_related=True,
        #     can_delete_related=True
        # )

        # self.fields['tipo_preservacao'].widget = RelatedFieldWidgetWrapper(
        #     self.fields['tipo_preservacao'].widget,
        #     ItemInspecao._meta.get_field('tipo_preservacao').remote_field,
        #     admin_site,
        #     can_add_related=True,
        #     can_change_related=True,
        #     can_delete_related=True
        # )


class MovimentacaoForm(forms.ModelForm):
    data_movimentacao = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Movimentacao
        fields = '__all__'
        widgets = {
            'item': ItemAutocompleteWidget(attrs={'class': 'form-control w-100'}),
            'setor': forms.Select(attrs={'class': 'form-control'}),
            'local': forms.Select(attrs={'class': 'form-control'}),
            # se quiser manter tudo padronizado no mesmo estilo Bootstrap
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicializa dinamicamente o queryset de 'local' com base no setor
        if 'setor' in self.data:
            try:
                setor_id = int(self.data.get('setor'))
                self.fields['local'].queryset = Localizacao.objects.filter(setor_id=setor_id)
            except (ValueError, TypeError):
                self.fields['local'].queryset = Localizacao.objects.none()
        elif self.instance.pk:
            self.fields['local'].queryset = Localizacao.objects.filter(setor=self.instance.setor)
        else:
            self.fields['local'].queryset = Localizacao.objects.none()


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'cargo', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['razao_social', 'cnpj', 'telefone', 'email']
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    labels = {
        'razao_social': 'Razão Social',
        'cnpj': 'CNPJ',
        'telefone': 'Telefone',
        'email': 'E-mail',
    }

class TransportadoraForm(forms.ModelForm):
    class Meta:
        model = Transportadora
        fields = ['razao_social', 'cnpj', 'telefone', 'email']
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class TipoProdutoForm(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = ['nome', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DescricaoProdutoForm(forms.ModelForm):
    class Meta:
        model = DescricaoProduto
        fields = ['tipo_produto', 'descricao']
        widgets = {
            'tipo_produto': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),  # <-- campo simples, sem autocompletar
        }

class TipoPreservacaoForm(forms.ModelForm):
    class Meta:
        model = TipoPreservacao
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'})
        }

class LocalizacaoForm(forms.ModelForm):
    class Meta:
        model = Localizacao
        fields = ['setor', 'local', 'ativo']
        widgets = {
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    setor = forms.ModelChoiceField(queryset=Setor.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RecebimentoForm(forms.ModelForm):
    data_recebimento = forms.DateField(
        widget=DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
            format='%Y-%m-%d'
        )
    )

    class Meta:
        model = Recebimento
        fields = [
            'data_recebimento', 'numero_nf', 'numero_contrato', 'tecnico_responsavel',
            'tecnico_recebimento', 'fornecedor', 'transportadora', 'entregador',
            'documento_entregador', 'volumes_recebidos', 'observacoes'
        ]
        widgets = {
            'numero_nf': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_contrato': forms.TextInput(attrs={'class': 'form-control'}),
            'entregador': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_entregador': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'volumes_recebidos': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProdutoRecebidoForm(forms.ModelForm):
    class Meta:
        model = ProdutoRecebido
        fields = ['tipo_produto', 'quantidade_recebida', 'quantidade_nf', 'preco_unitario', 'preco_total']
        widgets = {
            'tipo_produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_recebida': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade_nf': forms.NumberInput(attrs={'class': 'form-control'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'preco_total': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_quantidade_recebida(self):
        quantidade = self.cleaned_data.get('quantidade_recebida')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError('A quantidade recebida não pode ser negativa.')
        return quantidade

    def clean_quantidade_nf(self):
        quantidade_nf = self.cleaned_data.get('quantidade_nf')
        if quantidade_nf is not None and quantidade_nf < 0:
            raise forms.ValidationError('A quantidade da NF não pode ser negativa.')
        return quantidade_nf

    def clean_preco_unitario(self):
        preco_unitario = self.cleaned_data.get('preco_unitario')
        if preco_unitario is not None and preco_unitario < 0:
            raise forms.ValidationError('O preço unitário não pode ser negativo.')
        return preco_unitario

    def clean_preco_total(self):
        preco_total = self.cleaned_data.get('preco_total')
        if preco_total is not None and preco_total < 0:
            raise forms.ValidationError('O preço total não pode ser negativo.')
        return preco_total


class AnexoRecebimentoForm(forms.Form):
    arquivos = forms.FileField(required=False)


class PreservacaoForm(forms.ModelForm):
    class Meta:
        model = Preservacao
        fields = ['item', 'data_preservacao', 'proxima_preservacao', 'status', 'observacoes']
        widgets = {
            'item': ItemAutocompleteWidget,
            'data_preservacao': forms.DateInput(attrs={'type': 'date'}),
            'proxima_preservacao': forms.DateInput(attrs={'type': 'date'}),
        }

class SolicitacaoUsoForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=ItemInspecao.objects.all(),
        label='Código do Produto',
        widget=ItemAutocompleteWidget(attrs={'class': 'form-control'})
    )
    solicitante = forms.ModelChoiceField(
        queryset=Funcionario.objects.all(),
        label='Solicitante',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    motivo = forms.CharField(
        label='Motivo da Solicitação',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    observacoes = forms.CharField(
        label='Observações',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': False}),
        required=False
    )

    class Meta:
        model = SolicitacaoUso
        fields = ['item', 'solicitante', 'motivo', 'observacoes']