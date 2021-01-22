from django.urls import path
from .views import *

urlpatterns = [
    #path('editor/<str:diagram_id>', diagram_editor, name='diagram_editor'),
    path('create-new-diagram', create_new_diagram, name='create_new_diagram'),
]

