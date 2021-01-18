from django.urls import path
from .views import *


urlpatterns = [
    path('editor/', rule_editor, name='rule_editor'),
    path('editor/set-title', set_rule_title, name='set_rule_title'),
    path('editor/set-key-category', set_rule_key_category, name='set_rule_key_category'),
    path('editor/set-result-category', set_rule_result_category, name='set_rule_result_category'),
    path('editor/set-key-diagram-name', set_key_diagram_name, name='set_key_diagram_name'),
    path('editor/set-result-diagram-name', set_result_diagram_name, name='set_result_diagram_name')
]

