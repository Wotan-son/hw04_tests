from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings as s


from . .models import Post, Group

User = get_user_model()


class PostNamespaceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test2',
            description='Тестовое описание 2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованный клиент
        user = PostNamespaceTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def test_url_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', args=[str(self.group.slug)]
            ),
            'posts/profile.html': reverse(
                'posts:profile', args=[str(self.user.username)]
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', args=[str(self.post.pk)]
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit', args={str(self.post.pk)}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_alone(self):
        """Тестим шаблон отдельно без словаря чтобы пройти автотест"""
        template = 'posts/create_post.html'
        reverse_name = reverse('posts:post_create')
        response = self.authorized_client.get(reverse_name)
        self.assertTemplateUsed(response, template)

    def check_post(self, post):
        first_object = post
        post = PostNamespaceTest.post
        test_context = {
            first_object.text: self.post.text,
            first_object.author: self.post.author,
            first_object.pub_date: self.post.pub_date,
            first_object.group: self.post.group,
            first_object.id: self.post.id
        }
        for request, contex in test_context.items():
            with self.subTest(contex=contex):
                self.assertEqual(request, contex)

    def check_group(self, group):
        second_object = group
        group = PostNamespaceTest.group
        group_test_context = {
            second_object.title: self.group.title,
            second_object.slug: self.group.slug,
            second_object.description: self.group.description
        }
        for request, contex in group_test_context.items():
            with self.subTest(contex=contex):
                self.assertEqual(request, contex)

    def check_user(self, user):
        third_object = user
        user = PostNamespaceTest.user
        username = third_object.username
        post_count = third_object.posts.count()
        self.assertEqual(username, self.user.username)
        self.assertEqual(post_count, self.user.posts.count())

    def test_index_shows_correct_context(self):
        """Главная страница показывает получает правильный контекст"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_post(first_object)

    def test_group_list_shows_correct_context(self):
        """Страница группы показывает правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[str(self.group.slug)])
        )
        first_object = response.context['page_obj'][0]
        self.check_post(first_object)
        second_object = response.context['group']
        self.check_group(second_object)

    def test_profile_shows_correct_context(self):
        """Страница профиля показывает правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[str(self.user.username)])
        )
        first_object = response.context['posts']
        self.assertCountEqual(first_object, self.user.posts.all())
        third_object = response.context['user_profile']
        self.check_user(third_object)

    def test_post_detail_shows_correct_context(self):
        """Страница поста показывает правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[str(self.post.pk)])
        )
        first_object = response.context['post']
        self.check_post(first_object)

    def test_post_edit_shows_correct_context(self):
        """Страница редактирования поста показывает правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={str(self.post.pk)})
        )
        first_object = response.context['post']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.check_post(first_object)

    def test_post_create_shows_correct_context(self):
        """Страница создания поста показывает правильный контекст"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_main_page(self):
        """Пост попал на главную страницу"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_in_group_page(self):
        """Пост попал на страницу группы"""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[str(self.group.slug)])
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_in_profile_page(self):
        """Пост попал на страницу профиля"""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[str(self.user.username)])
        )
        self.assertEqual(len(response.context['posts']), 1)

    def test_post_in_another_group_page(self):
        """Пост не попал на страницу другой группы"""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[str(self.group_2.slug)])
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание'
        )
        post_list = [
            Post(
                text=f'Тест {i}',
                author=cls.user_2,
                group=cls.group
            ) for i in range(13)
        ]
        Post.objects.bulk_create(post_list)

    def test_index_first_page(self):
        """Первая страница index содержит 10 постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            s.POSTS_QUANTITY
        )

    def test_index_second_page(self):
        """Вторая страница index содержит 3 поста"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        post_count = Post.objects.all().count()
        last_page_posts = post_count % s.POSTS_QUANTITY
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            last_page_posts
        )

    def test_group_list_first_page(self):
        """Первая страница группы содержит 10 постов"""
        response = self.client.get(
            reverse('posts:group_list', args=[str(self.group.slug)])
        )
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            s.POSTS_QUANTITY
        )

    def test_group_list_second_page(self):
        """Вторая страница группы содержит 3 поста"""
        response = self.client.get(
            reverse('posts:group_list', args=[str(self.group.slug)])
            + '?page=2'
        )
        post_count = Post.objects.all().count()
        last_page_posts = post_count % s.POSTS_QUANTITY
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            last_page_posts
        )

    def test_profile_first_page(self):
        """Первая страница профиля содержит 10 постов"""
        response = self.client.get(
            reverse('posts:profile', args=[str(self.user_2.username)])
        )
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            s.POSTS_QUANTITY
        )

    def test_profile_second_page(self):
        """Вторая страница профиля содержит 3 поста"""
        response = self.client.get(
            reverse('posts:profile', args=[str(self.user_2.username)])
            + '?page=2'
        )
        post_count = Post.objects.all().count()
        last_page_posts = post_count % s.POSTS_QUANTITY
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            last_page_posts
        )
