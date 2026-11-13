from django.conf import settings
from django.db import migrations


def criar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=settings.GRUPO_COORDENADORES)
    Group.objects.get_or_create(name=settings.GRUPO_PROFESSORES)


def remover_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=[settings.GRUPO_COORDENADORES, settings.GRUPO_PROFESSORES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('commex', '0004_repositorio_branch_principal'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(criar_grupos, remover_grupos),
    ]
