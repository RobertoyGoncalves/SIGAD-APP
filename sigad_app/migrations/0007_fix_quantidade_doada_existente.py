"""
Corrige quantidade_doada para itens existentes:
quantidade_doada = quantidade_atual + total_ja_distribuido
"""

from django.db import migrations


def fix_quantidade_doada(apps, schema_editor):
    ItemEstoque = apps.get_model('sigad_app', 'ItemEstoque')
    LinhaDistribuicao = apps.get_model('sigad_app', 'LinhaDistribuicao')

    from django.db.models import Sum

    for item in ItemEstoque.objects.all():
        total_distribuido = (
            LinhaDistribuicao.objects
            .filter(item_estoque=item)
            .aggregate(total=Sum('quantidade'))['total'] or 0
        )
        item.quantidade_doada = item.quantidade + total_distribuido
        item.save(update_fields=['quantidade_doada'])


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0006_add_quantidade_doada_itemestoque'),
    ]

    operations = [
        migrations.RunPython(fix_quantidade_doada, reverse_code=migrations.RunPython.noop),
    ]
