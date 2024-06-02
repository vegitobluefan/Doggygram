from django import forms  # type: ignore
from django.urls import reverse_lazy  # type: ignore

from .models import Comment, Post


class CommentForm(forms.ModelForm):
    """Comment creation form."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Post creation form."""

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'is_published',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'), attrs={'type': 'datetime-local'}
            )
        }
