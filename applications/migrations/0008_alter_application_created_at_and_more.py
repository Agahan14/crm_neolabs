# Generated by Django 4.1.5 on 2023-03-19 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0007_alter_application_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
