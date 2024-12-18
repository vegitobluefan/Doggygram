from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic import TemplateView


class About(TemplateView):
    """View для страницы "О проекте"."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """View для страницы правил."""

    template_name = 'pages/rules.html'


def csrf_failure(request: HttpRequest, reason=''):
    """Кастомная view функция для 403 CSRF failure."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request: HttpRequest, exception):
    """Кастомная view функция для 404 failure."""
    return render(request, 'pages/404.html', status=404)


def server_error_500(request: HttpRequest):
    """Кастомная view функция для 500 failure."""
    return render(request, 'pages/500.html', status=500)
