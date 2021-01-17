from django.views.generic import CreateView
from django.shortcuts import render, HttpResponse
from .models import DiagramRule
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def rule_editor(request):
    return render(request, 'rule_editor.html')


def edit_rule_title(request):
    print(request.POST)
    return HttpResponse(str(request.POST))


def edit_rule_key_category(request):
    print(request.POST)
    return HttpResponse(str(request.POST))

    
def edit_rule_result_category(request):
    print(request.POST)
    return HttpResponse(str(request.POST))
