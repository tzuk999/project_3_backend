# Generated by Django 4.2.5 on 2023-09-12 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_product_category_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.URLField(),
        ),
    ]
