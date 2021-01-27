"""QuiverDatabase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import home, error
from accounts.views import signup_view, login_view, logout_view, user_profile

#from accounts.views import user_signup

urlpatterns = [
    path('diagram/', include('diagram_editor.urls')),    
    path('', home, name='home'),
    path('profile', user_profile, name='profile'),
    path('sign-up', signup_view,
         {'next': 'profile'}, name='create_user'),
    
    path('sign-in', login_view, 
         {'next': 'profile'}, name='login'),
    
    path('sign-out', logout_view, 
         {'next': 'home'}, name='logout'),
    
    path('password-reset/', include('password_reset.urls')),
    path('admin/', admin.site.urls),
    path('database/', include('database_service.urls')),
    path('rules/', include('rules.urls')),
    path('error/<str:msg>', error, name='error'),
]

urlpatterns += staticfiles_urlpatterns()