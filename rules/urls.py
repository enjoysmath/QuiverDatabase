from django.urls import path
from .views import *


urlpatterns = [
    path('editor/', rule_editor, name='rule_editor'),
    path('editor/set-title', set_rule_title, name='set_rule_title'),
    path('editor/set-key-cat', set_rule_key_category, name='set_rule_key_category'),
    path('editor/set-result-cat', set_rule_result_category, name='set_rule_result_category'),
]

