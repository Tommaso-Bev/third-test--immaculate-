from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from recipes.models import Recipe
from . import models 
from . import forms

# Create your views here.
def register(request):
    if request.method=="POST":
        form=forms.UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request, f"{username}, you're account has been created!, please login ")
            return redirect('user-login')
    else:    
        form = forms.UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required()
def profile(request):
    user = request.user
    following = user.following.all()
    followers = user.followers.all()
    context = {
        'user': user,
        'following': following,
        'followers': followers,
        'title': 'My Profile'
    }
    return render(request, 'users/profile.html', context)

def favorites(request):
    return render(request, 'users/favorites.html',{'title':'Favorites'})

def my_recipes(request):
    recipes = Recipe.objects.filter(author=request.user)
    context = {
        'recipes': recipes
    }
    
    return render(request, 'users/my-recipes.html', context)         #TODO change name 

@login_required
def toggle_follow(request, user_id):
    user_to_follow = models.UserProfile.objects.get(pk=user_id)
    if request.user in user_to_follow.followers.all():
        user_to_follow.followers.remove(request.user)
        action = 'unfollow'
    else:
        user_to_follow.followers.add(request.user)
        action = 'follow'
    user_to_follow.save()  # Save the changes to the user_to_follow object    
    return redirect(request.META.get('HTTP_REFERER'))