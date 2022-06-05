from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_uses_correct_template_for_authorised_user(self):
        response = self.authorized_client.get('/create/')
        template = 'posts/create_post.html'
        self.assertTemplateUsed(response, template)

    def test_url_uses_correct_template_for_author(self):
        response = self.authorized_client.get('/posts/1/edit/')
        template = 'posts/create_post.html'
        self.assertTemplateUsed(response, template)

    def test_404_for_uncorrect_url(self):
        response_1 = self.guest_client.get('/unexisting_page/')
        response_2 = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response_1.status_code, 404)
        self.assertEqual(response_2.status_code, 404)
