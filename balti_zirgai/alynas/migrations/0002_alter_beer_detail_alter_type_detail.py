# Generated by Django 4.2.6 on 2023-10-18 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alynas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beer',
            name='detail',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='type',
            name='detail',
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
