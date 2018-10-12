from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Account, Payment
from rest_framework import viewsets
from .serializers import UserSerializer, AccountSerializer, PaymentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('date_joined')
    serializer_class = UserSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

