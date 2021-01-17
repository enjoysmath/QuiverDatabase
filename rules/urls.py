from django.urls import path
from .views import *


urlpatterns = [
    path('editor/', rule_editor, name='rule_editor'),
    path('editor/edit-title', edit_rule_title, name='edit_rule_title'),
    path('editor/edit-key-cat', edit_rule_key_category, name='edit_rule_key_category'),
    path('editor/edit-result-cat', edit_rule_result_category, name='edit_rule_result_category'),
]

