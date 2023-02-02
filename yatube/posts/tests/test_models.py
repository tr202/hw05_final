from django.core.validators import validate_unicode_slug
from django.db.transaction import TransactionManagementError
from django.db.utils import IntegrityError
from django.test import TestCase

from mixer.backend.django import mixer

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User, username='auth')
        cls.group = mixer.blend(
            Group,
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.post = mixer.blend(
            Post,
            author=cls.user,
            text='Тестовый пост' * 15,
        )
        cls.comment = mixer.blend(Comment)
        cls.follow = mixer.blend(Follow)

    def test_on_delete_comment_follow(self):
        """Тест удаление подписки и комментария вместе с постом и автором"""
        post = mixer.blend(Post)
        comment_id = mixer.blend(Comment, post=post).pk
        follow_id = mixer.blend(Follow, author=post.author).pk
        verify = (
            Comment.objects.filter(pk=comment_id).exists()
            and Follow.objects.filter(pk=follow_id).exists())
        self.assertTrue(verify)
        Post.objects.filter(pk=post.pk).delete()
        self.assertFalse(Comment.objects.filter(pk=comment_id).exists())
        User.objects.filter(pk=post.author.pk).delete()
        self.assertFalse(Follow.objects.filter(pk=follow_id).exists())

    def test_follow_constraints(self):
        """Тест ограничения БД подписки"""
        verify_unic, verify_same_author = True, True
        try:
            Follow.objects.create(
                user=self.follow.user, author=self.follow.author)
        except IntegrityError:
            verify_unic = False
        try:
            Follow.objects.create(
                user=self.follow.user, author=self.follow.user)
        except TransactionManagementError:
            verify_same_author = False
        self.assertFalse(verify_unic and verify_same_author)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        for obj in (self.comment, self.post,):
            self.assertEqual(obj.text[:15], str(obj))
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(
            self.follow.user.username + ' подписан на '
            + self.follow.author.username, str(self.follow))

    def test_group_have_correct_slug(self):
        """Проверяем, наличие и корректность slug по умолчанию"""
        task = PostModelTest.group
        validate_unicode_slug(task.slug)

    def test_greated_post_has_expected_group(self):
        """Проверка, что пост не попал в чужую группу."""
        group = Group.objects.get(title='Тестовая группа')
        self.post = Post.objects.create(
            author=self.user,
            text='Пост проверки соответствия группы',
            group=group,
        )
        self.assertEqual(Post.objects.get(pk=self.post.pk).group, group)
