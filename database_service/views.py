from django.shortcuts import render, redirect
from .models import Object, Category, Diagram, get_model_by_uid, get_model_class
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.http_tools import get_posted_text
from django.http import JsonResponse
from QuiverDatabase.python_tools import full_qualname

# Create your views here.

@login_required   
@user_passes_test(is_editor)
def set_model_name(request, Model:str):
    try:        
        name = get_posted_text(request)        
        
        if name == '':
            raise Exception(f'Name cannot be empty.')
                
        old_id = request.POST['pk']
        
        ModelClass = get_model_class(Model)         
        model = get_model_by_uid(ModelClass, uid=old_id)
                
        if model.name != name:
            model_exists = ModelClass.nodes.get_or_none(name=name)
            
            if model_exists:
                raise ValueError(f'A {Model} already exists with name "{name}".')
            
            model.name = name
            model.save()
            
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error_msg': f'{full_qualname(e)}: {e}'}) 

