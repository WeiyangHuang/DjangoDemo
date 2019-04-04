# Generated by Django 2.1.3 on 2018-12-20 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0004_productdetail_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productcategory',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productdetail',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ProductCategory',
        ),
    ]