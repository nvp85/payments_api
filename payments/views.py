from typing import Any

from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.request import Request
from rest_framework import mixins
from rest_framework.serializers import BaseSerializer
from django.db import transaction
from .models import Account, Payment
from rest_framework import viewsets
from .serializers import UserSerializer, AccountSerializer, PaymentSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('date_joined')
    serializer_class = UserSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class PaymentViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer: BaseSerializer) -> None:
        account_from = serializer.validated_data['from_account']
        account_to = serializer.validated_data['to_account']
        if account_from:
            account_from.balance = account_from.balance - serializer.validated_data['amount']
            account_from.save()
        if account_to:
            account_to.balance = account_to.balance + serializer.validated_data['amount']
            account_to.save()
        super().perform_create(serializer)



