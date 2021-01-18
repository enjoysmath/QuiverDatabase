from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def error(request, msg):
    return render(request, 'error.html', context={'error_msg': msg})


