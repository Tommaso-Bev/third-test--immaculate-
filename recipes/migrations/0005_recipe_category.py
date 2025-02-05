# Generated by Django 4.2.1 on 2023-06-04 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0004_rating"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="category",
            field=models.CharField(
                choices=[
                    ("first", "First"),
                    ("second", "Second"),
                    ("side", "Side"),
                    ("dessert", "Dessert"),
                ],
                default="Uncategorized",
                max_length=20,
            ),
        ),
    ]
