# Generated by Django 4.2.7 on 2024-05-07 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booths", "0004_alter_booth_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menu",
            name="is_soldout",
            field=models.BooleanField(default=True),
        ),
    ]
