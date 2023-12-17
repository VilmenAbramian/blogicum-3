from django.shortcuts import render
from django.views.generic import TemplateView


class AboutDetailView(TemplateView):
    template_name = 'pages/about.html'


class RulesDetailView(TemplateView):
    template_name = 'pages/rules.html'


def rules(request):
    template_name = 'pages/rules.html'
    return render(request, template_name)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def failure_500(request, *args):
    return render(request, 'pages/500.html', status=500)
