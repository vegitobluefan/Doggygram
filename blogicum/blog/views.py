from django.utils import timezone
from django.http import Http404
from django.conf import settings
from django.shortcuts import get_object_or_404, render

from blog.models import Category, Post


def index(request):
    template = 'blog/index.html'
    context = {
        'post_list': Post.published.all()[:settings.POSTS_SLICE]
    }
    return render(request, template, context)


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

    post_list = category.posts(manager='published').all()
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template, context)
