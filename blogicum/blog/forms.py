from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)