# Generated by Django 3.2.3 on 2021-07-05 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_alter_product_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.JSONField(default=[]),
        ),
    ]
