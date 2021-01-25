from django.shortcuts import render, redirect
from .forms import SignupForm, SigninForm
from django.views.generic import CreateView, FormView, View
from .models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import TemplateResponseMixin
from django.contrib import auth
from urllib import parse as urlparse 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from QuiverDatabase.python_tools import full_qualname
from inspect import getframeinfo, currentframe
from django.core.exceptions import ObjectDoesNotExist
from database_service.models import Diagram

# Create your views here.


def signup_view(request, next:str=None):
    try:
        form = SignupForm(request.POST)
    
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.password = make_password(form.cleaned_data['password1'])
            new_user.save()
            
            login(request, new_user)
            
            if next is None:
                next = request.GET.get('next', 'profile')
                
            login(request, new_user)            
            return redirect(next)
        return render(request, 'signup.html', {'form': form})   
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return redirect('error', full_qualname(e) + ': ' + str(e), frameinfo.lineno, frameinfo.filename)        
        
        
def login_view(request, next:str=None):
    try:
        logout(request)
        
        if request.POST:
            username = request.POST['username']
            password = request.POST['password']
    
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    if next is None:
                        next = request.POST.get('next', 'profile')
                    login(request, user)
                    return redirect(next)
    
        context = {
            'form' : SigninForm(request.POST)
        }
                
        return render(request, 'login.html', context)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return redirect('error', full_qualname(e) + ': ' + str(e), frameinfo.lineno, frameinfo.filename)
        

@login_required
def logout_view(request, next:str=None):
    try:            
        user = request.user
        
        if user and user.is_authenticated:
            logout(request)
            
        if next is None:
            next = request.GET.get('next', 'home')
            
        return redirect(next)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return redirect('error', full_qualname(e) + ': ' + str(e), frameinfo.lineno, frameinfo.filename)
    
    

@login_required
def user_profile(request):
    diagrams = []
    session = request.session
    
    if 'diagram ids' in session:
        for diagram_id in session['diagram ids']:
            try:
                diagram = Diagram.get_or_none(uid=diagram_id)
                diagrams.append(diagram)
            except ObjectDoesNotExist:
                messages.warning(f'Diagram with uid {diagram_id} does not exist but is listed in profile of {request.user.username}') 
                session['diagram ids'].remove(diagram_id)
                session.save()
    
    context = {
        'diagrams' : diagrams
    }
                
    return render(request, 'user_profile.html', context)
    
    

