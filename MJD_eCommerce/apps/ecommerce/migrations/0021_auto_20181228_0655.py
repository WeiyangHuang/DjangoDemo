# Generated by Django 2.1.3 on 2018-12-27 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0020_remove_confirmation_buyerphone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='comfirmNumber',
            field=models.CharField(max_length=255),
        ),
    ]
