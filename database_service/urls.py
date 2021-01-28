from django.urls import path
from .views import *


urlpatterns = [
    path('set-model-name/<str:Model>', set_model_name, name='set_model_name'),
    path('save-diagram/<str:diagram_id>', save_diagram_to_database, name='save_diagram'),
    path('load-diagram/<str:diagram_id>', load_diagram_from_database, name='load_diagram'),
    path('open-diagrams', list_open_diagrams, name='open_diagrams'),
    path('all-diagrams', list_all_diagrams, name='all_diagrams')
]

