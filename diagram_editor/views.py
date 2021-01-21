from django.shortcuts import render

# Create your views here.


def quiver_editor(request):
    return render(request, 'quiver/src/index.html')