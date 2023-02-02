import shutil

from django import forms
from django.conf import settings as s
from django.core.cache import cache
from django.db.models.fields.files import ImageFieldFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from mixer.backend.django import mixer

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User

from .config_tests import (FOLLOWED_AUTHORS_TAPE, FOLLOW_UNFOLLOW,
                           INDEX_PAGE,
                           PAGES_SHOW_SINGLE_POST,
                           PAGES_USES_CREATE_TEMPLATE,
                           PAGE_SHOW_CORRECT_CONTEXT,
                           PAGINATOR_TEST_PAGES,
                           POST_APPEAR_ON_PAGES, TEMP_MEDIA_ROOT, UPLOADED, )
from .utils import create_posts, get_obj_test_urls


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_not_folowed = mixer.blend(User)
        cls.author = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.image = UPLOADED
        cls.posts = mixer.cycle(
            s.PAGE_POSTS_COUNT).blend(
                Post, author=cls.user, group=cls.group, image=cls.image)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_not_follow = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_follow.force_login(self.user_not_folowed)
        self.post = Post.objects.last()

    def test_authorized_can_follow_unfollow(self):
        """Авторизованный  пользователь может подписываться и отписываться"""
        Follow.objects.all().delete()
        self.authorized_client.get(
            reverse(FOLLOW_UNFOLLOW['follow'], kwargs={
                'username': self.author.username}))
        self.assertTrue(self.user.follower.filter(author=self.author).exists())
        self.authorized_client.get(
            reverse(FOLLOW_UNFOLLOW['unfollow'], kwargs={
                'username': self.author.username}))
        self.assertFalse(
            self.user.follower.filter(author=self.author).exists())

    def test_new_post_appear_on_follower_and_not_on_another(self):
        """Новый пост появляется только у подписанных"""
        self.follow = mixer.blend(Follow, user=self.user, author=self.author)
        post = mixer.blend(Post, author=self.author)
        cache.clear()
        response = self.authorized_client.get(
            reverse(FOLLOWED_AUTHORS_TAPE))
        page_obj_list = response.context.get('page_obj')
        contains = post in page_obj_list
        self.assertTrue(contains)
        response = self.authorized_client_not_follow.get(
            reverse(FOLLOWED_AUTHORS_TAPE))
        page_obj_list = response.context.get('page_obj')
        contains = post in page_obj_list
        self.assertFalse(contains)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        pages = PAGE_SHOW_CORRECT_CONTEXT
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                cache.clear()
                response = self.authorized_client.get(urls[page].url)
            page_obj_list = response.context.get('page_obj')
            for post in page_obj_list:
                self.assertEqual(post.image.__class__, ImageFieldFile)
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.author, self.user)
                self.assertIsInstance(post, Post)

    def test_pages_show_single_post(self):
        """Страницы создания и редактирования"""
        pages = PAGES_USES_CREATE_TEMPLATE
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(urls[page].url)
            context = response.context
            self.assertIsInstance(context.get('form'), PostForm)
        self.assertEqual(context.get('post'), self.post)
        self.assertEqual(context.get('is_edit'), True)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_only_show_single_post(self):
        """Один пост отфильтрованный по id - detail."""
        pages = PAGES_SHOW_SINGLE_POST
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(urls[page].url)
        page_obj_list = response.context.get('post'),
        self.assertEqual(page_obj_list[0].image.__class__, ImageFieldFile)
        self.assertEqual(len(page_obj_list), 1)
        self.assertIsInstance(page_obj_list[0], Post)
        self.assertEqual(page_obj_list[0].pk, self.post.pk)

    def test_appear_greated_post(self):
        """Созданный пост появляется на страницах"""
        pages = POST_APPEAR_ON_PAGES
        self.post = create_posts(1, self)[0]
        Post.save(self.post)
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                cache.clear()
                response = self.authorized_client.get(urls[page].url)
            page_obj_list = response.context.get('page_obj')
            contains = self.post in page_obj_list
            self.assertTrue(contains)

    def test_cached_pages(self):
        """Запись остаётся в кэш"""
        cache.clear()
        mixer.blend(Post)
        content = self.client.get(INDEX_PAGE).content
        Post.objects.all().delete()
        after_del_content = self.client.get(INDEX_PAGE).content
        self.assertEqual(content, after_del_content)
        cache.clear()
        after_clear_cache_content = self.client.get(INDEX_PAGE).content
        self.assertNotEqual(content, after_clear_cache_content)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.test_urls = get_obj_test_urls(cls, PAGINATOR_TEST_PAGES)
        cls.posts = mixer.cycle(
            s.PAGE_POSTS_COUNT * 2).blend(
                Post, author=cls.user, group=cls.group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Проверяем paginator на всех страницах"""
        for page in PAGINATOR_TEST_PAGES:
            with self.subTest(page=page):
                cache.clear()
                response = self.authorized_client.get(self.test_urls[page].url)
                self.assertEqual(
                    len(response.context['page_obj']), s.PAGE_POSTS_COUNT)
                response = self.authorized_client.get(
                    self.test_urls[page].url + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), s.PAGE_POSTS_COUNT)
