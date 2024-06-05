from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from blog.models import Category, Comment, Post
from blog.forms import CommentForm, PostForm, UserForm


User = get_user_model()


class Profile(ListView):
    """User's profile view."""

    template_name = 'blog/profile.html'
    paginate_by = settings.POST_PAGINATION

    def get_user_profile(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        return Post.posts_manager.filter(
            author=self.get_user_profile()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_profile()

        return context


class ProfieEditView(LoginRequiredMixin, UpdateView):
    """User's profile editing view."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostBaseMixin:
    """Base mixin for posts"""

    model = Post
    slug_field = 'id'
    slug_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if (
            not post.category.is_published
            or post.pub_date > timezone.now()
            or not post.is_published
        ) and post.author != request.user:
            raise Http404('Пост не найден.')

        return super().dispatch(request, *args, **kwargs)


class PostListView(ListView):
    """Post list view."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        return Post.posts_manager.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )


class PostDetailView(PostBaseMixin, DetailView):
    """Certain post view."""

    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author', 'post'
            ).filter(
                post__id=self.kwargs['post_id']
            )
        )
        return context


class CategoryPostsView(ListView):
    """View for posts in certain category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        return Post.posts_manager.filter(
            category__slug=self.kwargs['category_slug'],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class CommentBaseMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'


class CommentEditDeleteMixin(CommentBaseMixin):
    slug_field = 'id'
    slug_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        if instance.author != request.user:
            raise Http404('Пост не найден.')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentCreateView(CommentBaseMixin, CreateView):
    """View for comment creation"""

    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentEditView(CommentEditDeleteMixin, UpdateView):
    """Comment editing view."""

    form_class = CommentForm


class CommentDeleteView(CommentEditDeleteMixin, DeleteView):
    """View for comment deletion."""

    pass


class PostCreateView(LoginRequiredMixin, CreateView):
    """Creation view"""

    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostEditView(PostBaseMixin, LoginRequiredMixin, UpdateView):
    """Post editing view."""

    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostBaseMixin, LoginRequiredMixin, DeleteView):
    """Post deletion view."""

    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:index')
