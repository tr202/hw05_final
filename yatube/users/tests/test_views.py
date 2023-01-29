from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User

UNAUTHORIZED_USER_TEST_URLS = {
    'users/signup.html': reverse('users:signup'),
    'users/login.html': reverse('users:login'),
    'users/password_reset_form.html': reverse(
        'users:password_reset_form'),
    'users/password_reset_done.html': reverse(
        'users:password_reset_done'),
    'users/logged_out.html': reverse('users:logout'),
    'users/password_reset_confirm.html': reverse(
        'users:password_reset_confirm',
        kwargs={'uidb64': '<uidb64>', 'token': 'token'}),
}
AUTHORIZED_USER_TEST_URLS = {
    'users/password_change_form.html': reverse(
        'users:password_change_form'),
    'users/password_change_done.html': reverse(
        'users:password_change_done'),
    'users/password_reset_complete.html': reverse(
        'users:password_reset_confirm'),
}


class UserViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_unautorized_users_urls(self):
        """Неавторизованые Users URL."""
        for template, reverse_name in UNAUTHORIZED_USER_TEST_URLS.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_autorized_users_urls(self):
        """Авторизованые Users URL."""
        for template, reverse_name in AUTHORIZED_USER_TEST_URLS.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
