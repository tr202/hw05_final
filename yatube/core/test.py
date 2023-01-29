from django.test import TestCase
from django.test.utils import override_settings

CUSTOM_404_TEMPLATE = {'/uneixisting/': 'core/404.html'}


@override_settings(DEBUG=False)
class Custom404Template(TestCase):
    def test_custom_404_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in CUSTOM_404_TEMPLATE.items():
            with self.subTest(url=url, template=template):
                response = self.client.get(url)
            self.assertTemplateUsed(response, template)
