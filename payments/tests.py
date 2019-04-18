import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from payments.models import Account, Payment, User
from moneyed import Money, PHP, USD


class AccountsTest(TestCase):

    def setUp(self):
        # Create users 'bob123' and 'alice456' and accounts belonging to them.
        self.bob = User.objects.create(username='bob123')
        self.alice = User.objects.create(username='alice456')
        self.bob_acc = Account.objects.create(
            owner=self.bob,
            balance_currency=USD,
            balance='10',
        )
        self.alice_acc = Account.objects.create(
            owner=self.alice,
            balance_currency=USD,
            balance='11',
        )

    def test_accounts_list(self):
        # Ensure we have two accounts in the list.
        url = reverse('account-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertContains(response, 'bob123')
        self.assertContains(response, 'alice456')
        self.assertEqual(len(data), Account.objects.count())

    def test_accounts_detail(self):
        # Get an account's detail.
        url = reverse('account-detail', args=(self.bob_acc.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        expected_res = {
            "id": 1,
            "owner": "bob123",
            "balance_currency": "USD",
            "balance": "10.000000000000000000"
        }
        self.assertEqual(data, expected_res)

    def test_accounts_create(self):
        # Create a new account for user "alice456".
        url = reverse('account-list')
        post_data = {
            "owner": self.alice,
            "balance_currency": "PHP",
        }
        response = self.client.post(url, post_data)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        expected_data = {
            "id": 3,
            "owner": "alice456",
            "balance_currency": "PHP",
            "balance": "0.000000000000000000"
        }
        self.assertEqual(data, expected_data)

    def test_account_delete(self):
        acc_id = self.bob_acc.id
        url = reverse('account-detail', args=(acc_id,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Account.objects.filter(pk=acc_id).exists())


class PaymentsTest(TestCase):

    def setUp(self):
        # Create users 'bob123' and 'alice456' and accounts belonging to them.
        self.bob = User.objects.create(username='bob123')
        self.alice = User.objects.create(username='alice456')
        self.bob_acc = Account.objects.create(
            owner=self.bob,
            balance_currency=USD,
            balance='100',
        )
        self.alice_acc = Account.objects.create(
            owner=self.alice,
            balance_currency=USD,
            balance='110',
        )

    def test_payments_list(self):
        # Get list of Payments. Try without any payments. Then create some payments and check again.
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)
        Payment.objects.create(
            from_account=self.alice_acc,
            to_account=self.bob_acc,
            amount=Money(amount=10, currency=USD)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_payments_detail(self):
        # Get payment's detail
        Payment.objects.create(
            from_account=self.alice_acc,
            to_account=self.bob_acc,
            amount=Money(amount=10, currency=USD)
        )
        url = reverse('payment-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        expected_res = {
            'amount': '10.000000000000000000',
            'amount_currency': 'USD',
            'date': data['date'],
            'from_account': 2,
            'id': 1,
            'to_account': 1
        }
        self.assertEqual(expected_res, data)

    def test_payments_create(self):
        url = reverse('payment-list')
        amount = 2
        post_data = {
            "amount_currency": "USD",
            "amount": amount,
            'from_account': self.bob_acc.id,
            'to_account': self.alice_acc.id
        }
        response = self.client.post(url, post_data)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Payment.objects.filter(pk=data['id']).exists())

    def test_payment_delete(self):
        payment = Payment.objects.create(
            from_account=self.alice_acc,
            to_account=self.bob_acc,
            amount=Money(amount=10, currency=USD)
        )
        url = reverse('payment-detail', args=(payment.id,))
        self.assertTrue(Payment.objects.filter(pk=payment.id).exists())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Payment.objects.filter(pk=payment.id).exists())


