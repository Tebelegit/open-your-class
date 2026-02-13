from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import TheUser, Course



class RegisterForm(UserCreationForm):
    class Meta:
        model = TheUser
        fields = ['username', 'role', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-underline no-radius',
            'placeholder': "username"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-underline no-radius',
            'placeholder': 'Mot de passe'
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # On retire 'request' des arguments avant de continuer
        super(LoginForm, self).__init__(*args, **kwargs)

class CourseCreateForm(ModelForm):
    class Meta:
        model = Course
        fields = ['module', 'title', 'description']
