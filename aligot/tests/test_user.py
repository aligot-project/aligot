# coding: utf-8

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ..models import User


class TestUserCreationAPI(TestCase):
    """
    Test cases for all the user creations schemes
    """

    def test_create_without_params(self):
        self.assertEquals(status.HTTP_400_BAD_REQUEST, self.client.post(reverse('user-create')).status_code)
        self.assertEquals(0, User.objects.count())

    def test_create_user(self):
        """
        Create user & wait for 201 response.
        """
        data = {
            'username': 'test',
            'password': 'test',
            'email': 'test@mail.com'
        }
        response = self.client.post(reverse('user-create'), data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)
        self.assertEqual(1, User.objects.count())

        # Check the first
        user = User.objects.all()[0]
        self.assertEqual(user.username, data['username'], 'Username in DB don\'t match')

    def test_create_with_same_email(self):
        """
        Test on the case of creation for an user with a same mail than an other user in DB
        Wait for 400 Bad Request
        """
        first_user = User.objects.create(
            username='test1',
            password='test',
            email='test@mail.com'
        )
        self.assertEqual(1, User.objects.count(), 'ORM don\'t insert user in DB')

        data = {
            'username': 'test2',
            'password': 'test',
            'email': 'test@mail.com'
        }
        response = self.client.post(reverse('user-create'), data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.content)
        self.assertEqual(1, User.objects.count())

    def test_create_with_same_username(self):
        """
        Test the creation's case of an user with a same username try to register
        Wait for 400 Bad Request
        The email difference musn't impact the test
        """

        first_user = User.objects.create(
            username='test',
            password='test',
            email='test1@mail.com'
        )
        self.assertEqual(1, User.objects.count(), 'ORM don\'t insert user in DB')

        data = {
            'username': 'test',
            'password': 'test',
            'email': 'test2@mail.com'
        }
        response = self.client.post(reverse('user-create'), data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.content)
        self.assertEqual(1, User.objects.count())


class TestUserApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='test',
            email='mail@mail.com'
        )
        self.client.force_authenticate(user=self.user)
        self.assertEqual(1, User.objects.count(), 'ORM don\'t insert user in DB')

    def test_retrieve(self):
        """
        Retrieve user & wait for 200 response
        """

        response = self.client.get(reverse('user-detail', args=[self.user.username]))
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)

    def test_delete(self):
        """
        Simple deletion of an user in DB
        Wait for 204 response.
        """

        response = self.client.delete(reverse('user-detail', args=[self.user.username]))

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content)

    def test_update(self):
        """
        Test if a connected user can change is own mail.
        """
        data = {
            'username': 'test',
            'password': 'test',
            'email': 'changed_mail@mail.com',
        }

        response = self.client.put(reverse('user-detail', args=[self.user.username]), data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)

        user = User.objects.get(username='test')

        self.assertEqual(user.email, data['email'], 'Update failed in DB')

    def test_patch(self):
        """
        Test if a connected user can patch a user Field.
        """

        data = {
            'email': 'changed_mail@mail.com',
        }

        response = self.client.patch(reverse('user-detail', args=[self.user.username]), data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)

        user = User.objects.get(username='test')

        self.assertEqual(user.email, data['email'], 'Update failed in DB')