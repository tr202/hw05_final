import re

from django.contrib.auth import authenticate
from django.core import mail
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import NoReverseMatch, reverse

from ..forms import User

USER_LOGIN_REVERSE_NAME = 'users:login'
USER_SIGNUP_REVERSE_NAME = 'users:signup'
USER_EMAIL = 'test@test.pr'
VALID_USER_NAME = 'username'
USER_OLD_PSW = 'oldpassword$734563'
USER_NEW_PSW = 'newpassword$43322'
PASSWORD_RESET_URL = reverse('users:password_reset_form')
FIRST_NAME = 'Dohn'
LAST_NAME = 'Dow'


def get_password_reset_confirm_url(uidb64, token):
    try:
        return reverse('users:password_reset_confirm', args=(uidb64, token))
    except NoReverseMatch:
        return 'login/'


def utils_extract_reset_tokens(full_url):
    return re.findall(r'/([\w\-]+)', re.search(r'^http\://.+$', full_url,
                      flags=re.MULTILINE)[0])[3:5]


class PasswordChangeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = {'username': VALID_USER_NAME,
                           'password': USER_OLD_PSW}
        cls.user = User.objects.create_user(**cls.credentials)

    def test_form_change_password(self):
        self.client.post(reverse(
            USER_LOGIN_REVERSE_NAME), self.credentials, follow=True)
        self.assertTrue(
            authenticate(username=VALID_USER_NAME, password=USER_OLD_PSW))
        self.client.post(
            reverse('users:password_change_form'),
            data={
                'old_password': USER_OLD_PSW,
                'new_password1': USER_NEW_PSW,
                'new_password2': USER_NEW_PSW,
            },
            follow=True,
        )
        self.assertIsNone(authenticate(
            username=VALID_USER_NAME, password=USER_OLD_PSW))
        self.assertTrue(authenticate(
            username=VALID_USER_NAME, password=USER_NEW_PSW))


class CreateUserFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_form_create_user(self):
        """Create_user_form увеличивает количество пользователей"""
        exists_users_count = User.objects.count()
        self.guest_client.post(
            reverse(USER_SIGNUP_REVERSE_NAME,),
            data={
                'username': VALID_USER_NAME,
                'password1': USER_OLD_PSW,
                'password2': USER_OLD_PSW,
                'first_name': FIRST_NAME,
                'last_name': LAST_NAME,
                'email': USER_EMAIL,
            },
            follow=True,
        )
        self.assertTrue(User.objects.count() > exists_users_count)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.myclient = Client()
        cls.user = User.objects.create(
            username=VALID_USER_NAME,
            email=USER_EMAIL,
            password=USER_OLD_PSW,)

    def test_password_reset_ok(self):
        """Password reset form, меняет пароль"""
        self.assertEqual(len(mail.outbox), 0)
        self.client.post(
            reverse('users:password_reset_form'),
            {'email': USER_EMAIL}, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        uidb64, token = utils_extract_reset_tokens(msg.body)
        self.myclient.get(get_password_reset_confirm_url(
            uidb64, token), follow=True)
        self.myclient.post(get_password_reset_confirm_url(
            uidb64, 'set-password'),
            {'new_password1': USER_NEW_PSW,
                'new_password2': USER_NEW_PSW}, follow=True)

        self.assertIsNone(authenticate(
            username=VALID_USER_NAME, password=USER_OLD_PSW))
        self.assertTrue(authenticate(
            username=VALID_USER_NAME, password=USER_NEW_PSW))
