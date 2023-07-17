from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

from django.contrib.auth import get_user_model
User = get_user_model()

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(help_text="Required",required=True)

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)