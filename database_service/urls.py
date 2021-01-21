from django.urls import path
from .views import *


urlpatterns = [
    path('set-model-name/<str:Model>', set_model_name, name='set_model_name'),
]

