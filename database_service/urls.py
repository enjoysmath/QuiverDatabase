from django.urls import path
from .views import *


urlpatterns = [
    path('set-category', set_diagram_category, name='set_diagram_category'),    
    path('set-model-string/<str:Model>/<str:field>', set_model_string, name='set_model_string'),
    path('save-diagram/<str:diagram_id>', save_diagram_to_database, name='save_diagram'),
    path('load-diagram/<str:diagram_id>', load_diagram_from_database, name='load_diagram'),
    path('open-diagrams', list_open_diagrams, name='open_diagrams'),
    path('all-diagrams', list_all_diagrams, name='all_diagrams'),
]

