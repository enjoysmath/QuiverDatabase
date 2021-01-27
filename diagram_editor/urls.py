from django.urls import path
from .views import *


urlpatterns = [
    path('create-new', create_new_diagram, name='create_new_diagram'),  # BUGFIX, this needs to come first!
    path('<str:diagram_id>', quiver_editor, name='diagram_editor'),
    path('viewer/<str:diagram_id>', quiver_viewer, name='diagram_viewer'),
    path('result/<str:diagram_id>', diagram_result_view, name='diagram_result_view')
]

