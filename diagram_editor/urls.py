from django.urls import path
from .views import *

urlpatterns = [
    path('editor/<int:id>', diagram_editor, name='diagram_editor'),
]

