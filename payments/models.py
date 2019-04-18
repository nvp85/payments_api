from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField


class Account(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    balance = MoneyField(max_digits=30, decimal_places=18, blank=False, null=False, default=0, default_currency='USD')


class Payment(models.Model):
    from_account = models.ForeignKey(Account, related_name='payments_out', blank=True, null=True, on_delete=models.SET_NULL)
    to_account = models.ForeignKey(Account, related_name='payments_in', blank=True, null=True, on_delete=models.SET_NULL)
    amount = MoneyField(max_digits=30, decimal_places=18, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
