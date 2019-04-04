# Generated by Django 2.1.3 on 2018-12-25 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0013_auto_20181226_0040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcart',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='shoppingCustomer', serialize=False, to='ecommerce.User'),
        ),
    ]