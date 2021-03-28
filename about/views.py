from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'aboutauthor.html'


class Tech(TemplateView):
    template_name = 'tech.html'
