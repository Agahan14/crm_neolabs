# Generated by Django 4.1.5 on 2023-04-22 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0021_remove_application_note_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='direction',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='rejectionreason',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
