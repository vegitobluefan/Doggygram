from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    """Форма создания комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Форма создания постов."""

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'is_published',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'), attrs={'type': 'datetime-local'}
            )
        }


class UserForm(UserChangeForm):
    """Форма редактирования пользователя."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
