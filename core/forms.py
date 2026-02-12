from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import TheUser, Course



class RegisterForm(UserCreationForm):
    class Meta:
        model = TheUser
        fields = ['username', 'role', 'password1', 'password2']

class LoginForm(ModelForm):
    class Meta:
        model = TheUser
        fields = ['username', 'password']

class CourseCreateForm(ModelForm):
    class Meta:
        model = Course
        fields = ['module', 'title', 'description']
