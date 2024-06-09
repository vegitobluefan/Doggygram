from django.utils import timezone
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
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


post_objects = Post.objects.all()


def get_post_queryset(self):
    return self.select_related(
        'category', 'location', 'author'
    ).filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
        is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class Profile(ListView):
    """User's profile view."""

    template_name = 'blog/profile.html'
    paginate_by = settings.POST_PAGINATION

    def get_user(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        queryset = self.get_user().author_profile.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
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
        return get_post_queryset(post_objects)


class PostBaseMixin:
    """Base mixin for post views."""

    model = Post
    slug_field = 'id'
    slug_url_kwarg = 'post_id'


class PostDetailView(PostBaseMixin, DetailView):
    """Certain post view."""

    template_name = 'blog/detail.html'

    def get_queryset(self):
        post = post_objects.get(id=self.kwargs['post_id'])
        if (
            not post.category.is_published
            or post.pub_date > timezone.now()
            or not post.is_published
        ) and post.author != self.request.user:
            raise Http404('Пост не найден.')

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CategoryPostsView(ListView):
    """View for posts in certain category."""

    template_name = 'blog/category.html'
    paginate_by = settings.POST_PAGINATION

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return self.get_category().posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class CommentBaseMixin(LoginRequiredMixin):
    """Mixin for comments."""

    model = Comment
    template_name = 'blog/comment.html'


class CommentEditDeleteMixin(CommentBaseMixin):
    """Mixin for editing or deleting comment views."""

    slug_field = 'id'
    slug_url_kwarg = 'comment_id'

    def get_queryset(self):
        comment = Comment.objects.get(pk=self.kwargs['comment_id'])

        if comment.author != self.request.user:
            raise Http404('Комментарий не найден.')
        return super().get_queryset()

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentCreateView(CommentBaseMixin, CreateView):
    """View for comment creation."""

    form_class = CommentForm

    def get_post(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.get_post().pk
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


class PostEditView(PostBaseMixin, LoginRequiredMixin, UpdateView):
    """Post editing view."""

    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = post_objects.get(id=self.kwargs['post_id'])

        if self.request.user != post.author:
            return redirect(
                'blog:post_detail', post_id=post.pk
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        post = post_objects.get(id=self.kwargs['post_id'])
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post.id}
        )


class PostDeleteView(PostBaseMixin, LoginRequiredMixin, DeleteView):
    """Post deletion view."""

    template_name = 'blog/create.html'

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:index')
