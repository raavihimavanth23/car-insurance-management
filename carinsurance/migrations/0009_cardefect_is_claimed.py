# Generated by Django 2.1 on 2024-07-13 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carinsurance', '0008_cardefect_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardefect',
            name='is_claimed',
            field=models.BooleanField(default=False),
        ),
    ]
