from django.shortcuts import render, HttpResponse, redirect
from .models import Object, Category
from neomodel import db, clear_neo4j_database
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

# Create your views here.

@csrf_exempt       # TODO: how do we do this /with/ CSRF?
@api_view(['POST'])
def save_to_database(request):
    print(request.POST)
    return HttpResponse(request.POST)

def get_objects(request):
    context = {
        'objects' : Object.nodes.all()
    }
    return render(request, 'objects.html', context)


def clear_database(request):
    clear_neo4j_database(db)
    return redirect('objects')


def create_test_data(request):   
    C = Category(name='C')
    C.save()
    x = Object(name='x')
    x.save()
    x.category.connect(C)
    C.objects.connect(x)
    y = Object(name='y')
    y.save()
    y.category.connect(C)
    C.objects.connect(y)
    f = x.morphisms.connect(y, {'name' : 'f'})
    f.save()
    return redirect('objects')

