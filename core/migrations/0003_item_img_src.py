# Generated by Django 2.2.13 on 2022-02-25 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20220225_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='img_src',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]
