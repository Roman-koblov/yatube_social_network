import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Post, User

AUTHOR = 'author'
TEST_TEXT = 'Тестовый текст поста'
NEW_TEXT = 'Новый тестовый текст поста'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=AUTHOR)
        cls.test_post = Post.objects.create(
            text=TEST_TEXT,
            author=cls.test_user,
        )
        cls.form = PostForm()
        cls.comment = Comment.objects.create(
            text=TEST_TEXT,
            author=cls.test_user,
            post=Post.objects.get(id='1')
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username=AUTHOR)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=image,
            content_type='image/gif'
        )
        form_data = {
            'text': TEST_TEXT,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': AUTHOR})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_TEXT,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        edited_post = Post.objects.get(id='1')
        form_data = {
            'text': NEW_TEXT,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        response_guest = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response_guest,
            (reverse('users:login') + '?next=/posts/1/edit/')
        )
        self.assertNotEqual(Post.objects.get(id='1').text, edited_post.text)

    def test_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': TEST_TEXT,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=TEST_TEXT
            ).exists()
        )
