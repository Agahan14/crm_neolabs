# Generated by Django 4.1.5 on 2023-04-22 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notifcation_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifcation',
            name='phone',
            field=models.CharField(max_length=55, null=True),
        ),
    ]
