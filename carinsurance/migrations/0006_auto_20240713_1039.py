# Generated by Django 2.1 on 2024-07-13 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carinsurance', '0005_carpolicy_amount_claimed'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarDefect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('severity', models.CharField(choices=[('Low', 'Low'), ('Moderate', 'Moderate'), ('Severe', 'Severe')], default='Moderate', max_length=100)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defects', to='carinsurance.Car')),
            ],
        ),
        migrations.AlterField(
            model_name='claim',
            name='damage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carinsurance.CarDefect'),
        ),
    ]
