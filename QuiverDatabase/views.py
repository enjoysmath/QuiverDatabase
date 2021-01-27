from django.shortcuts import render
from .settings import DEBUG

def home(request):
    return render(request, 'home.html')


def error(request, msg:str):
    context = {
        'error_msg': msg,
    }
   
    if DEBUG:
        raise Exception(msg)
    
    return render(request, 'error.html', context)


