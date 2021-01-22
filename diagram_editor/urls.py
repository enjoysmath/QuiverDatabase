from django.urls import path
from .views import *


urlpatterns = [
    path('<str:diagram_id>', quiver_editor, name='diagram_editor'),
]

