from django.test import TestCase, Client
from django.urls import reverse

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
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_urls_template(self):
        """Какой шаблон вызывается для страниц:"""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  kwargs={'slug': self.group.slug}),
            'post_new.html': reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id})
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_guest(self):
        """Доступность страницы редактирования поста для гостя"""
        response = self.guest_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_authorised_not_author(self):
        """Недооступность страницы редактирования поста для не автора поста"""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post2.id}))
        self.assertEqual(response.status_code, 404)

    def test_post_edit_redirect_not_author(self):
        """редирект со страницы /<username>/<post_id>/edit/для тех,
        у кого нет прав доступа к этой странице."""
        response = self.guest_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_urls_guest_client_200(self):
        """Тест страниц 200 для анонима"""
        test_urls = [
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_authorized_client_200(self):
        """Тест страниц 200 для авториз. пользователя"""
        test_urls = [
            reverse('index'),
            reverse('new_post'),
            reverse('profile',
                    kwargs={'username': self.user.username}),
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}),
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}),
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)
