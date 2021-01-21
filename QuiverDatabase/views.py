from django.shortcuts import render


def home(request):
    full_page = request.GET.get('full_page', 'yes')
    
    return render(request, 'home.html', 
                  context={'is_login_template': False,
                           'full_page': full_page})


def error(request, msg):
    return render(request, 'error.html', context={'error_msg': msg})


