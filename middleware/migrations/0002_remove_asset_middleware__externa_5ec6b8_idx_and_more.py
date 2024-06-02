# Generated by Django 5.0.6 on 2024-06-02 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('middleware', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='asset',
            name='middleware__externa_5ec6b8_idx',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='external_id',
            new_name='id',
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['id', 'ip_address'], name='middleware__id_ab89f2_idx'),
        ),
    ]
