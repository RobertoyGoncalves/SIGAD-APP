"""
Testes de contagem de queries (Req 5 — ajuste fino).

Usa CaptureQueriesContext para medir queries reais por request em
BeneficiadoDetail e DistribuicaoDetail após mover prefetch para get_queryset().
"""
from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from sigad_app.models import (
    Beneficiado,
    Distribuicao,
    Doador,
    ItemEstoque,
    LinhaDistribuicao,
)


class QueryCountBeneficiadoDetailTest(TestCase):
    """BeneficiadoDetail: verificar contagem de queries após ajuste fino."""

    def setUp(self):
        self.user = User.objects.create_user('op1', password='pass123')
        self.client.login(username='op1', password='pass123')

        doador = Doador.objects.create(nome='Doador QC', usuario=self.user)
        item1 = ItemEstoque.objects.create(
            nome='Arroz', categoria='Alimentos', quantidade=10,
            unidade='kg', usuario=self.user, doador=doador,
        )
        item2 = ItemEstoque.objects.create(
            nome='Feijão', categoria='Alimentos', quantidade=5,
            unidade='kg', usuario=self.user, doador=doador,
        )
        self.beneficiado = Beneficiado.objects.create(
            nome='Beneficiado QC', cpf='000.000.000-00',
            telefone='(00) 00000-0000', email='b@test.com',
            endereco='Rua Teste 1', usuario=self.user,
        )
        dist1 = Distribuicao.objects.create(
            beneficiado=self.beneficiado, usuario=self.user
        )
        dist2 = Distribuicao.objects.create(
            beneficiado=self.beneficiado, usuario=self.user
        )
        LinhaDistribuicao.objects.create(
            distribuicao=dist1, item_estoque=item1, quantidade=2
        )
        LinhaDistribuicao.objects.create(
            distribuicao=dist1, item_estoque=item2, quantidade=1
        )
        LinhaDistribuicao.objects.create(
            distribuicao=dist2, item_estoque=item1, quantidade=3
        )

    def test_query_count(self):
        url = f'/ver/beneficiado/{self.beneficiado.pk}/'
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        total = len(ctx.captured_queries)
        # imprime para o resumo do PR
        print(f'\nBeneficiadoDetail — queries totais: {total}')
        for i, q in enumerate(ctx.captured_queries, 1):
            sql = q['sql'][:120].replace('\n', ' ')
            print(f'  {i:2d}: {sql}')
        # limite superior conservador: sessão(2) + user(1) + objeto(1)
        # + prefetch distribuicoes(1) + prefetch linhas+item(1) = 6
        self.assertLessEqual(total, 6, f'Esperado ≤6 queries, obtido {total}')


class QueryCountDistribuicaoDetailTest(TestCase):
    """DistribuicaoDetail: verificar contagem de queries após ajuste fino."""

    def setUp(self):
        self.user = User.objects.create_user('op2', password='pass123')
        self.client.login(username='op2', password='pass123')

        doador = Doador.objects.create(nome='Doador QC2', usuario=self.user)
        item1 = ItemEstoque.objects.create(
            nome='Sabão', categoria='Limpeza', quantidade=20,
            unidade='un', usuario=self.user, doador=doador,
        )
        item2 = ItemEstoque.objects.create(
            nome='Shampoo', categoria='Higiene', quantidade=15,
            unidade='un', usuario=self.user, doador=doador,
        )
        benef = Beneficiado.objects.create(
            nome='Beneficiado QC2', cpf='111.111.111-11',
            telefone='(11) 11111-1111', email='c@test.com',
            endereco='Rua Teste 2', usuario=self.user,
        )
        self.dist = Distribuicao.objects.create(
            beneficiado=benef, usuario=self.user
        )
        LinhaDistribuicao.objects.create(
            distribuicao=self.dist, item_estoque=item1, quantidade=5
        )
        LinhaDistribuicao.objects.create(
            distribuicao=self.dist, item_estoque=item2, quantidade=3
        )

    def test_query_count(self):
        url = f'/ver/distribuicao/{self.dist.pk}/'
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        total = len(ctx.captured_queries)
        print(f'\nDistribuicaoDetail — queries totais: {total}')
        for i, q in enumerate(ctx.captured_queries, 1):
            sql = q['sql'][:120].replace('\n', ' ')
            print(f'  {i:2d}: {sql}')
        # sessão(2) + user(1) + objeto com select_related beneficiado(1)
        # + prefetch linhas+item_estoque(1) = 5
        self.assertLessEqual(total, 5, f'Esperado ≤5 queries, obtido {total}')


class GroupAccessRegistrarItemTest(TestCase):
    """Req 2 (Ajuste 1) — registrar_item requer grupo Gestores ou Operadores."""

    def setUp(self):
        from django.contrib.auth.models import Group
        self.grupo_op = Group.objects.get_or_create(name='Operadores')[0]
        self.grupo_gest = Group.objects.get_or_create(name='Gestores')[0]

        self.user_sem_grupo = User.objects.create_user('semgrupo', password='pass')
        self.user_operador = User.objects.create_user('operador', password='pass')
        self.user_operador.groups.add(self.grupo_op)
        self.user_gestor = User.objects.create_user('gestor', password='pass')
        self.user_gestor.groups.add(self.grupo_gest)
        self.superuser = User.objects.create_superuser('admin2', password='pass')

    def _login(self, user):
        self.client.logout()
        self.client.login(username=user.username, password='pass')

    def test_sem_grupo_nao_acessa(self):
        self._login(self.user_sem_grupo)
        r = self.client.get('/registrar-item/')
        # user_passes_test falhou: redireciona para login
        self.assertNotEqual(r.status_code, 200)

    def test_operador_acessa(self):
        self._login(self.user_operador)
        r = self.client.get('/registrar-item/')
        self.assertEqual(r.status_code, 200)

    def test_gestor_acessa(self):
        self._login(self.user_gestor)
        r = self.client.get('/registrar-item/')
        self.assertEqual(r.status_code, 200)

    def test_superuser_acessa(self):
        self._login(self.superuser)
        r = self.client.get('/registrar-item/')
        self.assertEqual(r.status_code, 200)
