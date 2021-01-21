from django.urls import path
from .views import *


urlpatterns = [
    path('', quiver_editor, name='quiver_editor'),
]

