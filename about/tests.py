from django.urls import reverse


def test_about_author_200(self):
    """URL, генерируемый при помощи имени about_author, доступен."""
    response = self.guest_client.get(reverse('about_author'))
    self.assertEqual(response.status_code, 200)


def test_about_tech_200(self):
    """URL, генерируемый при помощи имени about_tech, доступен."""
    response = self.guest_client.get(reverse('about_tech'))
    self.assertEqual(response.status_code, 200)


def testabout_pages_use_correct_template(self):
    """URL-адрес использует соответствующий шаблон."""
    templates_pages_names = {
        'aboutauthor.html': reverse('about_author'),
        'tech.html': reverse('about_tech'),
    }

    for template, reverse_name in templates_pages_names.items():
        with self.subTest(reverse_name=reverse_name):
            response = self.authorized_client.get(reverse_name)
            self.assertTemplateUsed(response, template)
