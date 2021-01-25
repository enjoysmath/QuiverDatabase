from django.forms import TextInput, PasswordInput, CharField, ModelForm, EmailField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from QuiverDatabase.settings import MAX_PASSWORD_LENGTH, MAX_USERNAME_LENGTH
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout


class SignupForm(UserCreationForm):
    email = EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
       
    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user



class LoginForm(AuthenticationForm):
    username = CharField(max_length=MAX_USERNAME_LENGTH, widget=TextInput(attrs={'placeholder': 'Username'}))
    password = CharField(max_length=MAX_PASSWORD_LENGTH, widget=PasswordInput())
               
    class Meta:
        model = User   
        fields = ['username', 'password']

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Sign In', css_class='btn btn-success'))
    helper.form_method = 'POST'    