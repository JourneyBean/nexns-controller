# Generated by Django 5.0 on 2024-01-15 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('variable', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='val',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='variable',
            name='text',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
