# Generated by Django 2.1.3 on 2018-12-27 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0018_auto_20181228_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to='ecommerce.User'),
        ),
    ]
