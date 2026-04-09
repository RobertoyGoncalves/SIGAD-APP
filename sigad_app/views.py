from datetime import date
from django.shortcuts import render


def sidebar_items():
    return [
        {'label': 'Dashboard', 'url_name': 'dashboard', 'icon': 'layout-dashboard'},
        {'label': 'Registrar Item', 'url_name': 'registrar_item', 'icon': 'package-plus'},
        {'label': 'Registrar Distribuição', 'url_name': 'registrar_distribuicao', 'icon': 'arrow-right-left'},
        {'label': 'Estoque', 'url_name': 'estoque', 'icon': 'boxes'},
        {'label': 'Beneficiários', 'url_name': 'beneficiarios', 'icon': 'users'},
        {'label': 'Relatórios', 'url_name': 'relatorios', 'icon': 'bar-chart-3'},
    ]


def base_context(active):
    return {
        'sidebar_items': sidebar_items(),
        'active_page': active,
    }


def dashboard(request):
    context = base_context('dashboard')
    context.update({
        'cards': [
            {'title': 'Total em Estoque', 'value': '1.247', 'delta': '+12.5%', 'icon': 'package', 'tone': 'blue'},
            {'title': 'Beneficiários Ativos', 'value': '342', 'delta': '+8.2%', 'icon': 'users', 'tone': 'green'},
            {'title': 'Distribuições (mês)', 'value': '156', 'delta': '+15.3%', 'icon': 'trending-up', 'tone': 'purple'},
            {'title': 'Itens Vencendo', 'value': '23', 'delta': 'Próximos 7 dias', 'icon': 'alert-circle', 'tone': 'orange'},
        ],
        'atividades': [
            {'titulo': 'Doação recebida', 'descricao': 'Arroz 5kg • João Silva', 'tempo': 'há 5 min'},
            {'titulo': 'Distribuição realizada', 'descricao': 'Feijão 1kg • undefined • Maria Santos', 'tempo': 'há 12 min'},
            {'titulo': 'Novo beneficiário', 'descricao': 'Carlos Oliveira', 'tempo': 'há 1 hora'},
            {'titulo': 'Doação recebida', 'descricao': 'Sabonete 90g • Empresa XYZ', 'tempo': 'há 2 horas'},
        ]
    })
    return render(request, 'sigad_app/dashboard.html', context)


def registrar_item(request):
    context = base_context('registrar_item')
    context['categorias'] = ['Selecione uma categoria', 'Alimentos', 'Higiene', 'Roupas']
    context['unidades'] = ['Selecione', 'pacote', 'unidade', 'litro', 'kg']
    return render(request, 'sigad_app/registrar_item.html', context)


def registrar_distribuicao(request):
    context = base_context('registrar_distribuicao')
    context['beneficiarios'] = ['Selecione um beneficiário', 'Maria Santos', 'João Silva', 'Carlos Oliveira', 'Ana Paula Costa']
    context['itens'] = ['Buscar item no estoque...', 'Arroz Branco 5kg', 'Feijão Preto 1kg', 'Sabonete 90g', 'Camiseta Tamanho M']
    return render(request, 'sigad_app/registrar_distribuicao.html', context)


def estoque(request):
    context = base_context('estoque')
    context['itens_estoque'] = [
        {'nome': 'Arroz Branco 5kg', 'categoria': 'Alimentos', 'quantidade': 150, 'unidade': 'pacote', 'validade': '14/08/2026', 'doador': 'João Silva', 'badge': 'green'},
        {'nome': 'Feijão Preto 1kg', 'categoria': 'Alimentos', 'quantidade': 95, 'unidade': 'pacote', 'validade': '19/10/2026', 'doador': 'Maria Santos', 'badge': 'green'},
        {'nome': 'Sabonete 90g', 'categoria': 'Higiene', 'quantidade': 230, 'unidade': 'unidade', 'validade': '09/03/2027', 'doador': 'Empresa XYZ', 'badge': 'blue'},
        {'nome': 'Camiseta Tamanho M', 'categoria': 'Roupas', 'quantidade': 45, 'unidade': 'unidade', 'validade': '-', 'doador': 'Doação Anônima', 'badge': 'purple'},
        {'nome': 'Óleo de Soja 900ml', 'categoria': 'Alimentos', 'quantidade': 78, 'unidade': 'litro', 'validade': '29/06/2026', 'doador': 'Carlos Oliveira', 'badge': 'green'},
        {'nome': 'Shampoo 350ml', 'categoria': 'Higiene', 'quantidade': 62, 'unidade': 'unidade', 'validade': '14/01/2027', 'doador': 'Ana Costa', 'badge': 'blue'},
    ]
    context['total_estoque'] = 660
    return render(request, 'sigad_app/estoque.html', context)


def beneficiarios(request):
    context = base_context('beneficiarios')
    context['beneficiarios_cards'] = [
        {'nome': 'Maria Santos', 'cpf': '123.456.789-00', 'telefone': '(11) 98765-4321', 'email': 'maria.santos@email.com', 'endereco': 'Rua das Flores, 123 - São Paulo, SP', 'ultima_distribuicao': '27/03/2026'},
        {'nome': 'João Silva', 'cpf': '987.654.321-00', 'telefone': '(11) 91234-5678', 'email': 'joao.silva@email.com', 'endereco': 'Av. Paulista, 456 - São Paulo, SP', 'ultima_distribuicao': '24/03/2026'},
        {'nome': 'Carlos Oliveira', 'cpf': '456.789.123-00', 'telefone': '(11) 92345-6789', 'email': 'carlos.oliveira@email.com', 'endereco': 'Rua da Esperança, 789 - São Paulo, SP', 'ultima_distribuicao': '20/03/2026'},
        {'nome': 'Ana Paula Costa', 'cpf': '321.654.987-00', 'telefone': '(11) 93456-7890', 'email': 'ana.costa@email.com', 'endereco': 'Rua do Comércio, 321 - São Paulo, SP', 'ultima_distribuicao': '18/03/2026'},
    ]
    return render(request, 'sigad_app/beneficiarios.html', context)


def relatorios(request):
    context = base_context('relatorios')
    context['today'] = date.today().strftime('%d/%m/%Y')
    return render(request, 'sigad_app/relatorios.html', context)
