from django.db import models


class Beneficiario(models.Model):
    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=14)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    endereco = models.CharField(max_length=255)
    ultima_distribuicao = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome


class ItemEstoque(models.Model):
    CATEGORIAS = [
        ('Alimentos', 'Alimentos'),
        ('Higiene', 'Higiene'),
        ('Roupas', 'Roupas'),
    ]

    nome = models.CharField(max_length=120)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    quantidade = models.PositiveIntegerField()
    unidade = models.CharField(max_length=30)
    validade = models.DateField(null=True, blank=True)
    doador = models.CharField(max_length=120)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return self.nome
