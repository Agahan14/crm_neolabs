# Generated by Django 4.1.5 on 2023-04-17 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0015_merge_20230417_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='reason_description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='historicalapplication',
            name='reason_description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
