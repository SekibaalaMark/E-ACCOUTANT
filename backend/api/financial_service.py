from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from .models import Purchase, Expense, Sale  # Assuming you have a Sale model


class FinancialService:
    """Service class for financial calculations and reporting"""
    
    @staticmethod
    def get_date_ranges(period_type, year=None, month=None, week=None):
        """Get start and end dates for different periods"""
        now = timezone.now()
        
        if period_type == 'weekly':
            if week:
                # Specific week of current year
                start_date = datetime.strptime(f'{now.year}-W{week}-1', "%Y-W%W-%w")
                end_date = start_date + timedelta(days=6)
            else:
                # Current week
                days_since_monday = now.weekday()
                start_date = now - timedelta(days=days_since_monday)
                end_date = start_date + timedelta(days=6)
                
        elif period_type == 'monthly':
            if year and month:
                start_date = datetime(year, month, 1)
                _, last_day = monthrange(year, month)
                end_date = datetime(year, month, last_day)
            else:
                # Current month
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    end_date = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
                else:
                    end_date = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
                    
        elif period_type == 'yearly':
            year = year or now.year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            
        return start_date, end_date

    @staticmethod
    def calculate_purchases_cost(start_date, end_date):
        """Calculate total purchase costs for a period"""
        purchases = Purchase.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_cost=Sum('total_cost'),
            total_quantity=Sum('quantity')
        )
        
        return {
            'total_cost': purchases['total_cost'] or 0,
            'total_quantity': purchases['total_quantity'] or 0
        }

    @staticmethod
    def calculate_expenses(start_date, end_date):
        """Calculate total expenses for a period"""
        expenses = Expense.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_amount=Sum('amount')
        )
        
        return {
            'total_expenses': expenses['total_amount'] or 0
        }

    @staticmethod
    def calculate_sales_revenue(start_date, end_date):
        """
        Calculate sales revenue for a period
        Note: You'll need to create a Sale model or modify this based on your sales tracking
        """
        # Example Sale model structure:
        # class Sale(models.Model):
        #     product = models.ForeignKey(Product, on_delete=models.CASCADE)
        #     quantity = models.PositiveIntegerField()
        #     selling_price = models.DecimalField(max_digits=10, decimal_places=2)
        #     total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
        #     date = models.DateTimeField(auto_now_add=True)
        
        try:
            sales = Sale.objects.filter(
                date__range=[start_date, end_date]
            ).aggregate(
                total_price=Sum('total_price'),
                #total_quantity=Sum('quantity')
            )
            
            return {
                'total_price': sales['total_price'] or 0,
                #'total_quantity_sold': sales['total_quantity'] or 0
            }
        except:
            # If Sale model doesn't exist, return zeros
            return {
                'total_price': 0,
                #'total_quantity_sold': 0
            }

    @classmethod
    def generate_financial_report(cls, period_type, year=None, month=None, week=None):
        """Generate comprehensive financial report"""
        start_date, end_date = cls.get_date_ranges(period_type, year, month, week)
        
        # Get all financial data
        purchases_data = cls.calculate_purchases_cost(start_date, end_date)
        expenses_data = cls.calculate_expenses(start_date, end_date)
        sales_data = cls.calculate_sales_revenue(start_date, end_date)
        
        # Calculate profits and balance
        total_revenue = sales_data['total_price']
        total_purchases = purchases_data['total_cost']
        total_expenses = expenses_data['total_expenses']
        
        # Cost of Goods Sold (COGS) = Purchase costs
        cogs = total_purchases
        
        # Gross Profit = Revenue - COGS
        gross_profit = total_revenue - cogs
        
        # Net Profit = Gross Profit - Operating Expenses
        net_profit = gross_profit - total_expenses
        
        # Operating Expenses = General expenses (not including purchases)
        operating_expenses = total_expenses
        
        return {
            'period': {
                'type': period_type,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'year': year,
                'month': month,
                'week': week
            },
            'revenue': {
                'total_revenue': float(total_revenue),
                #'total_quantity_sold': sales_data['total_quantity_sold']
            },
            'costs': {
                'cost_of_goods_sold': float(cogs),
                'total_purchases': float(total_purchases),
                'purchase_quantity': purchases_data['total_quantity'],
                'operating_expenses': float(operating_expenses)
            },
            'profitability': {
                'gross_profit': float(gross_profit),
                'net_profit': float(net_profit),
                'gross_profit_margin': float((gross_profit / total_revenue * 100)) if total_revenue > 0 else 0,
                'net_profit_margin': float((net_profit / total_revenue * 100)) if total_revenue > 0 else 0
            },
            'balance': {
                'total_income': float(total_revenue),
                'total_outgoing': float(total_purchases + total_expenses),
                'net_balance': float(total_revenue - total_purchases - total_expenses)
            }
        }