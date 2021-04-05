from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='ivan')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_about_pages_status(self):
        """Проверка доступности страниц about_author
         about_tech для неавторизованных пользователей"""
        url_code_pages = ['about_author', 'about_tech']
        for url in url_code_pages:
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def testabout_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/aboutauthor.html': reverse('about_author'),
            'about/tech.html': reverse('about_tech'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
