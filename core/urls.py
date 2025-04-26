#urls
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import (home_view, relatorio_view,
    recebimento_view, cadastrar_funcionario,
    cadastrar_fornecedor, cadastrar_transportadora,
    cadastrar_tipo_produto, cadastrar_descricao_produto,
    cadastrar_localizacao, ItemAutocomplete
)


urlpatterns = [
    path('recebimento/', views.recebimento_view, name='recebimento'),
    path('recebimentos/lista/', views.recebimentos_list, name='recebimentos_list'),
    path('recebimento/<int:id>/', views.recebimento_detail, name='recebimento_detail'),
    path('recebimento/<int:id>/editar/', views.recebimento_edit, name='recebimento_edit'),
    path('recebimento/editar/<int:id>/anexo/excluir/<int:anexo_id>/', views.excluir_anexo_recebimento, name='excluir_anexo_recebimento'),
    path('recebimento/<int:id>/gerar-itens/', views.gerar_itens_inspecao, name='gerar_itens_inspecao'),
    path('inspecao/', views.inspecao_view, name='inspecao'),
    path('inspecao/<int:id>/', views.inspecao_detail, name='inspecao_detail'),
    path('movimentacoes/', views.movimentacao_list, name='movimentacao_list'),
    path('movimentacao/criar/', views.movimentacao_create, name='movimentacao_create'),
    path('movimentacao/<int:id>/', views.movimentacao_detail, name='movimentacao_detail'),
    path('movimentacao/editar/<int:id>/', views.movimentacao_detail, name='movimentacao_edit'),
    path('preservacao/', views.preservacao_view, name='preservacao'),
    path('preservacoes/lista/', views.preservacao_list, name='preservacao_list'),
    path('solicitacao/', views.solicitacao_view, name='solicitacao'),
    path('solicitacoes/lista/', views.solicitacao_list, name='solicitacao_list'),
    path('', views.home_view, name='home'),
    path('relatorio/', views.relatorio_view, name='relatorio'),
    path('anexos/', views.anexos_view, name='anexos'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('funcionarios/novo/', cadastrar_funcionario, name='cadastrar_funcionario'),
    path('fornecedores/novo/', cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('transportadoras/novo/', cadastrar_transportadora, name='cadastrar_transportadora'),
    path('tipos-produto/novo/', cadastrar_tipo_produto, name='cadastrar_tipo_produto'),
    path('descricoes/novo/', cadastrar_descricao_produto, name='cadastrar_descricao_produto'),
    path('cadastrar/descricao/ajax/', views.cadastrar_descricao_produto_ajax, name='cadastrar_descricao_produto_ajax'),
    path('cadastrar-tipo-preservacao-ajax/', views.cadastrar_tipo_preservacao_ajax, name='cadastrar_tipo_preservacao_ajax'),
    path('setores/novo/', views.cadastrar_setor, name='cadastrar_setor'),
    path('cadastrar/setor/ajax/', views.cadastrar_setor_ajax, name='cadastrar_setor_ajax'),
    path('ajax/load-localizacoes/', views.load_localizacoes, name='ajax_load_localizacoes'),
    path('localizacoes/novo/', cadastrar_localizacao, name='cadastrar_localizacao'),
    path('select2/', include('django_select2.urls')),
    path('autocomplete/item/', ItemAutocomplete.as_view(), name='autocomplete_item'),
]
