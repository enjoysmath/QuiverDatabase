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
            
        rule = get_model_by_uid(DiagramRule, uid=rule_id)
        
        if rule.checked_out_by is None:
            if rule.can_be_checked_out():
                rule.checked_out_by = user
                session['rule ids'].append(rule_id)
                session.save()
        else:
            if rule.checked_out_by != user:
                raise OperationalError(
                    f'The rule with id "{rule_id}" is already checked out by {rule.checked_out_by}.')
        
        view_only = request.GET.get('viewonly', 'no')
        
        if view_only != 'no':
            view_only = 'yes'
        
        context = {
            'rule' : rule,
            'key_diagram' : rule.key_diagram.single(),
            'result_diagram' : rule.result_diagram.single(),
            'view_only' : view_only,
        }
        
        return render(request, 'rule_editor.html', context)
        
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    


@login_required
@user_passes_test(is_editor)
def create_new_rule(request):
    try:          
        rule = DiagramRule.our_create(key='Key', res='Result', name='')
        rule.checked_out_by = request.user.username
        rule.save()
        
        #request.session['new rule id'] = rule.uid  # BUGFIX: cannot pass rule to session itself (not JSON-serializable)
        
        context = {
            'rule' : rule
        }
    
        return render(request, 'new_rule.html', context)
    
    except Exception as e:
        if DEBUG:
            raise e
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    

rule_search_orders = [
    ('creator', 'Creator Name'),
    ('created', 'Date Created'),
    ('edited', 'Date Edited'),
    ('usages', 'Number of Usages'),
    ('views', 'Number of Views'),
    ('votes', 'Sum of Votes'),
    ('name', 'Rule Name'),
]

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
        
        ascending = request.GET.get('asc', 'true')
        order_param = request.GET.get('ord', 'name')
        
        for (param, text) in rule_search_orders:
            if order_param == param:
                order_text = text
                break
        else:
            raise ValueError(order_param + " is not a valid value to order by.")
        
        test_rule = DiagramRule.our_create(name="Rule Test Name")
        
        context = {
            'diagram_id' : diagram_id,
            'order_param' : order_param,
            'order_text' : order_text,
            'orders' : rule_search_orders,
            'rules' : [test_rule],
            'ascending' : ascending,
        }
        
        return render(request, 'rule_search.html', context)
        
    except Exception as e:
        #if DEBUG:
            #raise e
        return redirect('error', f'{full_qualname(e)}: {str(e)}')    
    
    
@login_required
@user_passes_test(is_editor)
def apply_rule(request, rule_id:str, diagram_id:str):
    try:
        rule = get_model_by_uid(DiagramRule, uid=rule_id)
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        
        var_map = diagram.get_variable_mapping(rule.key_diagram.single())
        
        # Create a new diagram with rule applied and variables appropriately substituted.
       
    except Exception as e:
        if DEBUG:
            raise e
        redirect('error', f'{full_qualname(e)}: {str(e)}')
    
    
def rule_viewer(request, rule_id):
    try:   
        session = request.session
        user = request.user.username
 
        rule = get_model_by_uid(DiagramRule, uid=rule_id)
        key_diagram = rule.key_diagram.single()
        res_diagram = rule.result_diagram.single()
        
        context = {
            'rule' : rule,
            'key_diagram' : key_diagram,
            'result_diagram' : res_diagram,
            'view_only' : 'no',
        }
        
        return render(request, 'rule_editor.html', context)
        
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')