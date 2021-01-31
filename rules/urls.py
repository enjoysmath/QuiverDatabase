from django.urls import path
from .views import *


urlpatterns = [
    path('editor/<str:rule_id>', rule_editor, name='rule_editor'),
    path('create-new-rule', create_new_rule, name='create_new_rule'),
    path('search/<str:diagram_id>', rule_search, name='rule_search'),
]

