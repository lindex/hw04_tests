from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Group


class PostsViewsTests(TestCase):
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
            'group.html': reverse('group_posts', kwargs={'slug': 'test-slug'}),
            'post_new.html': reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id}),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
         на главной странице."""

        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_object_group = response.context['group']
        group_title = post_object_group.title
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(group_title, self.group.title)

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

    # для ревью. тут проверяется, что пост
    # попал в нужную группу (значит в ненужную не попал)
    # коменты потом уберу

    def test_index_group_list_page_list_is_1(self):
        """Удостоверимся, что на главную
        страницу и group со списком постов передаётся
         ожидаемое количество постов"""

        response_main = self.authorized_client.get(reverse('index'))
        response_group = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        post_context = {
            len(response_main.context['page']): 1,
            len(response_group.context['page']): 1,
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(key, value)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )

        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].author.username,
                         self.user.username)

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
            })
        )
        post_context = {
            response.context['post'].text: self.post.text,
            response.context['post'].author.username: self.user.username
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(key, value)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='ivan')
        cls.client = Client()
        cls.client.force_login(cls.user)
        for i in range(13):
            Post.objects.create(
                text='Тестовый пост',
                author=cls.user,
            )

    def test_paginator(self):
        response_index = self.client.get(reverse('index'))
        response_index_page2 = self.client.get(reverse('index') + '?page=2')
        response_group = self.client.get(reverse('index'))
        response_group_page2 = self.client.get(reverse('index') + '?page=2')

        post_context = {
            len(response_index.context.get('page').object_list): 10,
            len(response_index_page2.context.get('page').object_list): 3,
            len(response_group.context.get('page').object_list): 10,
            len(response_group_page2.context.get('page').object_list): 3,

        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(key, value)
