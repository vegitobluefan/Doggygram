from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic import TemplateView


class About(TemplateView):
    """View for about page in header."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """View for rules page in header."""

    template_name = 'pages/rules.html'


def csrf_failure(request: HttpRequest, reason=''):
    """Custom view for 403 CSRF failure."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request: HttpRequest, exception):
    """Custom view for 404 failure."""
    return render(request, 'pages/404.html', status=404)


def server_error_500(request: HttpRequest):
    """Custom view for 500 failure."""
    return render(request, 'pages/500.html', status=500)
