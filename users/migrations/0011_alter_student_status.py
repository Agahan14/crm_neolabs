# Generated by Django 4.1.5 on 2023-04-15 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Клиент'), (1, 'Обучается'), (2, 'Закончил'), (3, 'Прервал обучение')], default=0),
        ),
    ]
