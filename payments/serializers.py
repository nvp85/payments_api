from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Account, Payment

class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        return value.get_username()
    class Meta:
        model = User
        fields = ('username',)

class AccountSerializer(serializers.ModelSerializer):
    #owner = UserSerializer()
    owner = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Account
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    #from_account = UserSerializer(source='from_account.owner')
    #to_account = UserSerializer(source='to_account.owner')
    from_account = serializers.CharField(source='from_account.owner')
    to_account = serializers.CharField(source='to_account.owner')

    def create(self, validated_data):
        from_account = Account.objects.get(owner__username=validated_data.get('from_account').get('owner'))
        to_account = Account.objects.get(owner__username=validated_data.get('to_account').get('owner'))
        amount = validated_data.get('amount')
        validated_data = {'from_account': from_account, 'to_account': to_account, 'amount': amount}
        return Payment.objects.create(**validated_data)

    class Meta:
        model = Payment
        fields = '__all__'