from django.utils import timezone  # type: ignore
from django.urls import reverse  # type: ignore
from django.http import Http404  # type: ignore
from django.db.models import Count  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.conf import settings  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore
from django.views.generic import (  # type: ignore
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Comment, Post
from blog.forms import CreateCommentForm, CreatePostForm


class PostListView(ListView):
    """Post list view."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related(
            'category', 'location', 'author').annotate(
            comment_count=Count('comment')
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    """Certain post view."""

    model = Post
    template_name = 'blog/detail.html'
    slug_field = 'id'
    slug_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if (
            not instance.category.is_published or
                instance.pub_date > timezone.now() or not
                instance.is_published and
                instance.author != request.user
        ):
            raise Http404('Пост не найден.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm
        context['comment'] = (
            self.object.comment.select_related('author')
        )
        return context


class CategoryPostsView(ListView):
    """View for posts in certain category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'category', 'location', 'author'
        ).filter(
            category__slug=self.kwargs['category_slug'],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(
            comment_count=Count('comment')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Comment creation view."""

    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['post_id'])
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


class CommentEditView(LoginRequiredMixin, UpdateView):
    """Comment editing view."""

    pass


class Profile(ListView):
    """User's profile view."""

    template_name = 'blog/profile.html'
    paginate_by = settings.POST_PAGINATION


class PostCreateView(LoginRequiredMixin, CreateView):
    """View for post creation."""

    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostEditView(LoginRequiredMixin, UpdateView):
    """Post editing view."""

    pass


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Post deletion view."""

    pass
