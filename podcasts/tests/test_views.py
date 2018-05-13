from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


TEST_CREDENTIALS = {
    'username': 'testuser',
    'password': 'password123456'
}
LOGIN_URL = getattr(settings, 'LOGIN_URL', '/accounts/login/')


class UnauthorizedViewTestCase(TestCase):
    pattern = ''
    view_url = ''

    def setUp(self):
        self.view_url = reverse(self.pattern)


class AuthorizedViewTestCase(TestCase):
    pattern = ''
    view_url = ''

    def setUp(self):
        User.objects.create_user(**TEST_CREDENTIALS)
        self.client.login(**TEST_CREDENTIALS)
        self.view_url = reverse(self.pattern)


class IndexTest(TestCase):
    def test_redirect(self):
        """Unauthorized client should redirect to login url"""
        response = self.client.get('/')
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, LOGIN_URL)


class PodcastsListUnauthorizedTest(UnauthorizedViewTestCase):
    pattern = 'podcasts:podcasts-list'

    def test_unauthorized(self):
        """Unauthorized client should redirect to login url"""
        response = self.client.get(self.view_url)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, LOGIN_URL)


class PodcastsListTest(AuthorizedViewTestCase):
    pattern = 'podcasts:podcasts-list'

    def test_logged_in(self):
        """Log in client to get *actual* url"""
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_from_index(self):
        """Test the redirect from index to podcasts-list"""
        response = self.client.get('/')
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, self.view_url)

    def test_empty_page_request(self):
        """Soft-failing request of empty/nonexistent pagination page"""
        response = self.client.get(self.view_url + '?page=9999')
        self.assertEqual(response.status_code, 200)
