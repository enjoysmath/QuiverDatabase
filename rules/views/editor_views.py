from django.shortcuts import render, redirect, HttpResponse
from database_service.models import (Object, Category, Diagram, get_model_by_uid, get_model_class,
                                     DiagramRule)
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.http_tools import get_posted_text
from django.http import JsonResponse
from QuiverDatabase.python_tools import full_qualname
import json
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from QuiverDatabase.settings import DEBUG
from neomodel import db


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
    
    

@login_required
def rule_search(request, diagram_id:str):
    try:
        session = request.session
        user = request.user.username
        
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        objects = diagram.all_objects()
            
        
        #results, meta = db.cypher_query(
            #f'MATCH (O:Object)-[:MAPS_TO*]->(x:Object) WHERE D.uid="{self.uid}" RETURN x')
        #results = [Object.inflate(row[0]) for row in results]
        
        #context = {
            #'rule_title' : rule.name,
            #'key_diagram_id' : rule.key_diagram.single().uid,
            #'result_diagram_id' : rule.result_diagram.single().uid,
        #}
        
        context = {}
        
        return render(request, 'rule_search.html', context)
        
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')    