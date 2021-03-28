from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Group


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='ivan')
        cls.user2 = User.objects.create_user(username='gena')
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

        cls.username = cls.post.author.username

        cls.resp_guest_main = cls.guest_client.get(reverse('index'))

        cls.resp_guest_new = cls.guest_client.get(reverse('new_post'))
        cls.resp_user_new = cls.authorized_client.get(reverse('new_post'))

        cls.resp_guest_group = cls.guest_client.get(reverse(
            'group_posts',
            kwargs={'slug': 'test-slug'}))
        cls.resp_user_group = cls.authorized_client.get(reverse(
            'group_posts',
            kwargs={'slug': 'test-slug'}))
        cls.resp_user_id_post = cls.guest_client.get(reverse(
            'profile',
            kwargs={'username': 'ivan'}))

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        self.assertEqual(self.resp_guest_main.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/slug/ доступна любому пользователю."""

        self.assertEqual(self.resp_guest_group.status_code, 200)

    def test_task_list_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""

        self.assertEqual(self.resp_user_new.status_code, 200)

    def test_group_url_exists_at_desired_location_authorized(self):
        """Страница /group/slug/ доступна авторизованному
        пользователю."""
        self.assertEqual(self.resp_user_group.status_code, 200)

    def test_new_url_redirect_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        self.assertEqual(self.resp_guest_new.status_code, 302)

    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина.
        """
        self.assertRedirects(
            self.resp_guest_new, '/auth/login/?next=/new/')

    def test_profile_url_authorised(self):
        """Страница профайла пользователя доступна по /<username>/"""
        response = self.authorized_client.get(reverse(
            'profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_url_post(self):
        """Пост пользователя доступен по post_id"""
        response = self.authorized_client.get(reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_url_edit_post(self):
        """ Проверка на доступность страницы редактирования поста
         /<username>/<post_id>/edit/"""
        response = self.guest_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_url_edit_post_autorized_author(self):
        """ Проверка на доступность страницы редактирования поста
         /<username>/<post_id>/edit/ для автора поста"""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_url_edit_post_autorized_no_author(self):
        """ Проверка на доступность страницы редактирования поста
         /<username>/<post_id>/edit/ для не автора поста"""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post2.id}))
        self.assertEqual(response.status_code, 404)

    def test_url_edit_redir_post(self):
        """  правильно ли работает редирект со страницы
         /<username>/<post_id>/edit/ для тех, у кого нет
          прав доступа к этой странице."""
        url = f'/{self.user.username}/{self.post2.id}/edit'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 301)
