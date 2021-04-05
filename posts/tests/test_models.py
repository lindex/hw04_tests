from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()
        cls.user = User.objects.create_user(username='alex')
        cls.client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Текст тестового поста', author=cls.user
        )

        cls.group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='Ссылка',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )

    def test_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'group': 'group',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = self.post
        field_help_texts = {
            'text': 'Напишите ваш пост',
            'group': 'Укажите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_str_group_title(self):
        post_context = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(key, value)
