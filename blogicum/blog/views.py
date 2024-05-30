from django.utils import timezone
from django.http import Http404
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Post


class PostMixin:
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related(
            'category', 'location', 'author')


class PostListView(PostMixin, ListView):
    model = Post
    template_name = 'blog/index.html'


class Profile(PostMixin, ListView):
    pass
    # template_name = 'blog/profile.html'


class CategoryPostsView(PostMixin, ListView):
    # model = Category
    template = 'blog/category.html'

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'category', 'location', 'author'
        ).filter(
            category__slug=self.kwargs['category_slug'],
            pub_date__lte=timezone.now(),
            is_published=True, category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    if (
        not post.category.is_published or post.pub_date > timezone.now()
            or not post.is_published and post.author != request.user
    ):
        raise Http404(f'Пост под номером {post_id} не найден.')

    context = {
        'post': post
    }
    return render(request, template, context)
