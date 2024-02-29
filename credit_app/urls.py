# credit_app/urls.py
from django.urls import path
from .views import RegisterCustomer ,CheckEligibility , CreateLoan , ViewLoanDetails , ViewCustomerLoans

urlpatterns = [
    path('register/', RegisterCustomer.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibility.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoan.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>/', ViewLoanDetails.as_view(), name='view-loan-details'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoans.as_view(), name='view-customer-loans'),
    # Add other URLs as needed
]
