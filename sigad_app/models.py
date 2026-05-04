from django.db import models


class Beneficiario(models.Model):
    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=14)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    endereco = models.CharField(max_length=255)
    ultima_distribuicao = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome


class ItemEstoque(models.Model):
    CATEGORIAS = [
        ('Alimentos', 'Alimentos'),
        ('Higiene', 'Higiene'),
        ('Roupas', 'Roupas'),
        ('Limpeza', 'Limpeza'),
        ('Outros', 'Outros'),
    ]

    nome = models.CharField(max_length=120)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    quantidade = models.PositiveIntegerField()
    unidade = models.CharField(max_length=30)
    validade = models.DateField(null=True, blank=True)
    doador = models.CharField(max_length=120)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome


class Distribuicao(models.Model):
    beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.PROTECT,
        related_name='distribuicoes',
    )
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registrado_em']

    def __str__(self):
        return f'Distribuição #{self.pk} — {self.beneficiario.nome}'


class LinhaDistribuicao(models.Model):
    distribuicao = models.ForeignKey(
        Distribuicao,
        on_delete=models.CASCADE,
        related_name='linhas',
    )
    item_estoque = models.ForeignKey(
        ItemEstoque,
        on_delete=models.PROTECT,
        related_name='linhas_distribuicao',
    )
    quantidade = models.PositiveIntegerField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.quantidade}x {self.item_estoque.nome}'
