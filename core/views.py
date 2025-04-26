#views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from .models import (ItemInspecao, Movimentacao, Preservacao, Funcionario, Fornecedor,
                     Transportadora, TipoProduto, DescricaoProduto, Localizacao, Setor,
                     ProdutoRecebido, AnexoRecebimento, Recebimento, AnexoPreservacao,
                     SolicitacaoUso, AnexoSolicitacao, TipoPreservacao)
from django.contrib.auth.decorators import login_required
from .forms import (FuncionarioForm, FornecedorForm, TransportadoraForm,
                    TipoProdutoForm, DescricaoProdutoForm, LocalizacaoForm,
                    RecebimentoForm, ProdutoRecebidoForm, AnexoRecebimentoForm,
                    ItemInspecaoForm, MovimentacaoForm, PreservacaoForm,
                    SolicitacaoUsoForm, SetorForm)
from django.forms import modelformset_factory, inlineformset_factory
from .utils import gerar_itens_inspecao_para_recebimento
from django_select2.views import AutoResponseView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


@login_required
def home_view(request):
    return render(request, 'core/home.html')

ProdutoRecebidoFormSet = inlineformset_factory(
    Recebimento, ProdutoRecebido, form=ProdutoRecebidoForm, extra=1, can_delete=True
)

@login_required
def recebimento_view(request):
    if request.method == 'POST':
        print("Requisição POST recebida.")
        print(f"FILES: {request.FILES}")
        recebimento_form = RecebimentoForm(request.POST, request.FILES)
        produto_formset = ProdutoRecebidoFormSet(request.POST, instance=recebimento_form.instance)

        if recebimento_form.is_valid() and produto_formset.is_valid():
            recebimento = recebimento_form.save()
            produto_formset.instance = recebimento
            produto_formset.save()

            arquivos = request.FILES.getlist('arquivos[]')  # Alteração aqui!
            print(f"Arquivos recebidos (getlist): {arquivos}")

            for arquivo in arquivos:
                print(f"Arquivo {arquivo.name} será salvo.")
                anexo = AnexoRecebimento(recebimento=recebimento, arquivo=arquivo)
                anexo.save()

            return redirect('recebimentos_list')

        else:
            print(f"Erro nos formulários: {recebimento_form.errors}, {produto_formset.errors}")
    else:
        recebimento_form = RecebimentoForm()
        produto_formset = ProdutoRecebidoFormSet(instance=Recebimento())

    context = {
        'form': recebimento_form,
        'formset': produto_formset,
    }
    return render(request, 'core/recebimento.html', context)


@login_required
def recebimentos_list(request):
    # Filtros
    codigo_recebimento = request.GET.get('codigo_recebimento')
    numero_nf = request.GET.get('numero_nf')
    contrato = request.GET.get('contrato')
    fornecedor_id = request.GET.get('fornecedor')

    # Comece a consulta com todos os recebimentos
    recebimentos = Recebimento.objects.all()

    if codigo_recebimento:
        recebimentos = recebimentos.filter(id__icontains=codigo_recebimento)

    if numero_nf:
        recebimentos = recebimentos.filter(numero_nf__icontains=numero_nf)

    if contrato:
        recebimentos = recebimentos.filter(contrato__icontains=contrato)

    if fornecedor_id:
        recebimentos = recebimentos.filter(fornecedor_id=fornecedor_id)

    # Criar lista de recebimentos com status de inspeção gerada
    recebimentos_com_status = []
    for recebimento in recebimentos:
        ja_gerou_inspecao = ItemInspecao.objects.filter(recebimento=recebimento).exists()
        recebimentos_com_status.append({
            'recebimento': recebimento,
            'ja_gerou_inspecao': ja_gerou_inspecao
        })

    # Paginação
    paginator = Paginator(recebimentos_com_status, 10)
    page_number = request.GET.get('page')  # Página atual
    page_obj = paginator.get_page(page_number)

    # Buscar fornecedores para o filtro
    fornecedores = Fornecedor.objects.all()

    context = {
        'page_obj': page_obj,
        'fornecedores': fornecedores,
    }
    return render(request, 'core/recebimentos_list.html', context)

