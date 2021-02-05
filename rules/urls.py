from django.urls import path
from .views import *


urlpatterns = [
    path('view/<str:rule_id>', rule_viewer, name='rule_viewer'),
    path('edit/<str:rule_id>', rule_editor, name='rule_editor'),
    path('create-new', create_new_rule, name='create_new_rule'),
    path('search/<str:diagram_id>', rule_search, name='rule_search'),
    path('apply/<str:rule_id>/<str:diagram_id>', apply_rule, name='apply_rule'),
]

