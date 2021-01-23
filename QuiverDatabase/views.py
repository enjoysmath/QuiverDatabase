from django.shortcuts import render
from .settings import DEBUG

def home(request):
    full_page = request.GET.get('full_page', 'yes')
    
    return render(request, 'home.html', 
                  context={'is_login_template': False,
                           'full_page': full_page})


def error(request, msg, line, file):
    context = {
        'erro_msg': msg,
    }
    
    if DEBUG:
        context['line_num'] = line
        context['file_path'] = file

    return render(request, 'error.html', context=context)


