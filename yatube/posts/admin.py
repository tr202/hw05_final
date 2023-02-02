from django.conf import settings
from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Comment, Follow, Group, Post

VERBOSE_NAME_FOR_GET_POST_AUTHOR_NAME = 'Автор поста'
VERBOSE_NAME_FOR_GET_POST_TEXT = 'Начало статьи'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'user',
                    'author',
                    'follow_at',
                    )
    search_fields = ('user', 'author')
    list_filter = ('follow_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'created',
                    'author',
                    'text',
                    'get_post_text',
                    'get_post_author_name',
                    )
    list_editable = ('text',)
    search_fields = ('text', 'created', 'post', )
    list_filter = ('created',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 80})},
    }

    def get_post_author_name(self, comment):
        return (f'{comment.post.author.first_name}'
                f'{comment.post.author.last_name}')
    get_post_author_name.__name__ = 'Автор статьи'

    def get_post_text(self, comment):
        return comment.post.text[:200]
    get_post_text.__name__ = 'Начало статьи'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group',
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
