from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    verbose_name = 'Группа'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите ваш пост')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              help_text='Укажите группу')

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
