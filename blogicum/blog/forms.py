from django import forms
from django.urls import reverse_lazy

from .models import Comment, Post


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'is_published',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'), attrs={'type': 'datetime-local'}
            )
        }
        success_url = reverse_lazy('blog:profile')
