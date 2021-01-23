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
from accounts.views import user_signup

urlpatterns = [
    path('diagram/', include('diagram_editor.urls')),
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('db/', include('database_service.urls')),
    path('rules/', include('rules.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("accounts/signup/", user_signup, name="signup"),
    path('error/<str:msg>/<int:line>/<str:file>', error, name='error'),
    path('quiver-editor/', include('diagram_editor.urls'))
]

urlpatterns += staticfiles_urlpatterns()