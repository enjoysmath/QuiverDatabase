from django.shortcuts import render, redirect, HttpResponse
from .models import Object, Category, Diagram, get_model_by_uid, get_model_class
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.http_tools import get_posted_text
from django.http import JsonResponse
from QuiverDatabase.python_tools import full_qualname
import json
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from QuiverDatabase.settings import DEBUG

# Create your views here.

@login_required   
@user_passes_test(is_editor)
def set_model_name(request, Model:str):
    try:        
        name = get_posted_text(request)        
        name = name.strip()
        
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
            
        return JsonResponse({'success': True, 'standardized': name})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error_msg': f'{full_qualname(e)}: {e}'}) 


@login_required
def list_open_diagrams(request):
    diagrams = []
    diagram_ids = request.session.get('diagram ids', [])
    
    for diagram_id in diagram_ids:
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        diagrams.append(diagram)
        
    context = {
        'diagrams' : diagrams
    }
        
    return render(request, 'diagram_list_page.html', context)



def load_diagram_from_database(request, diagram_id):
    try:
        if request.method == 'GET':
            diagram = get_model_by_uid(Diagram, uid=diagram_id)
            json_str = json.dumps(diagram.quiver_format())
            
            return HttpResponse(json_str, content_type='text/plain; charset=utf8')
                
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')



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
                data = json.loads(body)                
            except json.decoder.JSONDecodeError:
                # For some reason, empty diagrams are resulting in the body as a URL str (not JSON)
                data = [0, 0]               
        else:
            data = [0, 0]
        
        diagram.delete_objects()
        diagram.load_from_editor(data)        
                                            
        return JsonResponse(
            'Wrote the following data to the database:\n' + str(data), safe=False)

    except Exception as e:
        if DEBUG:
            raise e
        return JsonResponse({'error_msg' : f'{full_qualname(e)}: {str(e)}'})
    
    #except Exception as e:
        #return JsonResponse({'success': False, 'error_msg': f'{full_qualname(e)}: {e}'}) 
