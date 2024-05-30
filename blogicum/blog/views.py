from django.utils import timezone
from django.http import Http404
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Post


class PostMixin:
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.POST_PAGINATION

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related(
            'category', 'location', 'author')


class PostListView(PostMixin, ListView):
    pass


class Profile(PostMixin, ListView):
    pass


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


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )

    post_list = Post.objects.all()
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template, context)
