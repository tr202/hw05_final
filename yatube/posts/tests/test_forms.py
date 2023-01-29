import shutil

from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from mixer.backend.django import mixer

from posts.models import Group, Post, User

from .config_tests import (COMMENTS_UNAUTHORIZED_REDIRECT,
                           COMMENTS_URL,
                           TEMP_MEDIA_ROOT, UPLOADED)
from .utils import get_obj_test_urls


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_no_post_author = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user, group=cls.group)
        cls.test_urls = get_obj_test_urls(cls)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_only_authorized_can_comment(self):
        """Неавторизованный не может комментировать"""
        response = self.client.post(
            self.test_urls['post_detail'].url + COMMENTS_URL,
            data={'text': 'Проверка'}, follow=True)
        self.assertContains(response, COMMENTS_UNAUTHORIZED_REDIRECT)

    def test_comment_appear_on_detail(self):
        """Комментарий появляется на странице поста"""
        response = self.authorized_client.get(
            self.test_urls['post_detail'].url)
        comments_before = response.context.get('comments')
        response = self.authorized_client.post(
            self.test_urls['post_detail'].url + COMMENTS_URL,
            data={'text': 'Проверка'}, follow=True)
        comments_after = response.context.get('comments')
        self.assertNotEqual(len(comments_before), len(comments_after))

    def test_form_edit_post_change_post(self):
        """Edit_post изменяет пост"""
        post_text = Post.objects.get(pk=self.post.pk).text
        self.authorized_client.post(
            reverse(f"{self.test_urls['post_edit'].app_name}"
                    f":{self.test_urls['post_edit'].page_name}",
                    kwargs=self.test_urls['post_edit'].kwargs),
            data={'text': post_text + 'changed_part'}, follow=True)
        self.assertNotEqual(post_text, Post.objects.get(pk=self.post.pk).text)

    def test_form_create_post(self):
        """Create_post_form_with_image увеличивает количество постов"""
        exists_post_count = Post.objects.count()
        self.authorized_client.post(
            reverse(
                f"{self.test_urls['post_create'].app_name}"
                f":{self.test_urls['post_create'].page_name}",),
            data={'text': 'Проверка',
                  'image': UPLOADED, },
            follow=True,
        )
        self.assertTrue(Post.objects.count() > exists_post_count)
        latest_post = Post.objects.latest('pub_date')
        self.assertEqual(latest_post.text, 'Проверка')
        self.assertEqual(latest_post.author, self.user)
