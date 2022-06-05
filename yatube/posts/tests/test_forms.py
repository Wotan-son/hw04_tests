from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from . .models import Post, Group

User = get_user_model()


class PostFormsTest(TestCase):
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
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованный клиент
        user = PostFormsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def test_post_create_form_creates_post(self):
        """Форма создания поста создает запись в БД"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст',
            'group': self.group.pk,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[str(self.user.username)])
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_post_edit_form_change_post(self):
        """Форма редактирования поста не создает доп. запись в БД"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
        }
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[str(self.post.id)]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[str(self.post.id)]))
        self.assertEqual(Post.objects.count(), post_count)
