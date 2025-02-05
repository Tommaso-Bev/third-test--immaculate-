"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path
from django.views.static import serve

from django.contrib import admin
from django.urls import path,include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",include("recipes.urls")),
    path('register/', user_views.register, name="user-register"),
    path('login/', auth_views.LoginView.as_view(template_name="users/login.html"), name="user-login"),
    path('logout/', auth_views.LogoutView.as_view(), name="user-logout"),
    path('profile/', user_views.profile, name="user-profile"),
    path('my-recipes/', user_views.my_recipes, name="user-recipes"),
    path('favorites/', user_views.favorites, name="user-favorites"),
    path('toggle-follow/<int:user_id>/', user_views.toggle_follow, name='toggle-follow'),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)