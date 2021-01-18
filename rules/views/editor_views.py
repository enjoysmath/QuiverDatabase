from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from ..models import DiagramRule
from database_service.models import Diagram, Category
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from ..factory import get_rule_by_id
from database_service.factory import get_diagram, get_category

# Create your views here.

@login_required
@user_passes_test(is_editor)
def rule_editor(request):
    try:    
        rule_id = request.session.get('rule_id', None)
        
        rule = get_rule_by_id(
            rule_id,
            key={'name': 'Key Diagram'},
            key_cat={'name': 'Any'},
            res={'name': 'Result Diagram'},
            res_cat={'name': 'Any'},
            title='Rule Title')
    
        key = rule.key_diagram.single()
        key_cat = key.category.single()
        res = rule.result_diagram.single()
        res_cat = res.category.single()     
        
        request.session['rule_id'] = rule.uid
        request.session['editing_rule'] = True
        context = {
            'key_cat' : key_cat.name,
            'result_cat' : res_cat.name,
            'rule_title' : rule.title,
            'key_diagram' : key.name,
            'result_diagram' : res.name,
        }
        
        return render(request, 'rule_editor.html', context)  
            
    except Exception as e:
        if 'editing_rule' in request.session:
            request.session['editing_rule'] = False
        if 'rule_id' in request.session:
            del request.session['rule_id']
        return redirect('error', str(e))


@login_required   
@user_passes_test(is_editor)
def set_rule_title(request):
    if request.session.get('editing_rule', False):  
        try:                
            if not 'value' in request.POST:
                data = {'success': False, 'error_msg': 'Error, missing POST parameter(s).'}
                return JsonResponse(data)
            
            rule_title = request.POST['value']           
            rule = DiagramRule.nodes.get(uid=request.session['rule_id'])
            
            if rule.title != rule_title:
                rule.title = rule_title
                rule.save()
            # else: current rule title is correct
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error_msg': f'Exception: {e}'})
    else:
        return JsonResponse({'succes': False, 'error_msg': 'Settable only in rule editor.'})


@login_required   
@user_passes_test(is_editor)
def set_rule_key_category(request):
    #"""
    #X-Editable: handle post request to change the value of an attribute of an object
    #request.POST['pk']: pk of object to be changed
    #request.POST['value']: new value to be set
    #"""        
    if request.session.get('editing_rule', False):  
        try:                
            if not 'value' in request.POST:
                data = {'success': False, 'error_msg': 'Error, missing POST parameter(s).'}
                return JsonResponse(data)
            
            cat_name = request.POST['value']
            
            rule = DiagramRule.nodes.get(uid=request.session['rule_id'])
            key = rule.key_diagram.single()
            current_cat = key.category.single()
            
            if current_cat.name != cat_name:
                cat = get_category(name=cat_name)
                key.category.reconnect(current_cat, cat)
                key.save()
            # else: current cat name is correct
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error_msg': f'Exception: {e}'})
    else:
        return JsonResponse({'succes': False, 'error_msg': 'Settable only in rule editor.'})


@login_required   
@user_passes_test(is_editor)    
def set_rule_result_category(request):
    if request.session.get('editing_rule', False):  
        try:                
            if not 'value' in request.POST:
                data = {'success': False, 'error_msg': 'Error, missing POST parameter(s).'}
                return JsonResponse(data)
            
            cat_name = request.POST['value']
            
            rule = DiagramRule.nodes.get(uid=request.session['rule_id'])
            res = rule.result_diagram.single()
            current_cat = res.category.single()
            
            if current_cat.name != cat_name:
                cat = get_category(name=cat_name)
                res.category.reconnect(current_cat, cat)
                res.save()
            # else: current cat name is correct
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error_msg': f'Exception: {e}'})
    else:
        return JsonResponse({'succes': False, 'error_msg': 'Settable only in rule editor.'})
    
    
@login_required   
@user_passes_test(is_editor)
def set_key_diagram_name(request):
    #"""
    #X-Editable: handle post request to change the value of an attribute of an object
    #request.POST['pk']: pk of object to be changed
    #request.POST['value']: new value to be set
    #"""        
    if request.session.get('editing_rule', False):  
        try:                
            if not 'value' in request.POST:
                data = {'success': False, 'error_msg': 'Error, missing POST parameter(s).'}
                return JsonResponse(data)
            
            diagram_name = request.POST['value']
            
            rule = DiagramRule.nodes.get(uid=request.session['rule_id'])
            key = rule.key_diagram.single()
            
            if key.name != diagram_name:
                key.name = diagram_name
                key.save()
            # else: current diagram name is correct
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error_msg': f'Exception: {e}'})
    else:
        return JsonResponse({'succes': False, 'error_msg': 'Settable only in rule editor.'})


@login_required   
@user_passes_test(is_editor)    
def set_result_diagram_name(request):
    if request.session.get('editing_rule', False):  
        try:                
            if not 'value' in request.POST:
                data = {'success': False, 'error_msg': 'Error, missing POST parameter(s).'}
                return JsonResponse(data)
            
            diagram_name = request.POST['value']
            
            rule = DiagramRule.nodes.get(uid=request.session['rule_id'])
            res = rule.result_diagram.single()
            
            if res.name != diagram_name:
                res.name = diagram_name
                res.save()
            # else: current diagram name is correct
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error_msg': f'Exception: {e}'})
    else:
        return JsonResponse({'succes': False, 'error_msg': 'Settable only in rule editor.'})