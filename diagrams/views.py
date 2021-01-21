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

# Create your views here.

@login_required
@user_passes_test(is_editor)
def diagram_editor(request, diagram_id=None):
    try:
        session = request.session
        user = request.user.username
        
        full_page = request.GET.get('full_page', 'yes')
        
        if 'diagram ids' not in session:
            session['diagram ids'] = []
    
        diagram = Diagram.nodes.get(uid=diagram_id)
        
        if diagram:
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
           
        context = {
            'diagram_name' : diagram.name,
            'category_name' : diagram.category.single().name,
            'full_page' : full_page,
            'category_id' : diagram.category.single().uid,
            'diagram_id' : diagram.uid,
        }
                      
        return render(request, 'diagram_editor.html', context)  
    
    except Exception as e:
        return redirect('error', full_qualname(e) + ': ' + str(e))
    


@login_required
@user_passes_test(is_editor)
def create_new_diagram(request):
    full_page = request.GET.get('full_page', 'yes')
    diagram = Diagram.our_create(name='', checked_out_by=request.user.username)
                
    return render(request, 'new_diagram.html', 
                  context={'full_page': full_page, 'diagram_id': diagram.uid})
  