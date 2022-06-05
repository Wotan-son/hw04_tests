from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group_task = PostModelTest.group
        expected_group_name = group_task.title
        post_task = PostModelTest.post
        expected_post_name = post_task.text[:15]
        self.assertEqual(expected_group_name, str(group_task))
        self.assertEqual(expected_post_name, str(post_task))

    def test_verbose_name(self):
        task = PostModelTest.post
        verboses_fields = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in verboses_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        task = PostModelTest.post
        help_text_fields = {
            'text': 'Текст Вашего поста',
            'group': 'Группа, к которой относится пост'
        }
        for value, expected in help_text_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).help_text, expected)
