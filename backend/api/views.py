from django.shortcuts import render
from rest_framework import serializers
from .models import *
from .serializers import *

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import LoginSerializer

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        }, status=status.HTTP_200_OK)


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Product instances.
    Provides standard CRUD operations: list, retrieve, create, update, and delete.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Save the product instance with validated data.

        """
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)

    def perform_update(self, serializer):
        """
        Update the product instance with validated data.
        """
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)




class SaleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Sale instances.
    Provides standard CRUD operations: list, retrieve, create, update, and delete.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Save the sale instance with validated data, triggering the model's save method.
        """
        if serializer.is_valid():   
            serializer.save()

    def perform_update(self, serializer):
        """
        Update the sale instance with validated data, triggering the model's save method.
        """
        if serializer.is_valid():
            serializer.save()






class PurchaseViewSet(viewsets.ModelViewSet):
    """
    Simple ModelViewSet for Purchase model
    Provides all CRUD operations:
    - GET /purchases/ (list all)
    - POST /purchases/ (create new)
    - GET /purchases/{id}/ (get one)
    - PUT/PATCH /purchases/{id}/ (update)
    - DELETE /purchases/{id}/ (delete)
    """
    queryset = Purchase.objects.select_related('product').all()
    serializer_class = PurchaseSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Save the purchase instance with validated data.
        """
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)

    def perform_update(self, serializer):
        """
        Update the purchase instance with validated data.
        """
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    Simple ModelViewSet for Expense model
    Provides all CRUD operations:
    - GET /expenses/ (list all)
    - POST /expenses/ (create new)
    - GET /expenses/{id}/ (get one)
    - PUT/PATCH /expenses/{id}/ (update)
    - DELETE /expenses/{id}/ (delete)
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)

    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)
        



from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .financial_service import FinancialService


class FinancialReportsViewSet(viewsets.ViewSet):
    """
    ViewSet for financial reports and calculations
    """
    
    @action(detail=False, methods=['get'])
    def weekly_report(self, request):
        """
        Get weekly financial report
        Usage: GET /financial-reports/weekly_report/?week=30&year=2024
        """
        week = request.query_params.get('week')
        year = request.query_params.get('year')
        
        if year:
            year = int(year)
        
        if week:
            week = int(week)
        
        try:
            report = FinancialService.generate_financial_report('weekly', year=year, week=week)
            return Response({
                'success': True,
                'report_type': 'Weekly Financial Report',
                'data': report
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """
        Get monthly financial report
        Usage: GET /financial-reports/monthly_report/?month=8&year=2024
        """
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        try:
            report = FinancialService.generate_financial_report('monthly', year=year, month=month)
            return Response({
                'success': True,
                'report_type': 'Monthly Financial Report',
                'data': report
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def yearly_report(self, request):
        """
        Get yearly financial report
        Usage: GET /financial-reports/yearly_report/?year=2024
        """
        year = request.query_params.get('year')
        
        if year:
            year = int(year)
        
        try:
            report = FinancialService.generate_financial_report('yearly', year=year)
            return Response({
                'success': True,
                'report_type': 'Yearly Financial Report',
                'data': report
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def current_period(self, request):
        """
        Get financial report for current week, month, and year
        Usage: GET /financial-reports/current_period/
        """
        try:
            weekly = FinancialService.generate_financial_report('weekly')
            monthly = FinancialService.generate_financial_report('monthly')
            yearly = FinancialService.generate_financial_report('yearly')
            
            return Response({
                'success': True,
                'report_type': 'Current Period Summary',
                'data': {
                    'this_week': weekly,
                    'this_month': monthly,
                    'this_year': yearly
                }
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


from .reports import get_profit_calculations, get_overall_profits


class ProfitReportView(APIView):
    """
    API endpoint to retrieve profit reports by period (daily, weekly, monthly, yearly) or overall.
    - GET /api/profits/?period=<daily|weekly|monthly|yearly|overall>
    """
    def get(self, request):
        # Check user role (optional: restrict to admin or viewer)
        '''
        if not request.user.is_authenticated or request.user.role not in ['admin', 'viewer']:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)
            '''

        period = request.query_params.get('period', 'daily')

        try:
            if period == 'overall':
                data = get_overall_profits()
            else:
                data = get_profit_calculations(period)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


import csv
from django.http import HttpResponse
from rest_framework.views import APIView

class ProfitReportCSVView(APIView):
    """
    API endpoint to download profit reports as CSV.
    - GET /api/profits/csv/?period=<daily|weekly|monthly|yearly|overall>
    """
    def get(self, request):
        # Check user role (optional: restrict to admin)
        '''
        if not request.user.is_authenticated or request.user.role != 'admin':
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)
            '''

        period = request.query_params.get('period', 'daily')

        try:
            if period == 'overall':
                data = [get_overall_profits()]
            else:
                data = get_profit_calculations(period)

            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{period}_profits.csv"'

            writer = csv.writer(response)
            writer.writerow(['Period', 'Revenue', 'COGS', 'Expenses', 'Profit'])  # Header

            for row in data:
                period_str = row.get('period', 'Overall') or 'Overall'
                writer.writerow([period_str, row['revenue'], row['cogs'], row['expenses'], row['profit']])

            return response
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)