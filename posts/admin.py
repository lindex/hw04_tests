from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # добавим в начало столбец pk
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = ('-пусто-')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    empty_value_display = ('-пусто-')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
