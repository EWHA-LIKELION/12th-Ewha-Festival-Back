# Generated by Django 4.2.7 on 2024-05-07 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booths", "0003_alter_booth_category_alter_booth_contact_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booth",
            name="updated_at",
            field=models.DateTimeField(),
        ),
    ]
