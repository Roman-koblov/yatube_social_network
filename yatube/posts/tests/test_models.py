from django.test import TestCase

from ..models import Group, Post, User

AUTHOR = 'author'
GROUP_SLUG = 'the_group'
GROUP_TITLE = 'Тестовая группа 0'
GROUP_DESCRIPTION = 'Описание групппы'
TEST_TEXT = 'Тестовый текст поста'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        group_expected_name = group.title
        post_expected_name = post.text[:15]
        self.assertEqual(str(group), group_expected_name)
        self.assertEquals(str(post), post_expected_name)
