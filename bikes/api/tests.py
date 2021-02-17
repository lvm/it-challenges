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


class OrderTest(APITestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            'userdup', 'user@dupdup.com', 'pass123qwe')
        self.token = get_or_create_token(self.test_user)

        self.staff_user = get_user_model().objects.create_user(
            'staff', 'staf@dupdup.com', 'pass123qwe')
        self.staff_user.is_staff = True
        self.staff_user.save()
        self.token_staff = get_or_create_token(self.staff_user)

        self.order_url = reverse('order-list')

        data = {
            'rentals': 'h',
            'is_family': False
        }
        self.response = self.client.post(
            self.order_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.order_detail_url = reverse('order-detail',
                                        args=[self.response.data['id']])


    def test_create_order_without_discount(self):
        data = {
            'rentals': 'd, d, d,',
            'is_family': False
        }
        price_daily_x3 = 60
        response = self.client.post(
            self.order_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        # is created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # worth $30
        self.assertEqual(response.data.get('total').get('total'),
                         price_daily_x3)
        # because it should create, only 3.
        # despite "4" items when rentals.split(,)
        self.assertEqual(len(response.data.get('bike_rentals')), 3)

    def test_create_order_with_discount(self):
        data = {
            'rentals': 'd, d, d,',
            'is_family': True
        }
        price_daily_x3_with_discount = 42
        response = self.client.post(
            self.order_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        # is created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('total').get('total'),
                         price_daily_x3_with_discount)


    def test_delete_order_ok(self):
        rental_id = dict(self.response.data.get('bike_rentals').pop()).get('id')
        rental_detail_url = reverse('rental-detail', args=[rental_id])

        response = self.client.delete(
            self.order_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_staff.key))
        response_rental = self.client.get(
            rental_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        # order is deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # and the rental associated is not available anymore
        self.assertEqual(response_rental.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_fail(self):
        data = {
            'rentals': 'h',
            'is_family': False
        }
        self.response_2 = self.client.post(
            self.order_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.order_detail_url_2 = reverse('order-detail',
                                        args=[self.response_2.data['id']])
        rental_id = dict(self.response.data.get('bike_rentals').pop()).get('id')
        rental_detail_url = reverse('rental-detail', args=[rental_id])

        response = self.client.delete(
            self.order_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        response_rental = self.client.get(
            rental_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        # order is deleted
        self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # and the rental associated is not available anymore
        self.assertNotEqual(response_rental.status_code, status.HTTP_404_NOT_FOUND)


class RentalTest(APITestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            'userdup', 'user@dupdup.com', 'pass123qwe')
        self.token = get_or_create_token(self.test_user)


        self.staff_user = get_user_model().objects.create_user(
            'staff', 'staf@dupdup.com', 'pass123qwe')
        self.staff_user.is_staff = True
        self.staff_user.save()
        self.token_staff = get_or_create_token(self.staff_user)

        self.order_url = reverse('order-list')

        data = {
            'rentals': 'h',
            'is_family': False
        }
        self.response = self.client.post(
            self.order_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))
        self.order_detail_url = reverse('order-detail',
                                        args=[self.response.data['id']])

    def test_update_rental_fail(self):
        rental_id = dict(self.response.data.get('bike_rentals').pop()).get('id')
        rental_detail_url = reverse('rental-detail', args=[rental_id])

        data = {'returned': True}
        response = self.client.put(
            rental_detail_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        # then we query the order
        # we could check this through /api/rentals/{id}
        # but the order is the way to query data.
        response_order = self.client.get(
            self.order_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        rental_returned = dict(response_order.data.get('bike_rentals').pop()).get('is_returned')

        # rental is not updated
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(rental_returned, False)

    def test_update_rental_ok(self):
        rental_id = dict(self.response.data.get('bike_rentals').pop()).get('id')
        rental_detail_url = reverse('rental-detail', args=[rental_id])

        data = {'returned': True}
        response = self.client.put(
            rental_detail_url, data, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_staff.key))

        # then we query the order
        # we could check this through /api/rentals/{id}
        # but the order is the way to query data.
        response_order = self.client.get(
            self.order_detail_url, format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token.key))

        rental_returned = dict(response_order.data.get('bike_rentals').pop()).get('is_returned')

        # rental is updated
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(rental_returned, True)
