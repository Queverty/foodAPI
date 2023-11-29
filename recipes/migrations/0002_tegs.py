# Generated by Django 4.2.7 on 2023-11-18 03:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tegs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('hex_color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator('^#[A-Fa-f0-9]{6}$')], verbose_name='Цветовой HEX-код')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
    ]
