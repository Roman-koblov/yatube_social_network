from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_url_for_auth_users(self):
        """Тест доступности страниц about"""
        urls = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница возвращает 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
