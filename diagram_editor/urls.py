from django.urls import path
from .views import *


urlpatterns = [
    path('create-new', create_new_diagram, name='create_new_diagram'),  # BUGFIX, this needs to come first!
    path('<str:diagram_id>', quiver_editor, name='diagram_editor'),
    path('close-editor/<str:diagram_id>', close_editor, name='close_diagram_editor'),
]

