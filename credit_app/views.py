
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer,Loan
from .serializers import CustomerRegistrationSerializer , CheckEligibilitySerializer , CreateLoanSerializer , LoanDetailsSerializer , LoanListItemSerializer
from datetime import datetime, date
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class RegisterCustomer(APIView):

    @method_decorator(csrf_exempt) 
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
         
            monthly_income = serializer.validated_data['monthly_income']
            approved_limit = round(36 * monthly_income, -5)  # Round to nearest lakh

            customer = serializer.save(approved_limit=approved_limit)

            return Response({
                'customer_id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_income,
                'approved_limit': approved_limit,
                'phone_number': customer.phone_number,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CheckEligibility(APIView):

    @classmethod
    def calculate_credit_score(cls, customer, past_loans):
        credit_score = 0

        # i. Past Loans paid on time
        emis_paid_on_time_total = sum(loan.emis_paid_on_time for loan in past_loans)
        credit_score += emis_paid_on_time_total

        # ii. No of loans taken in the past
        num_past_loans = past_loans.count()
        credit_score += num_past_loans * 5  # Arbitrary weight

        # iii. Loan activity in the current year
        current_year = date.today().year
        loans_in_current_year = past_loans.filter(start_date__year=current_year)
        credit_score += loans_in_current_year.count()

        # iv. Loan approved volume
        approved_loan_volume = sum(loan.loan_amount for loan in past_loans)
        credit_score += approved_loan_volume // 100000  

        # v. If sum of current loans of the customer > approved limit of the customer, credit score = 0
        current_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today())
        if sum(loan.loan_amount for loan in current_loans) > customer.approved_limit:
            credit_score = 0

        return credit_score

    @classmethod
    def check_loan_eligibility(cls, credit_score, loan_amount, interest_rate, tenure, monthly_salary, customer):
        approval = False
        corrected_interest_rate = interest_rate
        monthly_installment = (loan_amount * (1 + interest_rate / 100)) / tenure


        if credit_score > 50:
            approval = True
        elif 50 > credit_score > 30:
            if interest_rate <= 12:
                corrected_interest_rate = 12
                monthly_installment = (loan_amount * (1 + corrected_interest_rate / 100)) / tenure
        elif 30 > credit_score > 10:
            if interest_rate <= 16:
                corrected_interest_rate = 16
                monthly_installment = (loan_amount * (1 + corrected_interest_rate / 100)) / tenure


        current_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today())

        if credit_score < 10 or sum(loan.monthly_repayment for loan in current_loans) > 0.5 * monthly_salary:
            approval = False

        return approval, corrected_interest_rate, monthly_installment

    @method_decorator(csrf_exempt)  
    def post(cls, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            # Get customer and their past loan data
            customer = Customer.objects.get(customer_id=customer_id)
            past_loans = Loan.objects.filter(customer=customer)

            # Implement credit score calculation logic
            credit_score = cls.calculate_credit_score(customer, past_loans)

            # Implement loan approval logic based on credit score
            approval, corrected_interest_rate, monthly_installment = cls.check_loan_eligibility(
                credit_score, loan_amount, interest_rate, tenure, customer.monthly_salary, customer
            )

            # Prepare the response data
            return Response({
                'customer_id': customer_id,
                'approval': approval,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate,
                'tenure': tenure,
                'monthly_installment': monthly_installment,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CreateLoan(APIView):
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            # Get customer and their past loan data
            customer = Customer.objects.get(customer_id=customer_id)
            past_loans = Loan.objects.filter(customer=customer)


            credit_score = CheckEligibility.calculate_credit_score(customer, past_loans)

            approval, corrected_interest_rate, monthly_installment = CheckEligibility.check_loan_eligibility(
                credit_score, loan_amount, interest_rate, tenure, customer.monthly_salary, customer
            )

  
            if approval:

                new_loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=corrected_interest_rate,
                    tenure=tenure,
                    monthly_repayment=monthly_installment,
                )

                response_data = {
                    'loan_id': new_loan.id,
                    'customer_id': customer_id,
                    'loan_approved': True,
                    'monthly_installment': monthly_installment,
                }
            else:
                response_data = {
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': 'Loan not approved based on eligibility criteria.',
                    'monthly_installment': 0.0,
                }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ViewLoanDetails(APIView):
    def get(self, request, loan_id):
        try:
            
            loan = Loan.objects.get(id=loan_id)

        
            customer = Customer.objects.get(id=loan.customer.id)

            serializer = LoanDetailsSerializer({
                'loan_id': loan.id,
                'customer': {
                    'id': customer.id,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'phone_number': customer.phone_number,
                    'age': customer.age,
                },
                'loan_approved': loan.is_approved,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'tenure': loan.tenure,
            })

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Loan.DoesNotExist:
            return Response({'message': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        


class ViewCustomerLoans(APIView):
    def get(self, request, customer_id):
        try:
     
            customer = Customer.objects.get(id=customer_id)


            current_loans = Loan.objects.filter(customer=customer, is_approved=True)

  
            serializer = LoanListItemSerializer(current_loans, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
