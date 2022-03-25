from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

AUTHOR = 'author'
GROUP_SLUG = 'the_group'
GROUP_TITLE = 'Тестовая группа 0'
GROUP_DESCRIPTION = 'Описание групппы'
TEST_TEXT = 'Тестовый текст поста'


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=AUTHOR)
        cls.test_post = Post.objects.create(
            text=TEST_TEXT,
            author=cls.test_user,
        )
        cls.test_group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.templates_and_urls_names = {
            '/': 'posts/index.html',
            '/group/the_group/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        cls.urls = [
            '/create/',
            '/group/the_group/',
            '/',
            '/posts/1/',
        ]

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.user1 = User.objects.create_user(username='not_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        # Cоздаем пользователя-автора поста
        self.user2 = User.objects.get(username=AUTHOR)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in (
            PostsURLTests.templates_and_urls_names.items()
        ):
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_url_for_auth_users(self):
        """Тест доступности страниц"""
        for address in PostsURLTests.urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница возвращает 404."""
        response = self.guest_client.get('/unexisting_page/')
        if settings.DEBUG is False:
            self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pots_editing_for_not_author(self):
        """Пост может редактировать только автор"""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/posts/1/'
        )

    def test_pages_url_for_guests_redirect(self):
        """Неавторизованного пользователя направляет на страницу авторизации
        при попытке создать запись"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, (reverse('users:login') + '?next=/create/')
        )

    def test_comment_by_guest(self):
        """Пост может комментировать только авторизованный пользователь"""
        response = self.guest_client.get('/posts/1/comment/', follow=True)
        self.assertRedirects(
            response, (reverse('users:login') + '?next=/posts/1/comment/')
        )
