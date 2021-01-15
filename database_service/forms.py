from django.forms import ModelForm
from models import Object

class ObjectForm(ModelForm):
    class Meta:
        model = Object
        fields = ['name'] #, 'category']