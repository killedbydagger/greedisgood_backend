# Generated by Django 3.1.1 on 2020-09-19 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0004_game_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Probability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rarity', models.IntegerField()),
                ('chance', models.IntegerField()),
            ],
            options={
                'db_table': 'probability',
            },
        ),
    ]
