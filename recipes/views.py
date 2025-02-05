from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.core.files.storage import default_storage
from django.conf import settings
import os
import base64
from django.core.files.base import ContentFile
from django.core.paginator import Paginator


from .models import Comment, Rating, Favorite
from . import models
from .models import Recipe
from .forms import RecipeForm, CommentForm, RatingForm

# Create your views here.
def index(request):
    recipes = models.Recipe.objects.all()
    categories = models.Recipe.CATEGORIES  # Fixed this line

    # Set up pagination
    paginator = Paginator(recipes, 9)  # Show 10 recipes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "recipes/index.html", {'title': 'Home', 'categories': categories, 'recipes': page_obj})


class RecipeListView(ListView):
    model = models.Recipe
    template_name = 'recipes/index.html'
    context_object_name = 'recipes'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['categories'] = models.Recipe.CATEGORIES  # Fixed this line
        return context

    def get_queryset(self):
        # You can customize this queryset to filter or order recipes
        return models.Recipe.objects.all().order_by('-created_at')    
        

class RecipeBaseView(LoginRequiredMixin):
    print("Form validation started")
    model = Recipe
    fields = ['title', 'description', 'categories']

    def form_valid(self, form):
        # Ottieni i dati degli ingredienti
        ingredients = self.request.POST.getlist('ingredient[]')
        quantities = self.request.POST.getlist('quantity[]')
        units = self.request.POST.getlist('unit[]')
        form.instance.servings = self.request.POST.get('servings')  # Capture the value


        cropped_image_data = self.request.POST.get("cropped_image")
        if cropped_image_data:
            format, imgstr = cropped_image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(base64.b64decode(imgstr), name=f"recipe_image.{ext}")
            form.instance.img = image_data
            # Handle categories (this is automatically handled by Django when using MultiSelectField)
            selected_categories = self.request.POST.getlist('categories')  # Get selected categories from the form
            form.instance.categories = ",".join(selected_categories)  # Fix: assign selected categories as a string

        # Crea una lista degli ingredienti concatenando gli ingredienti, quantità e unità
        ingredients_list = [
            f"{ingredients[i]}-{quantities[i]}-{units[i]}" for i in range(len(ingredients))
        ]

        # Unisci gli ingredienti in una stringa separata da "; "
        form.instance.ingredients = "; ".join(ingredients_list)

        # Gestione dei passaggi
        step_descriptions = {
            int(k.strip("step_description[]")): v
            for k, v in self.request.POST.items() if k.startswith("step_description[")
        }

        # Raccogli le immagini con chiavi specifiche come step_image[3]
        step_images = {
            int(k.strip("step_image[]")): v
            for k, v in self.request.FILES.items() if k.startswith("step_image[")
        }

        default_image_url = os.path.join(settings.MEDIA_URL, 'images/no_image_available.png')

        steps = []
        for i in sorted(step_descriptions.keys()):  # Ordina per numero di step
            description = step_descriptions[i]

            if i in step_images:
                image = step_images[i]
                # Genera un nome unico per l'immagine
                image_name = f"step_{i}_{image.name}"
                # Salva l'immagine nella cartella media/recipes
                image_path = default_storage.save(f'recipes/{image_name}', image)
                # Ottieni il percorso relativo dell'immagine
                image_url = os.path.join(settings.MEDIA_URL, image_path)
            else:
                image_url = default_image_url  # Immagine predefinita se non presente

            # Aggiungi la descrizione e l'URL dell'immagine per ciascun passo
            steps.append(f"{description}|{image_url}")

        # Unisci tutti gli step in una stringa separata da ";"
        form.instance.steps = ";".join(steps)

        # Assegna l'autore alla ricetta (l'utente loggato)
        form.instance.author = self.request.user

        print("Step descriptions:", step_descriptions)
        print("Step images:", step_images)
        print("Steps:", steps)

        print("Form validation ended")
        if not self.request.user.is_authenticated:
            print("User is not authenticated before saving the form")
        return super().form_valid(form)




