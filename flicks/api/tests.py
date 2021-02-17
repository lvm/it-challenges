from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from .api_views import get_or_create_token
from rest_framework.test import APIClient
from rest_framework import status


class UserTest(APITestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            'userdup', 'user@dupdup.com', 'pass123qwe')
        self.token = get_or_create_token(self.test_user)
        self.create_url = reverse('user-create')
        self.login_url = reverse('user-login')
        self.logout_url = reverse('user-logout')

    def test_create_user(self):
        data = {
            'username': 'redfield',
            'password': 'somepassword123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Welcome")

    def test_create_user_fail(self):
        data = {
            'username': 'ouch',
            'password': 'ouch'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['message'] == "Welcome")

    def test_create_user_dup_fail(self):
        data = {
            'username': 'userdup',
            'password': 'otherpassword123'
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         {'username': ['This field must be unique.']})

    def test_login_user_without_logout(self):
        data = {
            'username': 'userdup',
            'password': 'pass123qwe'
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Welcome")
        self.assertEqual(response.data['token'], self.token.key)

    def test_logout_user(self):
        response = self.client.post(
            self.logout_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token.key)
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


class FilmTest(APITestCase):
    def setUp(self):
        test_data = {
            'title': 'Rambo: first blood',
            'year': '1980'
        }
        self.test_user = get_user_model().objects.create_user(
            'userdup', 'user@dupdup.com', 'pass123qwe')
        self.token = get_or_create_token(self.test_user)
        self.film_url = reverse('film-list')
        self.response = self.client.post(
            self.film_url, test_data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.film_detail_url = reverse('film-detail',
                                       args=[self.response.data['id']])

    def test_create_film(self):
        data = {
            'title': 'Rambo: first blood 2',
            'year': '1985'
        }
        response = self.client.post(
            self.film_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_film(self):
        data = {
            'title': 'Rambo: First blood',
            'year': '1982'
        }
        response = self.client.put(
            self.film_detail_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_delete_film(self):
        response = self.client.delete(
            self.film_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PersonTest(APITestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            'userdup', 'user@dupdup.com', 'pass123qwe')
        self.token = get_or_create_token(self.test_user)
        test_film = {
            'title': 'Rambo: First blood',
            'year': '1982'
        }
        self.film_url = reverse('film-list')
        self.film_response = self.client.post(
            self.film_url, test_film, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.film_detail_url = reverse('film-detail',
                                       args=[self.film_response.data['id']])

        test_data = {
            'first_name': 'Silvester',
            'last_name': 'Stalone',
            'alias': ['the dude from Rambo']
        }
        self.person_url = reverse('person-list')
        self.response = self.client.post(
            self.person_url, test_data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.person_detail_url = reverse('person-detail',
                                         args=[self.response.data['id']])

    def test_create_person(self):
        test_film = {
            'title': 'Seinfeld: The movie',
            'year': '1994'
        }
        film_url = reverse('film-list')
        film_response = self.client.post(
            self.film_url, test_film, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        data = {
            'first_name': 'Jason',
            'last_name': 'Alexander',
            'alias': ['Costanza'],
            'as_actor': [film_response.data['id']],
            'as_producer': [self.film_response.data['id'], film_response.data['id']],
        }
        response = self.client.post(
            self.person_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_person(self):
        test_film = {
            'title': 'Rocky',
            'year': '1976'
        }
        film_url = reverse('film-list')
        film_response = self.client.post(
            self.film_url, test_film, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        data = {
            'first_name': 'Sylvester',
            'last_name': 'Stallone',
            'alias': ['Sly', 'the dude from Rambo', 'Rocky'],
            'as_actor': [film_response.data['id']],
            'as_producer': [self.film_response.data['id'], film_response.data['id']],
        }
        response = self.client.put(
            self.person_detail_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


    def test_delete_film(self):
        response = self.client.delete(
            self.person_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
