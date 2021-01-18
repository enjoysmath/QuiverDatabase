from django.shortcuts import render, HttpResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from database_service.models import Diagram
from database_service.factory import get_diagram
# Create your views here.

@login_required
@user_passes_test(is_editor)
def diagram_editor(request, diagram_id=None):
    try:
        if request.method == 'GET':
            
            diagram = get_diagram()
            
            if diagram_id is not None:
                diagram = Diagram.nodes.get(uid=diagram_id)
                
                if diagram is None:
                    return Http404("Diagram ID: " + str(diagram_id) + " not found in DB.")       
                
                if diagram.is_checked_out:
                    return HttpResponse("The diagram " + str(diagram.name) + " is already checked out.")
            
                context = {
                    'diagram_name' : diagram.name,
                }
                
            else:
                diagram = get
            
            return render(request, 'diagram_editor.html', context)  
            
            
        
        #rule_id = request.session.get('rule_id', None)
        
        #rule = get_rule_by_id(
            #rule_id,
            #key={'name': 'Key Diagram'},
            #key_cat={'name': 'Any'},
            #res={'name': 'Result Diagram'},
            #res_cat={'name': 'Any'},
            #title='Rule Title')
    
        #key = rule.key_diagram.single()
        #key_cat = key.category.single()
        #res = rule.result_diagram.single()
        #res_cat = res.category.single()     
        
        #request.session['rule_id'] = rule.uid
        #request.session['editing_rule'] = True
        #context = {
            #'key_cat' : key_cat.name,
            #'result_cat' : res_cat.name,
            #'rule_title' : rule.title,
            #'key_diagram' : key.name,
            #'result_diagram' : res.name,
        #}
        
        #return render(request, 'rule_editor.html', context)  
            
    #except Exception as e:
        #if 'editing_rule' in request.session:
            #request.session['editing_rule'] = False
        #if 'rule_id' in request.session:
            #del request.session['rule_id']
        #return redirect('error', str(e))