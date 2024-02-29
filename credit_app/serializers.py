# credit_app/serializers.py
from rest_framework import serializers
from .models import Customer

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class LoanDetailsSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    customer = serializers.DictField()
    loan_approved = serializers.BooleanField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.FloatField()
    tenure = serializers.IntegerField()


class LoanListItemSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.FloatField()
    emis_left = serializers.IntegerField()
    repayments_left = serializers.FloatField()
