from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.post.author}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }

    def setUp(self):
        self.guest_client = Client()
        user = PostUrlTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_uses_correct_template_for_authorised_user(self):
        response = self.authorized_client.get('/create/')
        template = 'posts/create_post.html'
        self.assertTemplateUsed(response, template)

    def test_url_uses_correct_template_for_author(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        template = 'posts/create_post.html'
        self.assertTemplateUsed(response, template)

    def test_404_for_uncorrect_url(self):
        response_1 = self.guest_client.get('/unexisting_page/')
        response_2 = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response_1.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response_2.status_code, HTTPStatus.NOT_FOUND)
