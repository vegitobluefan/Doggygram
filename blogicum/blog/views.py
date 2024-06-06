from django.utils import timezone
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from blog.models import Category, Comment, Post, User
from blog.forms import CommentForm, PostForm, UserForm


class Profile(ListView):
    """User's profile view."""

    template_name = 'blog/profile.html'
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        self.user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Post.posts_manager.filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user

        return context


class ProfieEditView(LoginRequiredMixin, UpdateView):
    """User's profile editing view."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


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


class PostBaseMixin:
    """Base mixin for post views."""

    model = Post
    slug_field = 'id'
    slug_url_kwarg = 'post_id'

    def get_post(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return post


class PostDetailView(PostBaseMixin, DetailView):
    """Certain post view."""

    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_post()

        if (
            not post.category.is_published
            or post.pub_date > timezone.now()
            or not post.is_published
        ) and post.author != request.user:
            raise Http404('Пост не найден.')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()

        return context


class CategoryPostsView(ListView):
    """View for posts in certain category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return Post.posts_manager.filter(
            category__slug=self.kwargs['category_slug'],
            pub_date__lte=timezone.now(),
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentBaseMixin(LoginRequiredMixin):
    """Mixin for comments."""

    model = Comment
    template_name = 'blog/comment.html'


class CommentEditDeleteMixin(CommentBaseMixin):
    """Mixin for editing or deleting comment views."""

    slug_field = 'id'
    slug_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        if comment.author != request.user:
            raise Http404('Пост не найден.')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentCreateView(CommentBaseMixin, CreateView):
    """View for comment creation."""

    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        form.instance.author = self.request.user
        form.instance.post_id = post.pk
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
    """Post creation view."""

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


class PostEditDeleteMixin(PostBaseMixin, LoginRequiredMixin):
    """Mixin for post creation and deletion views."""

    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_post()

        if self.request.user != post.author:
            return redirect(
                'blog:post_detail', post_id=post.pk
            )

        return super().dispatch(request, *args, **kwargs)


class PostEditView(PostEditDeleteMixin, UpdateView):
    """Post editing view."""

    form_class = PostForm

    def get_success_url(self):
        post = self.get_post()
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post.pk}
        )


class PostDeleteView(PostEditDeleteMixin, DeleteView):
    """Post deletion view."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:index')
