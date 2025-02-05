from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField

User = get_user_model()


# Create your models here.
class Recipe(models.Model):
    CATEGORIES = [
        ('Americano', 'Americano'),
        ('Fast-food', 'Fast-food'),
        ('Hamburger', 'Hamburger'),
        ('Asiatico', 'Asiatico'),
        ('Barbecue', 'Barbecue'),
        ('Bevande', 'Bevande'),
        ('Carne', 'Carne'),
        ('Cinese', 'Cinese'),
        ('Colazione', 'Colazione'),
        ('Dessert', 'Dessert'),
        ('Dolci', 'Dolci'),
        ('Frutti di mare', 'Frutti di mare'),
        ('Gelato', 'Gelato'),
        ('Giapponese', 'Giapponese'),
        ('Gourmet', 'Gourmet'),
        ('Greco', 'Greco'),
        ('Indiano', 'Indiano'),
        ('Insalate', 'Insalate'),
        ('Internazionale', 'Internazionale'),
        ('Italiano', 'Italiano'),
        ('Kebab', 'Kebab'),
        ('Latino-americano', 'Latino-americano'),
        ('Libanese', 'Libanese'),
        ('Local food', 'Local food'),
        ('Mediterraneo', 'Mediterraneo'),
        ('Mercati locali', 'Mercati locali'),
        ('Messicano', 'Messicano'),
        ('Panificio e pasticceria', 'Panificio e pasticceria'),
        ('Panini', 'Panini'),
        ('Pasta', 'Pasta'),
        ('Pesce', 'Pesce'),
        ('Piadina', 'Piadina'),
        ('Pizza', 'Pizza'),
        ('Poke', 'Poke'),
        ('Pollo', 'Pollo'),
        ('Sano', 'Sano'),
        ('Senza glutine', 'Senza glutine'),
        ('Snack', 'Snack'),
        ('Sushi', 'Sushi'),
        ('Tè e caffè', 'Tè e caffè'),
        ('Thailandese', 'Thailandese'),
        ('Vegano', 'Vegano'),
        ('Vegetariano', 'Vegetariano'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    img = models.ImageField(upload_to="recipes/", blank=False, null=False)
    ingredients = models.TextField(blank=False, default='')    
    steps = models.TextField(blank=True, default='')  # Nuovo campo per i passaggi
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    servings = models.IntegerField(default=1)  


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Usa MultiSelectField per le categorie selezionabili
    categories = MultiSelectField(choices=CATEGORIES, max_length=255, default='Americano')

    def get_absolute_url(self):
        return reverse('recipes-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
    
    def average_rating(self):
        ratings = Rating.objects.filter(recipe=self)
        if ratings.exists():
            total_ratings = ratings.count()
            sum_ratings = ratings.aggregate(models.Sum('rating'))['rating__sum']
            average = sum_ratings / total_ratings
            return round(average, 1)
        else:
            return None


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} likes {self.recipe.title}"    

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments')

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"    
    
class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"Rating {self.rating} by {self.user.username} on {self.recipe.title}"    