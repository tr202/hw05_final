from mixer.backend.django import mixer

from django.test import Client, TestCase
from django.test.utils import override_settings

from posts.models import User

CUSTOM_404_TEMPLATE = {'/uneixisting/': 'core/404.html'}
CUSTOM_403CSRF_TEMPLATE = 'core/403csrf.html'
CSRF_FORM_URL = '/create/'


@override_settings(DEBUG=False)
class Custom404Template(TestCase):
    def setUp(self):
        self.user = mixer.blend(User)
        self.authorized_client = Client(enforce_csrf_checks=True)
        self.authorized_client.force_login(self.user)

    def test_custom_403csrf_template(self):
        response = self.authorized_client.post(CSRF_FORM_URL)
        self.assertTemplateUsed(response, CUSTOM_403CSRF_TEMPLATE)

    def test_custom_404_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in CUSTOM_404_TEMPLATE.items():
            with self.subTest(url=url, template=template):
                response = self.client.get(url)
            self.assertTemplateUsed(response, template)
