from django.shortcuts import render, redirect
from django.http import JsonResponse
from database_service.models import Diagram, Category, Rule, get_unique
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.python_tools import full_qualname
from QuiverDatabase.http_tools import get_posted_text
from database_service.http_tools import get_diagram
#from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
import traceback
from QuiverDatabase.python_tools import deep_get, deep_get
import json
from database_service.models import Object, Category, Diagram, get_model_by_uid

# Create your views here.

@login_required
@user_passes_test(is_editor)
def quiver_editor(request, diagram_id):
    try:
        session = request.session
        user = request.user.username
 
        if 'diagram ids' not in session:
            session['diagram ids'] = []
    
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        
        if diagram:
            if diagram.name == '':
                raise ValueError('Diagram name must not be empty.')
            
            if not diagram.checked_out_by:
                diagram.checked_out_by = user
                session['diagram ids'].append(diagram_id)
                session.save()
            else:
                if diagram.checked_out_by != user:
                    raise OperationalError(
                        f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')
        else:
            raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".')                
        
        category = diagram.category.single()
        
        context = {
            'diagram_name' : diagram.name,
            'category_name' : category.name,
            'category_id' : category.uid,
            'diagram_id' : diagram.uid,
            'quiver_str' : json.dumps(diagram.quiver_format()),
        }
                      
        return render(request, 'quiver.html', context)  
    
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    
    

@login_required
def quiver_viewer(request, diagram_id:str):
    try:
        session = request.session
        user = request.user.username
 
        if 'diagram ids' not in session:
            session['diagram ids'] = []
    
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        
        if diagram:
            if diagram.name == '':
                raise ValueError('Diagram name must not be empty.')
            
            if not diagram.checked_out_by:
                diagram.checked_out_by = user
                
                if diagram_id not in session['diagram ids']:
                    session['diagram ids'].append(diagram_id)
                    session.save()
            else:
                if diagram.checked_out_by != user:
                    raise OperationalError(
                        f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')
        else:
            raise ObjectDoesNotExist(f'There exists no diagram with uid "{diagram_id}".')                
        
        category = diagram.category.single()
        
        context = {
            'diagram_name' : diagram.name,
            'category_name' : category.name,
            'diagram_id' : diagram.uid,
            'view_only' : None,   # Existence of this variable is tested for
            'quiver_str' : json.dumps(diagram.quiver_format()),
        }
                      
        return render(request, 'quiver.html', context)  
    
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    

@login_required
def diagram_result_view(request, diagram_id:str):
    try:
        session = request.session
        user = request.user.username
 
        if 'diagram ids' not in session:
            session['diagram ids'] = []
    
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        
        if diagram.name == '':
            raise ValueError('Diagram name must not be empty.')
        
        if not diagram.checked_out_by:
            diagram.checked_out_by = user
            
            if diagram_id not in session['diagram ids']:
                session['diagram ids'].append(diagram_id)
                session.save()
        else:
            if diagram.checked_out_by != user:
                raise OperationalError(
                    f'The diagram with id "{diagram_id}" is already checked out by {diagram.checked_out_by}')
                     
        category = diagram.category.single()
        
        context = {
            'diagram' : diagram,
            'category' : category,
            'view_only' : None,  # Test for existence is made
        }
                      
        return render(request, 'quiver_result_preview.html', context)  
    
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')


    

@login_required
@user_passes_test(is_editor)
def create_new_diagram(request):
    diagram = Diagram.our_create(name='', checked_out_by=request.user.username)
    session = request.session
    
    if 'diagram ids' not in session:
        session['diagram ids'] = [diagram.uid]
    else:
        if diagram.uid not in session['diagram ids']:
            session['diagram ids'].append(diagram.uid)
            session.save()

    diagrams = []
    
    for diagram_id in session['diagram ids']:
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        diagrams.append(diagram)
        
    context={
        'diagram_id': diagram.uid,
        'diagrams' : diagrams,
    } 
                
    return render(request, 'new_diagram.html', context)
    