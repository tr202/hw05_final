from http import HTTPStatus

from django.test import Client, TestCase

TEMPLATES_URLS = {
    '/about/author/': 'about/author.html',
    '/about/tech/': 'about/tech.html',
}


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_get_correct_template(self):
        """Проверка шаблонов для адресов /about/*."""
        for url, template in TEMPLATES_URLS.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов /about/*."""
        for url in TEMPLATES_URLS.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
