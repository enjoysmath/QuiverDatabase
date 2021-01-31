from django.shortcuts import render
from .settings import DEBUG
from database_service.models import get_model_by_uid, Diagram

def home(request):
    diagrams = []
    
    diagram_ids = request.session.get('diagram ids', [])
    
    for id in diagram_ids:
        diagram = get_model_by_uid(Diagram, uid=id)
        diagrams.append(diagram)
    
    context = {
        'diagrams' : diagrams
    }

    return render(request, 'home.html', context)


def examples(request):
    pass


def error(request, msg:str):
    context = {
        'error_msg': msg,
    }
   
    #if DEBUG:
        #raise Exception(msg)
    
    return render(request, 'error.html', context)


