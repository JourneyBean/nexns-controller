# Generated by Django 5.0 on 2024-01-17 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recorddata',
            name='data',
            field=models.CharField(blank=True, max_length=65536),
        ),
        migrations.RenameField(
            model_name='recorddata',
            old_name='data',
            new_name='text'
        ),
        migrations.AddField(
            model_name='recorddata',
            name='val',
            field=models.CharField(blank=True, max_length=65536, null=True),
        ),
    ]
