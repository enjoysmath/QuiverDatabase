from django.shortcuts import render, redirect
from .models import Object, Category, Diagram, get_model_by_uid, get_model_class
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.http_tools import get_posted_text
from django.http import JsonResponse
from QuiverDatabase.python_tools import full_qualname
from .quiver_data_format import QuiverDataFormat
import json
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist

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



@login_required   
@user_passes_test(is_editor)
def save_diagram_to_database(request, diagram_id):
    try:
        if request.method != 'POST' or not request.headers.get("contentType", "application/json; charset=utf-8"):
            raise OperationalError('You can only use the POST method to save to the database.')            
        user = request.user.username
        
        diagram = get_model_by_uid(Diagram, uid=diagram_id)

        if diagram is None:
            raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".') 
        
        if diagram.checked_out_by != user:
            raise OperationalError(
                f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')                
                       
        body = request.body.decode('utf-8')
        
        if body:
            try:
                recvd_json = json.loads(body)
                data = QuiverDataFormat(recvd_json)
                
            except json.decoder.JSONDecodeError:
                # For some reason, empty diagrams are resulting in the body as a URL str (not JSON)
                data = QuiverDataFormat.Default                
        else:
            data = QuiverDataFormat.Default            
        
        diagram.delete_objects()
        category = diagram.category.single()
        
        obs = []
                
        for v in data.vertices:
            o = Object.create_from_editor(v)
            obs.append(o)
            
        for e in data.edges:
            A = obs[e.source_index]
            B = obs[e.target_index]
            f = A.morphisms.connect(B, {'name': e.label.string})
            if category.of_categories:
                f.functor = True
            A.save()                  
            f.load_from_editor(e)
            
        diagram.add_objects(obs)                
                                            
        return JsonResponse(str(data), safe=False)

    except Exception as e:
        raise e
    
    #except Exception as e:
        #return JsonResponse({'success': False, 'error_msg': f'{full_qualname(e)}: {e}'}) 
