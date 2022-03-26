import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

FIRST_PAGE_COUNT = 10
SECOND_PAGE_COUNT = 1
FIRST_ELEMENT_ON_PAGE = 0
AUTHOR = 'author'
GROUP_SLUG = 'the_group'
GROUP_TITLE = 'Тестовая группа 0'
GROUP_DESCRIPTION = 'Описание групппы'
ANOTHER_GROUP_SLUG = 'another_group1'
ANOTHER_GROUP_TITLE = 'Тестовая группа 1'
TEST_TEXT = 'Тестовый текст поста'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=IMAGE,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.main_author = User.objects.create_user(username=AUTHOR)
        cls.test_group0 = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.test_group1 = Group.objects.create(
            title=ANOTHER_GROUP_TITLE,
            slug=ANOTHER_GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        Post.objects.create(
            text=TEST_TEXT,
            author=cls.main_author,
            group=cls.test_group1,
            image=UPLOADED
        )
        Post.objects.bulk_create([
            Post(
                text=TEST_TEXT,
                author=cls.main_author,
                group=cls.test_group0,
                image=UPLOADED
            ) for i in range(12)
        ])
        Comment.objects.create(
            text=TEST_TEXT,
            author=cls.main_author,
            post=Post.objects.get(id='1')
        )
        cls.reverse_names = [
            reverse('posts:main_page'),
            reverse('posts:group_list', kwargs={'slug': GROUP_SLUG}),
            reverse('posts:profile', kwargs={'username': AUTHOR}),
        ]
        cls.templates_pages_names = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': GROUP_SLUG}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': AUTHOR}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': '1'}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}): (
                'posts/create_post.html'
            ),
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # автор
        self.user2 = User.objects.get(username=AUTHOR)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user2)
        # другой авторизованный клиент
        self.user1 = User.objects.create_user(username='not_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        # гость
        self.guest_client = Client()
        # посты от групп
        self.post_created_from_test_group0 = (
            PostsPagesTests.test_group0.posts.get(id='2')
        )
        self.post_created_from_test_group1 = (
            PostsPagesTests.test_group1.posts.get(id='1')
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in (
            PostsPagesTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(reverse('posts:main_page'))
        )
        posts_from_context = response.context['posts'][FIRST_ELEMENT_ON_PAGE]
        posts = Post.objects.all()[FIRST_ELEMENT_ON_PAGE]
        self.assertEqual(posts_from_context, posts)

        # Проверяем картинки
        self.assertEqual(posts_from_context.image, posts.image)

        # Проверяем, что пост созданный от группы, есть на главной станице
        posts_from_context1 = response.context['posts']
        self.assertIn(self.post_created_from_test_group0, posts_from_context1)
        self.assertIn(self.post_created_from_test_group1, posts_from_context1)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(
                reverse('posts:group_list', kwargs={'slug': GROUP_SLUG})
            )
        )
        posts_from_context1 = response.context['posts'][FIRST_ELEMENT_ON_PAGE]
        filtered_by_test_group0 = (
            self.test_group0.posts.all()[FIRST_ELEMENT_ON_PAGE]
        )
        self.assertEqual(posts_from_context1, filtered_by_test_group0)

        # Проверяем картинки
        self.assertEqual(
            posts_from_context1.image,
            filtered_by_test_group0.image
        )

        # Проверяем, что пост созданный от группы, есть на странице группы
        posts_from_context0 = response.context['posts']
        self.assertIn(self.post_created_from_test_group0, posts_from_context0)

        # Проверяем, что пост из группы another_group
        # не попал в группу the_group
        self.assertNotIn(
            self.post_created_from_test_group1, posts_from_context0
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(
                reverse('posts:profile', kwargs={'username': AUTHOR})
            )
        )
        posts_from_context1 = response.context['posts'][FIRST_ELEMENT_ON_PAGE]
        test_author = get_object_or_404(User, username=AUTHOR)
        filtered_by_test_author = (
            Post.objects.filter(author=test_author)[FIRST_ELEMENT_ON_PAGE]
        )
        self.assertEqual(posts_from_context1, filtered_by_test_author)

        # Проверяем картинки
        self.assertEqual(
            posts_from_context1.image,
            filtered_by_test_author.image
        )

        # Проверяем, что пост созданный от группы, есть на странице автора
        posts_from_context0 = response.context['posts']
        self.assertIn(self.post_created_from_test_group0, posts_from_context0)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            )
        )
        posts_from_context = response.context['post']
        test_post = Post.objects.get(id='1')
        self.assertEqual(posts_from_context, test_post)

        # Проверяем картинки
        self.assertEqual(posts_from_context.image, test_post.image)

        # Проверяем комментарии
        comment_from_context = (
            response.context['comments'][FIRST_ELEMENT_ON_PAGE]
        )
        comment_from_model = test_post.comments.all()[FIRST_ELEMENT_ON_PAGE]
        self.assertEqual(comment_from_context, comment_from_model)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(reverse('posts:post_create'))
        )
        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_edit_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            )
        )
        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        for reverse_name in PostsPagesTests.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), FIRST_PAGE_COUNT
                )

    def test_second_page_contains_some_records(self):
        for reverse_name in PostsPagesTests.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertGreaterEqual(
                    len(response.context['page_obj']), SECOND_PAGE_COUNT
                )


class PostsCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)

    def setUp(self):
        # автор
        self.user = User.objects.get(username=AUTHOR)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)

    def test_index_cache(self):
        """Cache главной страницы работает"""
        cached_post = Post.objects.create(
            text='cache', author=self.author
        )
        response = (
            self.authorized_author.get(reverse('posts:main_page'))
        )
        default_content = response.content
        cached_post.delete()
        response2 = (
            self.authorized_author.get(reverse('posts:main_page'))
        )
        changed_content = response2.content
        self.assertEqual(default_content, changed_content)
        cache.clear()
        response3 = (
            self.authorized_author.get(reverse('posts:main_page'))
        )
        cleared_cache_content = response3.content
        self.assertNotEqual(default_content, cleared_cache_content)


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        Post.objects.bulk_create([
            Post(
                text=TEST_TEXT,
                author=cls.author
            ) for i in range(5)
        ])

    def setUp(self):
        # автор
        self.user = User.objects.get(username=AUTHOR)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)
        # другой авторизованный клиент
        self.user1 = User.objects.create_user(username='not_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

    def test_follow(self):
        """Подписка работает"""
        # подписка
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow', kwargs={'username': AUTHOR}
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'not_author'})
        )
        response2 = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        followed_posts = response2.context['posts'][0]
        author_posts = Post.objects.filter(author_id=self.author)[0]
        self.assertEqual(author_posts, followed_posts)

    def test_unfollow(self):
        """Отписка работает"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow', kwargs={
                    'username': self.author.username
                }
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'not_author'})
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        followed_posts = response.context['posts']
        author_posts = Post.objects.filter(author_id=self.author)[0]
        self.assertNotIn(author_posts, followed_posts)

    def test_subscriber_see_new_post(self):
        """Новые посты появляются на странице подписчика"""
        # подписка
        self.authorized_client.get(
            reverse(
                'posts:profile_follow', kwargs={
                    'username': self.author.username
                }
            )
        )
        # автор написал пост
        new_post = Post.objects.create(
            text='for_subscribers',
            author=self.author
        )
        # проверяем наличие поста в списке постов подписчика
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        followed_posts = response.context['posts']
        self.assertIn(new_post, followed_posts)

    def test_not_subscr_cant_see_new_post(self):
        """Новые посты  не появляются на странице
        неподписанного пользователя"""
        # автор написал пост
        new_post = Post.objects.create(
            text='for_subscribers',
            author=self.author
        )
        # проверяем отсутствие поста в списке постов подписчика
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        posts = response.context['posts']
        self.assertNotIn(new_post, posts)
