from django import forms
from .models import Recipe, Comment, Rating

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'img', 'categories', 'ingredients','servings', 'steps']

    def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients')
        return ingredients if ingredients else ''

    def clean_steps(self):
        steps = self.cleaned_data.get('steps')
        return steps if steps else ''

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
