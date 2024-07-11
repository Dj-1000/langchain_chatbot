from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms   
from .models import ChatUser
from django.forms.widgets import PasswordInput, TextInput

#register a user
class CreateUserForm(UserCreationForm):
    class Meta:
        model = ChatUser
        fields = ['email','password1','password2']
        
        
# authenticate the user
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
