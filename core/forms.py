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
            'class': 'form-control border-top-0 border-end-0 border-start-0 rounded-0 shadow-none',
            'placeholder': "username",
            'style': 'border-bottom: 0.8px solid #ccc;'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border-top-0 border-end-0 border-start-0 rounded-0 shadow-none',
            'placeholder': 'passw',
            'style': 'border-bottom: 0.8px solid #ccc;'
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  
        super(LoginForm, self).__init__(*args, **kwargs)

class CourseCreateForm(ModelForm):
    class Meta:
        model = Course
        fields = ['module', 'title', 'description']
