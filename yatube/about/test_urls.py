from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class AboutUrlTest(TestCase):
    def test_author_url(self):
        """Страница author/ доступна любому пользователю."""
        response = self.client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_url(self):
        """Страница tech/ доступна любому пользователю."""
        response = self.client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_about_and_tech_uses_correct_templates(self):
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