@login_required
def recebimento_detail(request, id):
    # Buscar o recebimento pelo ID
    recebimento = get_object_or_404(Recebimento, id=id)

    # Renderizar a página com os detalhes do recebimento
    return render(request, 'core/recebimento_detail.html', {'recebimento': recebimento})

@login_required
def recebimento_edit(request, id):
    print(f"RECEBIMENTO_EDIT: Iniciando para ID = {id}")
    recebimento = get_object_or_404(Recebimento, id=id)
    print(f"RECEBIMENTO_EDIT: Recebimento encontrado: {recebimento}")

    if request.method == 'POST':
        print("RECEBIMENTO_EDIT: Método POST recebido")
        form = RecebimentoForm(request.POST, request.FILES, instance=recebimento)
        produto_formset = ProdutoRecebidoFormSet(request.POST, instance=recebimento)
        print("RECEBIMENTO_EDIT: Formulários instanciados")

        if form.is_valid() and produto_formset.is_valid():
            print("RECEBIMENTO_EDIT: Formulários válidos")
            try:
                recebimento = form.save()
                produto_formset.instance = recebimento
                produto_formset.save()
                print("RECEBIMENTO_EDIT: Dados salvos")

                arquivos = request.FILES.getlist('arquivos[]')
                print(f"RECEBIMENTO_EDIT: Arquivos recebidos: {arquivos}")
                for arquivo in arquivos:
                    print(f"RECEBIMENTO_EDIT: Salvando arquivo {arquivo.name}")
                    AnexoRecebimento.objects.create(recebimento=recebimento, arquivo=arquivo)
                print("RECEBIMENTO_EDIT: Novos anexos criados")

                print(f"RECEBIMENTO_EDIT: Redirecionando para recebimento_detail com ID = {recebimento.id}")
                return redirect('recebimento_detail', id=recebimento.id)
            except Exception as e:
                print(f"RECEBIMENTO_EDIT: Erro durante o salvamento: {e}")
        else:
            print(f"RECEBIMENTO_EDIT: Erros no formulário: {form.errors}, {produto_formset.errors}")
    else:
        print("RECEBIMENTO_EDIT: Método GET recebido")
        form = RecebimentoForm(instance=recebimento)
        produto_formset = ProdutoRecebidoFormSet(instance=recebimento)

    anexos = recebimento.anexos.all()
    print("RECEBIMENTO_EDIT: Renderizando template")
    return render(request, 'core/recebimento_edit.html', {
        'form': form,
        'formset': produto_formset,
        'anexos': anexos,
        'recebimento': recebimento
    })

@login_required
def excluir_anexo_recebimento(request, id, anexo_id):
    anexo = get_object_or_404(AnexoRecebimento, id=anexo_id, recebimento_id=id)

    if request.method == 'POST':
        # Opcional: Adicione lógica de permissão
        anexo.arquivo.delete(save=False)
        anexo.delete()
        return redirect('recebimento_edit', id=id)
    else:
        # Se a requisição não for POST, exiba uma confirmação (opcional)
        return render(request, 'core/confirmar_exclusao_anexo_recebimento.html', {'anexo': anexo, 'recebimento_id': id})

