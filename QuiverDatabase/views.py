from django.shortcuts import render
from .settings import DEBUG

def home(request):
    return render(request, 'home.html')


def error(request, msg, line, file):
    context = {
        'error_msg': msg,
    }
    
    if DEBUG:
        context['line_number'] = line
        context['file'] = file
 
    return render(request, 'error.html', context)


