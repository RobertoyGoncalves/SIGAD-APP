from django.db import models


class Beneficiado(models.Model):
    """Quem RECEBE itens na distribuição."""

    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=14)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    endereco = models.CharField(max_length=255)
    ultima_distribuicao = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Beneficiado'
        verbose_name_plural = 'Beneficiados'

    def __str__(self):
        return self.nome


class Beneficiario(models.Model):
    """Quem DOA itens ao estoque."""

    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=14, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Beneficiário'
        verbose_name_plural = 'Beneficiários'

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
    quantidade_doada = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade doada (original)',
        help_text='Quantidade registrada no momento da doação — nunca alterada.',
    )
    unidade = models.CharField(max_length=30)
    validade = models.DateField(null=True, blank=True)
    beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_doados',
        verbose_name='Beneficiário (quem doou)',
    )
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome


class Distribuicao(models.Model):
    beneficiado = models.ForeignKey(
        Beneficiado,
        on_delete=models.PROTECT,
        related_name='distribuicoes',
        verbose_name='Beneficiado (quem recebeu)',
    )
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registrado_em']

    def __str__(self):
        return f'Distribuição #{self.pk} — {self.beneficiado.nome}'


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