@login_required
def inspecao_view(request):
    numero_nf = request.GET.get('numero_nf', '')
    codigo_produto = request.GET.get('codigo_produto', '')
    produto = request.GET.get('produto', '')
    serial_produto = request.GET.get('serial_produto', '')

    itens = ItemInspecao.objects.select_related(
        'produto_recebido', 'produto_recebido__tipo_produto', 'descricao', 'recebimento'
    )

    if numero_nf:
        itens = itens.filter(recebimento__numero_nf__icontains=numero_nf)
    if codigo_produto:
        itens = itens.filter(codigo_produto__icontains=codigo_produto)
    if produto:
        itens = itens.filter(produto_recebido__tipo_produto__nome__icontains=produto)
    if serial_produto:
        itens = itens.filter(serial_produto__icontains=serial_produto)

    itens = itens.order_by('codigo_produto')

    paginator = Paginator(itens, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/inspecao.html', {'page_obj': page_obj})


@login_required
def inspecao_detail(request, id):
    # Buscar o ItemInspecao pelo id
    item_inspecao = get_object_or_404(ItemInspecao, id=id)  # Usamos o 'id' do ItemInspecao aqui
    tipos_produto = TipoProduto.objects.all()

    if request.method == 'POST':
        print("Método POST recebido na view inspecao_detail!")  # ADICIONE ESTA LINHA
        form = ItemInspecaoForm(request.POST, instance=item_inspecao)
        if form.is_valid():
            form.save()
            return redirect('inspecao')
        else:
            print(form.errors) # Para ver os erros de validação
    else:
        form = ItemInspecaoForm(instance=item_inspecao)

    return render(request, 'core/inspecao_detail.html', {
        'form': form,
        'item_inspecao': item_inspecao,
        'codigo_produto': item_inspecao.codigo_produto,
        'serial_produto': item_inspecao.serial_produto,
        'tipos_produto': tipos_produto,
    })


@login_required
def movimentacao_list(request):
    # Obter filtros da URL
    codigo_produto = request.GET.get('codigo_produto', '')
    setor = request.GET.get('setor', '')
    local = request.GET.get('local', '')

    # Filtrar as movimentações com base nos parâmetros
    movimentacoes = Movimentacao.objects.all()

    if codigo_produto:
        movimentacoes = movimentacoes.filter(item__codigo_produto__icontains=codigo_produto)

    if setor:
        movimentacoes = movimentacoes.filter(setor__nome__icontains=setor)

    if local:
        movimentacoes = movimentacoes.filter(local__local__icontains=local)

    # Paginação
    paginator = Paginator(movimentacoes, 10)
    page_number = request.GET.get('page')  # Pega o número da página na URL
    page_obj = paginator.get_page(page_number)  # Retorna a página correspondente

    return render(request, 'core/movimentacao_list.html', {
        'page_obj': page_obj,  # Passa o objeto de página para o template
        'codigo_produto': codigo_produto,
        'setor': setor,
        'local': local,
    })

@login_required
def movimentacao_create(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('movimentacao_list')
    else:
        form = MovimentacaoForm()
    return render(request, 'core/movimentacao_form.html', {'form': form})



@login_required
def movimentacao_detail(request, id):
    movimentacao = Movimentacao.objects.get(id=id)

    # Impede que edite se a movimentação já foi registrada
    editable = not movimentacao.data_movimentacao

    if request.method == 'POST' and editable:
        form = MovimentacaoForm(request.POST, instance=movimentacao)
        if form.is_valid():
            form.save()
            return redirect('movimentacao_list')
    else:
        form = MovimentacaoForm(instance=movimentacao)

    return render(request, 'core/movimentacao_form.html', {
        'form': form,
        'movimentacao': movimentacao,
        'editable': editable
    })


class ItemAutocomplete(AutoResponseView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ItemInspecao.objects.none()

        qs = ItemInspecao.objects.all()
        if self.q:
            qs = qs.filter(codigo_produto__icontains=self.q)
        return qs

@login_required
def preservacao_list(request):
    preservacoes = Preservacao.objects.all()

    # Filtros
    codigo_produto = request.GET.get('codigo_produto')
    serial_produto = request.GET.get('serial_produto')

    if codigo_produto:
        preservacoes = preservacoes.filter(item__codigo_produto__icontains=codigo_produto)
    if serial_produto:
        preservacoes = preservacoes.filter(item__serial_produto__icontains=serial_produto)

    paginator = Paginator(preservacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/preservacao_list.html', {
        'page_obj': page_obj,
    })

@login_required
def preservacao_view(request):
    if request.method == 'POST':
        form = PreservacaoForm(request.POST, request.FILES)

        if form.is_valid():
            preservacao = form.save()  # Salva o objeto de preservação

            # Processar os múltiplos anexos
            for arquivo in request.FILES.getlist('arquivos[]'):
                if arquivo:  # Certifique-se de que um arquivo foi enviado
                    anexo = AnexoPreservacao(preservacao=preservacao, arquivo=arquivo)
                    anexo.save()

            return redirect('preservacao_list')

    else:
        form = PreservacaoForm()

    return render(request, 'core/preservacao.html', {
        'form': form,
    })

@login_required
def solicitacao_view(request):
    if request.method == 'POST':
        form = SolicitacaoUsoForm(request.POST, request.FILES)
        if form.is_valid():
            solicitacao = form.save()  # Salva o formulário diretamente

            # Processar os múltiplos anexos
            for arquivo in request.FILES.getlist('arquivos[]'):
                if arquivo:
                    anexo = AnexoSolicitacao(solicitacao=solicitacao, arquivo=arquivo)
                    anexo.save()

            return redirect('solicitacao_list')
        else:
            return render(request, 'core/solicitacao.html', {'form': form})
    else:
        form = SolicitacaoUsoForm()
    return render(request, 'core/solicitacao.html', {'form': form})

@login_required
def solicitacao_list(request):
    solicitacoes = SolicitacaoUso.objects.all()

    # Filtros
    codigo_produto = request.GET.get('codigo_produto')
    nome_solicitante = request.GET.get('solicitante')

    if codigo_produto:
        solicitacoes = solicitacoes.filter(item__codigo_produto__icontains=codigo_produto)
    if nome_solicitante:
        solicitacoes = solicitacoes.filter(solicitante__nome__icontains=nome_solicitante)

    paginator = Paginator(solicitacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/solicitacao_list.html', {
        'page_obj': page_obj,
    })

@login_required
def relatorio_view(request):
    itens = ItemInspecao.objects.all().select_related(
        'produto_recebido__recebimento',
        'descricao'
    ).prefetch_related('movimentacoes', 'preservacoes')

    filtro_setor = request.GET.get('setor')
    filtro_status = request.GET.get('status')
    busca = request.GET.get('busca')

    dados = []
    for item in itens:
        recebimento = item.recebimento
        descricao = item.descricao.descricao if item.descricao else ''
        movimentacoes = item.movimentacoes.order_by('-data_movimentacao')
        ultima_mov = movimentacoes.first()
        setor = ultima_mov.setor.nome if ultima_mov and ultima_mov.setor else ''
        local = ultima_mov.local.local if ultima_mov and ultima_mov.local else ''

        ultima_preserv = item.preservacoes.order_by('-data_preservacao').first()
        status_preservacao = ultima_preserv.status if ultima_preserv else 'Não informado'

        registro = {
            'numero_recebimento': recebimento.id,
            'data_recebimento': recebimento.data_recebimento,
            'codigo_produto': item.codigo_produto,
            'descricao': descricao,
            'setor': setor,
            'local': local,
            'status_preservacao': status_preservacao,
        }

        # Aplicar filtros
        if filtro_setor and setor != filtro_setor:
            continue
        if filtro_status and status_preservacao != filtro_status:
            continue
        if busca and busca.lower() not in (item.codigo_produto.lower() + descricao.lower()):
            continue

        dados.append(registro)

    # Paginação
    paginator = Paginator(dados, 20)  # 10 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'exportar' in request.GET:
        return exportar_excel(dados)

    # Coletar opções únicas de filtro
    setores = sorted(set(d['setor'] for d in dados if d['setor']))
    statuses = ['OK', 'RESTRICAO', 'Não informado']

    context = {
        'page_obj': page_obj,
        'setores': setores,
        'statuses': statuses,
        'filtro_setor': filtro_setor,
        'filtro_status': filtro_status,
        'busca': busca,
    }

    return render(request, 'core/relatorio.html', context)

def exportar_excel(dados):
    wb = Workbook()
    ws = wb.active
    ws.title = "Relatório de Itens"

    # Cabeçalhos
    headers = ['Nº Recebimento', 'Data Recebimento', 'Código do Produto', 'Descrição', 'Setor', 'Local', 'Status da Preservação']
    ws.append(headers)

    for d in dados:
        ws.append([
            d['numero_recebimento'],
            d['data_recebimento'].strftime('%d/%m/%Y') if d['data_recebimento'] else '',
            d['codigo_produto'],
            d['descricao'],
            d['setor'],
            d['local'],
            d['status_preservacao'],
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=relatorio_estoque.xlsx'
    wb.save(response)
    return response

@login_required
def anexos_view(request):
    codigo_recebimento = request.GET.get('codigo_recebimento', '').strip()
    codigo_produto = request.GET.get('codigo_produto', '').strip()
    numero_nf_busca = request.GET.get('numero_nf', '').strip()
    todos_anexos = []

    q_recebimento = Q()
    if codigo_recebimento:
        q_recebimento |= Q(recebimento__id__exact=codigo_recebimento) # Busca exata por ID do recebimento
    if numero_nf_busca:
        q_recebimento |= Q(recebimento__numero_nf__icontains=numero_nf_busca)

    anexos_recebimento = AnexoRecebimento.objects.select_related('recebimento').filter(q_recebimento)
    for anexo in anexos_recebimento:
        todos_anexos.append({
            'tipo': 'Recebimento',
            'codigo_produto': '',
            'vinculo': f'Recebimento #{anexo.recebimento.id} - NF: {anexo.recebimento.numero_nf}',
            'arquivo': anexo.arquivo.url,
            'nome_arquivo': anexo.arquivo.name.split('/')[-1],
            'data_upload': anexo.data_upload
        })

    q_preservacao = Q()
    if codigo_produto:
        q_preservacao |= Q(preservacao__item__codigo_produto__icontains=codigo_produto)

    anexos_preservacao = AnexoPreservacao.objects.select_related('preservacao__item').filter(q_preservacao)
    for anexo in anexos_preservacao:
        todos_anexos.append({
            'tipo': 'Preservação',
            'codigo_produto': anexo.preservacao.item.codigo_produto if anexo.preservacao.item else '',
            'vinculo': f'Preservação do item #{anexo.preservacao.item.id}',
            'arquivo': anexo.arquivo.url,
            'nome_arquivo': anexo.arquivo.name.split('/')[-1],
            'data_upload': anexo.data_upload
        })

    q_solicitacao = Q()
    if codigo_produto:
        q_solicitacao |= Q(solicitacao__item__codigo_produto__icontains=codigo_produto)

    anexos_solicitacao = AnexoSolicitacao.objects.select_related('solicitacao__item').filter(q_solicitacao)
    for anexo in anexos_solicitacao:
        todos_anexos.append({
            'tipo': 'Solicitação',
            'codigo_produto': anexo.solicitacao.item.codigo_produto if anexo.solicitacao.item else '',
            'vinculo': f'Solicitação do item #{anexo.solicitacao.item.id}',
            'arquivo': anexo.arquivo.url,
            'nome_arquivo': anexo.arquivo.name.split('/')[-1],
            'data_upload': anexo.data_upload
        })

    anexos_filtrados = []
    for anexo in todos_anexos:
        incluir = True
        if codigo_recebimento and anexo['tipo'] == 'Recebimento' and codigo_recebimento != \
                str(anexo['vinculo']).replace('recebimento #', '').split(' - nf:')[0].strip():
            incluir = False
        if codigo_produto and anexo['tipo'] == 'Recebimento':
            incluir = False
        elif codigo_produto and anexo['tipo'] == 'Preservação' and codigo_produto.lower() not in str(anexo['codigo_produto']).lower():
            incluir = False
        elif codigo_produto and anexo['tipo'] == 'Solicitação' and codigo_produto.lower() not in str(anexo['codigo_produto']).lower():
            incluir = False
        if numero_nf_busca and anexo['tipo'] == 'Recebimento' and numero_nf_busca.lower() not in anexo['vinculo'].lower():
            incluir = False
        elif numero_nf_busca and anexo['tipo'] != 'Recebimento':
            incluir = False

        if incluir:
            anexos_filtrados.append(anexo)

    paginator = Paginator(anexos_filtrados, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/anexos_list.html', {
        'page_obj': page_obj,
        'codigo_recebimento': codigo_recebimento,
        'codigo_produto': codigo_produto,
        'numero_nf': numero_nf_busca,
        'anexos': todos_anexos
    })


@login_required
def cadastrar_funcionario(request):
    form = FuncionarioForm(request.POST or None)

    # Campos de busca
    nome = request.GET.get('nome', '')
    cargo = request.GET.get('cargo', '')

    # Filtro
    funcionarios = Funcionario.objects.all().order_by('nome')
    if nome:
        funcionarios = funcionarios.filter(nome__icontains=nome)
    if cargo:
        funcionarios = funcionarios.filter(cargo__icontains=cargo)

    # Paginação
    paginator = Paginator(funcionarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Salvamento do formulário
    if form.is_valid():
        form.save()
        return redirect('cadastrar_funcionario')

    context = {
        'form': form,
        'page_obj': page_obj,
        'nome': nome,
        'cargo': cargo,
    }
    return render(request, 'core/cadastro_funcionario.html', context)


@login_required
def cadastrar_fornecedor(request):
    form = FornecedorForm(request.POST or None)

    # Campos de busca
    razao_social = request.GET.get('razao_social', '')
    cnpj = request.GET.get('cnpj', '')

    # Filtro
    fornecedores = Fornecedor.objects.all()
    if razao_social:
        fornecedores = fornecedores.filter(razao_social__icontains=razao_social)
    if cnpj:
        fornecedores = fornecedores.filter(cnpj__icontains=cnpj)

    # Paginação
    paginator = Paginator(fornecedores, 10)
    page = request.GET.get('page')
    fornecedores_paginados = paginator.get_page(page)

    if form.is_valid():
        form.save()
        return redirect('cadastrar_fornecedor')

    context = {
        'form': form,
        'fornecedores': fornecedores_paginados,
        'razao_social': razao_social,
        'cnpj': cnpj,
    }
    return render(request, 'core/cadastro_fornecedor.html', context)


@login_required
def cadastrar_transportadora(request):
    form = TransportadoraForm(request.POST or None)

    razao_social = request.GET.get('razao_social', '')
    cnpj = request.GET.get('cnpj', '')

    transportadoras_list = Transportadora.objects.all().order_by('razao_social')
    if razao_social:
        transportadoras_list = transportadoras_list.filter(razao_social__icontains=razao_social)
    if cnpj:
        transportadoras_list = transportadoras_list.filter(cnpj__icontains=cnpj)

    paginator = Paginator(transportadoras_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if form.is_valid():
        form.save()
        return redirect('cadastrar_transportadora')

    return render(request, 'core/cadastro_transportadora.html', {
        'form': form,
        'page_obj': page_obj,
        'razao_social': razao_social,
        'cnpj': cnpj,
    })



@login_required
def cadastrar_tipo_produto(request):
    form = TipoProdutoForm(request.POST or None)

    # Campo de busca
    nome = request.GET.get('nome', '')

    # Filtro
    tipos_produto_list = TipoProduto.objects.all().order_by('nome')
    if nome:
        tipos_produto_list = tipos_produto_list.filter(nome__icontains=nome)

    # Paginação
    paginator = Paginator(tipos_produto_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if form.is_valid():
        form.save()
        return redirect('cadastrar_tipo_produto')

    return render(request, 'core/cadastro_tipo_produto.html', {
        'form': form,
        'page_obj': page_obj,
        'nome': nome,
    })


@login_required
def cadastrar_descricao_produto(request):
    form = DescricaoProdutoForm(request.POST or None)

    # Campos de busca
    descricao = request.GET.get('descricao', '')
    tipo = request.GET.get('tipo', '')

    # Filtro com busca combinada
    descricoes = DescricaoProduto.objects.all()
    if descricao:
        descricoes = descricoes.filter(descricao__icontains=descricao)
    if tipo:
        descricoes = descricoes.filter(tipo_produto__nome__icontains=tipo)

    descricoes = descricoes.order_by('-id')

    paginator = Paginator(descricoes, 10)  # 10 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if form.is_valid():
        form.save()
        return redirect('cadastrar_descricao_produto')

    return render(request, 'core/cadastro_descricao_produto.html', {
        'form': form,
        'page_obj': page_obj,
        'descricao': descricao,
        'tipo': tipo,
    })

@login_required
@require_POST
def cadastrar_descricao_produto_ajax(request):
    form = DescricaoProdutoForm(request.POST)
    if form.is_valid():
        nova_descricao = form.save()
        return JsonResponse({'success': True, 'id': nova_descricao.id, 'descricao': str(nova_descricao)})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})

@login_required
@require_POST
def cadastrar_tipo_preservacao_ajax(request):
    nome = request.POST.get('nome')
    if nome:
        novo_tipo = TipoPreservacao.objects.create(nome=nome)
        return JsonResponse({'success': True, 'id': novo_tipo.id, 'nome': novo_tipo.nome})
    else:
        return JsonResponse({'success': False, 'error': 'Nome não fornecido'})


@login_required
def cadastrar_localizacao(request):
    form = LocalizacaoForm(request.POST or None)
    setores = Setor.objects.all()  # Busca todos os setores cadastrados

    # Campos de busca
    local = request.GET.get('local', '')
    setor_busca = request.GET.get('setor', '')

    # Filtro com busca combinada
    localizacoes_list = Localizacao.objects.all()
    if local:
        localizacoes_list = localizacoes_list.filter(local__icontains=local)
    if setor_busca:
        localizacoes_list = localizacoes_list.filter(setor__nome__icontains=setor_busca)

    localizacoes_list = localizacoes_list.order_by('local')

    # Paginação
    paginator = Paginator(localizacoes_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if form.is_valid():
        form.save()
        return redirect('cadastrar_localizacao')  # Recarrega a tela com o formulário limpo

    return render(request, 'core/cadastro_localizacao.html', {
        'form': form,
        'setores': setores,  # Passando os setores para o template
        'page_obj': page_obj,  # Passando a paginação para o template
        'local': local,  # Passando o valor da busca por local
        'setor': setor_busca,  # Passando o valor da busca por setor
    })

@login_required
def cadastrar_setor(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = SetorForm(request.POST)
        if form.is_valid():
            setor = form.save()
            return JsonResponse({'success': True, 'id': setor.id, 'nome': setor.nome})
        else:
            return JsonResponse({'success': False, 'error': form.errors['nome'][0]}, status=400)
    else:
        form = SetorForm(request.POST or None)
        setores = Setor.objects.all().order_by('nome')
        return render(request, 'core/cadastro_setor.html', {
            'form': form,
            'setores': setores,
        })

def cadastrar_setor_ajax(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome do setor é obrigatório.'})

        if Setor.objects.filter(nome=nome).exists():
            return JsonResponse({'success': False, 'error': 'Setor já existe.'})

        setor = Setor.objects.create(nome=nome)
        return JsonResponse({'success': True, 'nome': setor.nome})

    return JsonResponse({'success': False, 'error': 'Requisição inválida.'})

@login_required
def load_localizacoes(request):
    setor_id = request.GET.get('setor_id')
    locais = Localizacao.objects.filter(setor_id=setor_id).order_by('local')
    locais_list = [{'id': local.id, 'local': local.local} for local in locais]
    return JsonResponse({'locais': locais_list})

def gerar_itens_inspecao(request, id):
    recebimento = get_object_or_404(Recebimento, id=id)

    if ItemInspecao.objects.filter(recebimento=recebimento).exists():
        messages.warning(request, 'Itens de inspeção já foram gerados para este recebimento.')
        return redirect('recebimentos_list')

    gerar_itens_inspecao_para_recebimento(recebimento)
    messages.success(request, 'Itens de inspeção gerados com sucesso.')
    return redirect('recebimentos_list')

