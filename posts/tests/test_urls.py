from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import Post, User, Group


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='ivan')
        cls.user2 = User.objects.create_user(username='igor')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='TestGroupName',
            slug='test-slug',
            description='Тестовая группа',
        )

        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user,
        )

        cls.post2 = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user2,
        )

    def test_new_posts_url_guest_client(self):
        """Страница /new/ создания поста не доступна анонимному пользователю"""
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_template(self):
        """Какой шаблон вызывается для страниц:"""
        templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{self.group.slug}/',
            'post_new.html': f'/{self.user.username}/{self.post.id}/edit/'
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_guest(self):
        """Доступность страницы редактирования поста для неавт. пользователя"""
        response = self.guest_client.get(f'/{self.user.username}/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_authorised_not_author(self):
        """Доступность страницы редактирования поста для не автора поста"""
        response = self.authorized_client.get(
            f'/{self.user2.username}/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_redirect_not_author(self):
        """редирект со страницы /<username>/<post_id>/edit/для тех,
        у кого нет прав доступа к этой странице."""
        url = f'/{self.user.username}/{self.post2.id}/edit'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_urls_guest_client_200(self):
        """Тест страниц 200 для анонима"""
        test_urls = [
            '/',
            '/about/author/',
            '/about/tech/',
            f'/group/{self.group.slug}/',
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_client_200(self):
        """Тест страниц 200 для пользвателя"""
        test_urls = [
            f'/group/{self.group.slug}/',
            '/new/',
            f'/{self.user.username}/',
            f'/{self.user.username}/1/',
            f'/{self.user.username}/1/edit/'
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
