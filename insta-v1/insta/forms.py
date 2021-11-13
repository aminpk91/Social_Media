import re
from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Post


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"
        exclude = "fg","fw"


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        exclude = "like",


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "username")