class RecipeCreateView(RecipeBaseView, CreateView):
    pass

class RecipeUpdateView(RecipeBaseView, UpdateView):
    template_name = 'recipes/recipe_form_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object  # Get the current recipe

        # Process Ingredients
        if recipe.ingredients:
            context['ingredient_list'] = [
                ingredient.split("-") for ingredient in recipe.ingredients.split("; ")
            ]
        else:
            context['ingredient_list'] = []

        # Process Steps
        if recipe.steps:
            context['step_list'] = [
                step.split("|") for step in recipe.steps.split(";")
            ]
        else:
            context['step_list'] = []

        return context

    def test_func(self):
        recipe = self.get_object()
        # Allow deletion if the user is the author or an admin
        return self.request.user == recipe.author or self.request.user.is_superuser


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = models.Recipe
    success_url = reverse_lazy('user-recipes')

    def test_func(self):
        recipe = self.get_object()
        # Allow deletion if the user is the author or an admin
        return self.request.user == recipe.author or self.request.user.is_superuser



def about(request):
    return render(request,"recipes/about.html",{'title':'about us page'})


@login_required
def toggle_favorite(request, recipe_id):
    # Get the recipe by id
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Check if the recipe is already in the user's favorites
    favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()

    if favorite:
        # If the recipe is already a favorite, remove it
        favorite.delete()
        action = 'remove'
    else:
        # If the recipe is not a favorite, add it
        Favorite.objects.create(user=request.user, recipe=recipe)
        action = 'add'

    # Return the action result (add or remove)
    return JsonResponse({'action': action})

def search_results(request):
    query = request.GET.get('query')

    recipes = models.Recipe.objects.filter(
        Q(title__icontains=query) | Q(author__username__icontains=query) | Q(description__icontains=query)
    )
    context = {
        'query': query,
        'recipes': recipes,
    }
    return render(request, 'recipes/search_results.html', context)


@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    content = request.POST.get('content')
    comment = Comment(recipe=recipe, author=request.user, content=content)
    comment.save()
    return redirect('recipes-detail', pk=recipe_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.author == request.user or comment.recipe.author == request.user:
        recipe_id = comment.recipe.id
        comment.delete()
        return redirect('recipes-detail', pk=recipe_id)
    else:
        return HttpResponseForbidden()

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)

    return redirect('recipes-detail', pk=comment.recipe.id)



class RecipeDetailView(DetailView):
    model = models.Recipe
    template_name = 'recipes/recipe_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get the user rating
            rating = Rating.objects.filter(recipe=self.object, user=self.request.user).first()
            context['user_rating'] = rating.rating if rating else None

            # Get the user's favorite for the recipe
            favorite = Favorite.objects.filter(user=self.request.user, recipe=self.object).first()
            context['favorite'] = favorite

        # Split ingredients: first by "; ", then by "-" (ingredient, quantity, unit)
        if self.object.ingredients:
            context['ingredients'] = [
                ingredient.split('-') for ingredient in self.object.ingredients.split('; ')
            ]
        else:
            context['ingredients'] = []

        # Process steps: split by ";" and then by "|"
        if self.object.steps:
            context['steps'] = [
                step.split('|') for step in self.object.steps.split(';')
            ]
        else:
            context['steps'] = []
            
        context['servings'] = self.object.servings
        context['categories'] = list(self.object.categories) if self.object.categories else []

        return context








@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    rating_value = int(request.POST.get('rating'))

    # Update existing rating or create a new one
    rating, created = Rating.objects.update_or_create(recipe=recipe, user=request.user, defaults={'rating': rating_value})

    if created:
        message = 'Rating added successfully.'
    else:
        message = 'Rating updated successfully.'

    return redirect(request.META.get('HTTP_REFERER'))