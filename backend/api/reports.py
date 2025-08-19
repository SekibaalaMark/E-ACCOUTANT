# reports.py (Create a new file in your app directory, e.g., your_app/reports.py)
# This module provides functions to calculate profits (revenue - COGS - expenses) 
# aggregated by daily, weekly, monthly, or yearly periods, as well as overall totals.
# You can import and use these in your views, management commands, or templates for report generation.
# For actual report generation (e.g., PDF/CSV export), you can extend this with libraries like ReportLab or csv.

from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from decimal import Decimal
from .models import Sale, Expense  # Assuming this is in the same app as models.py

def get_profit_calculations(period='daily'):
    """
    Calculate profits grouped by the specified period.
    - period: 'daily', 'weekly', 'monthly', 'yearly'
    Returns a list of dicts with 'period', 'revenue', 'cogs', 'expenses', 'profit'
    """
    if period == 'daily':
        trunc_func = TruncDay
    elif period == 'weekly':
        trunc_func = TruncWeek
    elif period == 'monthly':
        trunc_func = TruncMonth
    elif period == 'yearly':
        trunc_func = TruncYear
    else:
        raise ValueError("Invalid period. Choose from 'daily', 'weekly', 'monthly', 'yearly'.")

    # Calculate sales revenue and COGS per period
    sales_data = Sale.objects.annotate(
        period=trunc_func('date')
    ).values('period').annotate(
        revenue=Sum('total_price', output_field=DecimalField()),
        cogs=Sum(ExpressionWrapper(F('quantity') * F('product__buying_price'), output_field=DecimalField()))
    ).order_by('period')

    # Calculate expenses per period
    expenses_data = Expense.objects.annotate(
        period=trunc_func('date')
    ).values('period').annotate(
        expenses=Sum('amount', output_field=DecimalField())
    ).order_by('period')

    # Convert querysets to dicts for easy merging
    sales_dict = {item['period']: {'revenue': item['revenue'] or Decimal('0.00'), 'cogs': item['cogs'] or Decimal('0.00')} for item in sales_data}
    expenses_dict = {item['period']: item['expenses'] or Decimal('0.00') for item in expenses_data}

    # Get all unique periods from both sales and expenses
    all_periods = sorted(set(sales_dict.keys()) | set(expenses_dict.keys()))

    # Build the results
    results = []
    for p in all_periods:
        revenue = sales_dict.get(p, {'revenue': Decimal('0.00')})['revenue']
        cogs = sales_dict.get(p, {'cogs': Decimal('0.00')})['cogs']
        expenses = expenses_dict.get(p, Decimal('0.00'))
        profit = revenue - cogs - expenses
        results.append({
            'period': p,
            'revenue': revenue,
            'cogs': cogs,
            'expenses': expenses,
            'profit': profit
        })

    return results