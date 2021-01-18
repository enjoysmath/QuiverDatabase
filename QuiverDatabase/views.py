from django.shortcuts import render


def home(request):
    return render(request, 'home.html', context={'is_login_template': False})


def error(request, msg):
    return render(request, 'error.html', context={'error_msg': msg})


