from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Comment, Post


User = get_user_model()


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
