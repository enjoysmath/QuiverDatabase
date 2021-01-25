from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm  # AuthenticationForm
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

# Create your views here.



class SignupView(SuccessMessageMixin, CreateView):        
    template_name = 'sign_up.html'
    form_class = SignupForm
    succes_url = reverse_lazy('home')
    success_message = 'Your account was created successfully.'
    


    
class LoginView(SuccessMessageMixin, FormView):
    form_class = LoginForm    
    template_name = 'login.html'
    success_message = 'Successful login message. (TODO)'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can check the test cookie stuff and log him in.
        """
        self.check_and_delete_test_cookie()
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def form_invalid(self, form):
        """
        The user has provided invalid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        set the test cookie again and re-render the form with errors.
        """
        self.set_test_cookie()
        return super(LoginView, self).form_invalid(form)

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.get(), but adds test cookie stuff
        """
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)




class LogoutView(TemplateResponseMixin, View):
    template_name = "logout.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        else:
            return redirect('home')
        return self.render_to_response(context={})


