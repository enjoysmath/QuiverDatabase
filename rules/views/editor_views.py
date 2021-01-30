from django.shortcuts import render, redirect
from django.http import JsonResponse
from database_service.models import DiagramRule, Diagram, get_unique
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.python_tools import full_qualname
from QuiverDatabase.settings import MAX_TEXT_LENGTH
from django.core.exceptions import ObjectDoesNotExist
from QuiverDatabase.http_tools import get_posted_text
from django.db import OperationalError
import traceback

# Create your views here.

@login_required
@user_passes_test(is_editor)
def rule_editor(request, rule_id):
    try:   
        session = request.session
        user = request.user.username
        
        if 'rule ids' not in session:
            session['rule ids'] = []
            
        rule = DiagramRule.nodes.get(uid=rule_id)
        
        if rule:
            if not rule.checked_out_by:
                rule.checked_out_by = user
                session['rule ids'].append(rule_id)
                session.save()
            else:
                if rule.checked_out_by != user:
                    raise OperationalError(
                        f'The rule with id "{rule_id}" is already checked out by {rule.checked_out_by}.')
        else:
            raise ObjectDoesNotExist(f'There exists no diagram with uid "{rule_id}".')
        
        context = {
            'rule_title' : rule.name,
            'key_diagram_id' : rule.key_diagram.single().uid,
            'result_diagram_id' : rule.result_diagram.single().uid,
        }
        
        return render(request, 'rule_editor.html', context)
        
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    


@login_required
@user_passes_test(is_editor)
def create_new_rule(request):
    rule = DiagramRule.our_create()
    rule.checked_out_by = request.user.username
    
    request.sesstion['new rule'] = rule
    
    context = {
        'rule_name' : rule.name,
    }
    
    return render(request, 'new_rule.html', context)
    
    
