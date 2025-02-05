# Generated by Django 4.2.1 on 2025-01-31 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0008_ingredient_alter_recipe_img_recipe_ingredients"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="img",
            field=models.ImageField(upload_to="recipes/"),
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="ingredients",
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.TextField(default="pippo coca"),
        ),
    ]
