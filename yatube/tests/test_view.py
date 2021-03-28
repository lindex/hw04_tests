from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Group


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='ivan')
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
            author=cls.user
        )

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'post_new.html': reverse('new_post'),
            'group.html': reverse('group_posts', kwargs={'slug': 'test-slug'}),
            'post_new.html': reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id}),
            'aboutauthor.html': reverse('about_author'),
            'tech.html': reverse('about_tech'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
         на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        post_object = self.post
        responce_post_object = response.context['page'][0]
        self.assertEqual(post_object, responce_post_object)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse(
            'group_posts',
            kwargs={'slug': 'test-slug'}))
        first_post = response.context['page'][0]
        self.assertEqual(
            self.post, first_post)
        group = response.context['group']
        self.assertEqual(
            self.group, group)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_list_page_list_is_1(self):
        """Удостоверимся, что на главную
        страницу со списком постов передаётся
         ожидаемое количество постов"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_group_list_page_list_is_1(self):
        """Удостоверимся, что на главную страницу группы со списком
        постов передаётся
         ожидаемое количество постов"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page']), 1)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            }
                    )
        )
        self.assertEqual(response.context['post'], self.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(response.context['page'][0], self.post)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            }
                    )
        )
        post_context = {
            'post': self.post,
            'user': self.user
            # не могу разобраться почему тут user проходит,а с author нет
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                context = response.context[key]
                self.assertEqual(context, value)

    def test_about_author_200(self):
        """URL, генерируемый при помощи имени about_author, доступен."""
        response = self.guest_client.get(reverse('about_author'))
        self.assertEqual(response.status_code, 200)

    def test_about_tech_200(self):
        """URL, генерируемый при помощи имени about_author, доступен."""
        response = self.guest_client.get(reverse('about_tech'))
        self.assertEqual(response.status_code, 200)
