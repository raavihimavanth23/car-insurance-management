# Generated by Django 2.2 on 2024-07-26 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='image_src',
            field=models.CharField(blank=True, max_length=1024),
        ),
    ]
