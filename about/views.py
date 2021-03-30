from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'about/aboutauthor.html'


class Tech(TemplateView):
    template_name = 'about/tech.html'
