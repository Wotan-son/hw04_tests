from django.test import TestCase, Client


class UsersUrlTest(TestCase):
    def test_signup_url(self):
        """Страница signup/ доступна любому пользователю."""
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        """Страница login/ доступна любому пользователю."""
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)

    def test_users_app_urls_uses_correct_templates(self):
        """Url-запросы используют корректные шаблоны"""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)