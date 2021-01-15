from django.urls import path
from .views import *


urlpatterns = [
    path('', get_objects, name='index'),
    path('objects/', get_objects, name='objects'),
    path('create-test-data/', create_test_data, name='create'),
    path('clear-database/', clear_database, name='clear'),
    path('save/', save_to_database, name='save'),
]

