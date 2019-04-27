from django.contrib.auth.models import User
from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers
from .models import Account, Payment
from decimal import Decimal
from moneyed import Money, USD


class UserSerializer(serializers.ModelSerializer):

    def to_representation(self, value):
        return {'id': value.id, 'username': value.get_username()}

    class Meta:
        model = User
        fields = ('username', 'id')


class AccountSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    balance = MoneyField(decimal_places=18, max_digits=30, default=Money(amount=Decimal('0.0'), currency=USD))

    class Meta:
        model = Account
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        #from_account = Account.objects.get(owner__username=validated_data.get('from_account').get('owner'))
        #to_account = Account.objects.get(owner__username=validated_data.get('to_account').get('owner'))
        #amount = validated_data.get('amount')
        #validated_data = {'from_account': from_account, 'to_account': to_account, 'amount': amount}
        return Payment.objects.create(**validated_data)

    def validate(self, validated_data):
        errors = {}
        from_account = validated_data.get('from_account')
        to_account = validated_data.get('to_account')
        # We must block the data we try to modify.
        if from_account:
            validated_data['from_account'] = Account.objects.select_for_update().get(pk=validated_data['from_account'].pk)
        if to_account:
            validated_data['to_account'] = Account.objects.select_for_update().get(pk=validated_data['to_account'].pk)
        if not from_account and not to_account:
            errors['from_account and to_account'] = ['At least one account field must be defined',]
        elif from_account == to_account:
            errors['accounts'] = ['Sender and recipient accounts must be different.']
        if type(validated_data.get('amount')) is Decimal:
            errors['amount'] = ['Currency must be defined explicitly.']
        else:
            if from_account:
                if validated_data['from_account'].balance.currency != validated_data['amount'].currency:
                    errors['from_account'] = ["Payment must be in currency of sender's account,"]
                elif validated_data['from_account'].balance < validated_data['amount']:
                    errors['amount'] = ['Not enough money for the payment',]
            if to_account:
                if validated_data['to_account'].balance.currency != validated_data['amount'].currency:
                    errors['to_account'] = ["Payment must be in currency of recipient's account,"]
        if errors:
            raise serializers.ValidationError(errors)
        return validated_data

    class Meta:
        model = Payment
        fields = '__all__'
