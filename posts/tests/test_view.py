from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Group
from posts.views import PAGINATE_BY


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
        cls.group2 = Group.objects.create(
            title='TestGroupName2',
            slug='test-slug2',
            description='Тестовая группа2',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

    def check_post_fields(self, response):
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group_id
        self.assertIn('page', response.context)
        self.assertEqual(post_group_0, self.post.group_id)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  kwargs={'slug': self.group.slug}),
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

        response_index = self.authorized_client.get(reverse('index'))
        self.check_post_fields(response_index)

    def test_group_correct_context(self):
        """Шаблон group сформирован с правильным контекстом
         на главной странице."""

        response = self.authorized_client.get(
            reverse(
                'group_posts',
                kwargs={'slug': self.group.slug}))
        group_object = response.context['group']
        self.assertEqual(group_object.title, self.group.title)
        self.assertEqual(
            group_object.description, self.group.description)

        self.check_post_fields(response)

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

    def test_index_group_list_page_post_is_1(self):
        """Удостоверимся, что на главную
        страницу и group со списком постов передаётся
         нужный пост"""

        page_list = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
        )

        for url in page_list:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertContains(response, self.post.text)

    def test_new_post_not_appear_group2(self):
        """Удостоверимся, что на
        страницу и group2 со списком постов не передаётся
         пост"""
        response = self.authorized_client.get(
            reverse(
                'group_posts', kwargs={'slug': self.group2.slug}))
        self.assertNotContains(response, self.post.text)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        post = response.context['post']
        self.assertIn('post', response.context)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.username,
                         self.user.username)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username}))

        self.assertIn('page', response.context)
        self.assertEqual(response.context['author'], self.user)
        self.check_post_fields(response)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            })
        )
        self.assertIn('post', response.context)
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
        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Описание',
        )
        cls.POST_NUMBER = 3

        objs = [
            Post(text=f'Текст тестового поста {i}',
                 group=cls.group,
                 author=cls.user)
            for i in range(PAGINATE_BY + cls.POST_NUMBER)
        ]
        Post.objects.bulk_create(objs)

    def test_pages_contains_records(self):
        response_pages = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}))
        pages_list = {PAGINATE_BY: 1, self.POST_NUMBER: 2}
        for records, page_number in pages_list.items():
            for page in response_pages:
                response = self.client.get(page, {'page': page_number})
                with self.subTest():
                    self.assertEqual(
                        len(response.context.get('page').object_list),
                        int(records))
