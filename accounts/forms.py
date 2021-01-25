from django.forms import TextInput, PasswordInput, CharField, ModelForm, EmailField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from QuiverDatabase.settings import MAX_PASSWORD_LENGTH, MAX_USERNAME_LENGTH
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout



from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column



class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-3 mb-0 input'),
                Column('email', css_class='form-group col-md-3 mb-0 input'),
                Column('password1', css_class='form-group col-md-3 mb-0 input'),
                Column('password2', css_class='form-group col-md-3 mb-0 input'),
                css_class='form-row'
            )
        )
    
    
    
class SigninForm(AuthenticationForm):
    username = CharField(max_length=MAX_USERNAME_LENGTH, widget=TextInput(attrs={'placeholder': 'Username'}))
    password = CharField(max_length=MAX_PASSWORD_LENGTH, widget=PasswordInput())
        
    class Meta:
        model = User   
        fields = ['username', 'password']

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Sign In', css_class='btn btn-success'))
    helper.form_method = 'POST'    