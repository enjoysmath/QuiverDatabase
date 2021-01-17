from django.views.generic import CreateView
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import DiagramRule
from database_service.models import Diagram, Category, unique
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext


# Create your views here.

uid = None  # TODO: how does Django handle user session?

def rule_editor(request):
    key_cat = unique(Category, name='Any').save()
    res_cat = key_cat
    
    key_diagram = Diagram(name='Key Diagram').save()
    key_diagram.category.connect(key_cat)
    key_diagram.save()
    res_diagram = Diagram(name='Result Diagram').save()
    res_diagram.category.connect(res_cat)
    
    diagram_rule = DiagramRule(title='Rule Title').save()
    diagram_rule.key_diagram.connect(key_diagram)
    diagram_rule.save()
    diagram_rule.result_diagram.connect(res_diagram)
    diagram_rule.save()   
    
    global uid
    uid = diagram_rule.uid
        
    context = {
        'key_cat' : key_cat.name,
        'result_cat' : res_cat.name,
        'rule_title' : diagram_rule.title,
    }
    
    return render(request, 'rule_editor.html', context)    
    


def set_rule_title(request):
    pass

    #try:
        #if not 'pk' in request.POST or not 'value' in request.POST:
            #data = {'success': False, 'error_msg': 'Error, missing POST parameter'}
            #return JsonResponse(data)
        
        #rule = DiagramRule.get(uid='myDiagramId')
        
def set_rule_key_category(request):
    #"""
    #X-Editable: handle post request to change the value of an attribute of an object
    #request.POST['pk']: pk of object to be changed
    #request.POST['value']: new value to be set
    #"""        
    try:
        if not 'value' in request.POST or not 'pk' in request.POST:
            print(repr(request.POST))
            data = {'success': False, 'error_msg': 'Error, missing POST parameter(s).'}
            return JsonResponse(data)
        
        cat_name = request.POST['value']
        
        global uid  #TODO: handle with session store
        diagram_rule = DiagramRule.nodes.get(uid=uid)
        key_diagram = diagram_rule.key_diagram.single()
        current_cat = key_diagram.category.single()
        
        if current_cat.name != cat_name:
            cat = Category.nodes.get_or_none(name=cat_name)
            
            if cat is None:
                cat = unique(Category, name=cat_name).save()
            
            key_diagram.category.reconnect(current_cat, cat)
            key_diagram.save()
        # else: current cat name is correct
        
        data = {'success': True}
        return JsonResponse(data)
    
    except Exception as e:
        #key_diagram = diagram_rule.key_diagram.get_or_none
        data = {'success': False, 'error_msg': f'Exception: {e}'}
        return JsonResponse(data)

    
def set_rule_result_category(request):
    print(request.POST)
    return HttpResponse(str(request.POST))
