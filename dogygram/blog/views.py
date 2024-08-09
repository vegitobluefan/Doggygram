from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post, User
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)


def filtering(posts):
    """Функция для устранения повторяющегося кода."""
    return posts.select_related(
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
    author = None

    def get_queryset(self):
        """Получаем список постов автора."""
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.author == self.request.user:
            queryset = self.author.posts.annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
            return queryset

        return filtering(self.author.posts)

    def get_context_data(self, **kwargs):
        """Получаем контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfieEditView(LoginRequiredMixin, UpdateView):
    """User's profile editing view."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Получаем пользователя."""
        return self.request.user

    def get_success_url(self):
        """Адрес успешного действия."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostListView(ListView):
    """Post list view."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = settings.POST_PAGINATION
    queryset = filtering(Post.objects)


class PostBaseMixin:
    """Base mixin for post views."""

    model = Post
    slug_field = 'id'
    slug_url_kwarg = 'post_id'


class PostDetailView(PostBaseMixin, DetailView):
    """Certain post view."""

    template_name = 'blog/detail.html'

    def get_object(self):
        """Получаем пост."""
        post = super().get_object()
        if (
            not post.category.is_published
            or post.pub_date > timezone.now()
            or not post.is_published
        ) and post.author != self.request.user:
            raise Http404('Пост не найден.')

        return post

    def get_context_data(self, **kwargs):
        """Получаем контекст."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CategoryPostsView(ListView):
    """View for posts in certain category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = settings.POST_PAGINATION
    category = None

    def get_queryset(self):
        """Получаем посты определённой категории."""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return filtering(self.category.posts)

    def get_context_data(self, **kwargs):
        """Получаем контекст."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentBaseMixin(LoginRequiredMixin):
    """Mixin for comments."""

    model = Comment
    template_name = 'blog/comment.html'


class CommentCreateView(CommentBaseMixin, CreateView):
    """View for comment creation."""

    form_class = CommentForm

    def form_valid(self, form):
        """Проверяем валидность формы."""
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        """Получаем адрес успешного действия."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentEditDeleteMixin(CommentBaseMixin):
    """Mixin for editing or deleting comment views."""

    slug_field = 'id'
    slug_url_kwarg = 'comment_id'

    def get_object(self):
        """Получаем комментарий."""
        comment = super().get_object()
        if comment.author != self.request.user:
            raise Http404('Комментарий не найден.')
        return comment

    def get_success_url(self):
        """Получаем адрес успешного действия."""
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
        """Проверяем валидность формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Получаем адрес успешного действия."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostEditDeleteMixin(PostBaseMixin, LoginRequiredMixin):
    """Mixin for post creation and deletion views."""

    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        """Диспатчеризация."""
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author:
            return redirect(
                'blog:post_detail', post_id=post.pk
            )

        return super().dispatch(request, *args, **kwargs)


class PostEditView(PostEditDeleteMixin, UpdateView):
    """Post editing view."""

    form_class = PostForm

    def get_success_url(self):
        """Получаем адрес успешного действия."""
        post = Post.objects.get(pk=self.kwargs['post_id'])
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post.pk}
        )


class PostDeleteView(PostEditDeleteMixin, DeleteView):
    """Post deletion view."""

    def get_context_data(self, **kwargs):
        """Получаем контекст."""
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        """Получаем адрес успешного действия."""
        return reverse('blog:index')
