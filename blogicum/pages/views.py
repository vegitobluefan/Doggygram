from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic import TemplateView


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def csrf_failure(request: HttpRequest, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request: HttpRequest, exception):
    return render(request, 'pages/404.html', status=404)


def server_error_500(request: HttpRequest):
    return render(request, 'pages/500.html', status=500)
