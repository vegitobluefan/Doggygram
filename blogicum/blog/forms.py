from django import forms

from .models import Comment, Post, User


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


class UserForm(forms.ModelForm):
    """User editing form."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
