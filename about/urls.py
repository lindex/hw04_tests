from django.urls import path

from . import views

urlpatterns = [
    path('about/author/', views.AboutAuthor.as_view(), name='about_author'),
    path('about/tech/', views.Tech.as_view(), name='about_tech'),

]
