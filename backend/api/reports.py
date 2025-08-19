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



def get_overall_profits():
    """
    Calculate overall (all-time) profits.
    Returns a dict with 'revenue', 'cogs', 'expenses', 'profit'
    """
    sales_agg = Sale.objects.aggregate(
        revenue=Sum('total_price', output_field=DecimalField()),
        cogs=Sum(ExpressionWrapper(F('quantity') * F('product__buying_price'), output_field=DecimalField()))
    )
    expenses_agg = Expense.objects.aggregate(
        expenses=Sum('amount', output_field=DecimalField())
    )

    revenue = sales_agg['revenue'] or Decimal('0.00')
    cogs = sales_agg['cogs'] or Decimal('0.00')
    expenses = expenses_agg['expenses'] or Decimal('0.00')
    profit = revenue - cogs - expenses

    return {
        'revenue': revenue,
        'cogs': cogs,
        'expenses': expenses,
        'profit': profit
    }

# Example usage in a view (add to your views.py):
# from django.http import JsonResponse
# from .reports import get_profit_calculations, get_overall_profits

# def profit_report(request, period='daily'):
#     if period == 'overall':
#         data = get_overall_profits()
#     else:
#         data = get_profit_calculations(period)
#     return JsonResponse(data, safe=False)

# For report generation (e.g., simple console print for testing):
# print(get_profit_calculations('daily'))
# print(get_overall_profits())

# To generate a CSV report (example extension):
# import csv
# from django.http import HttpResponse

# def export_profit_csv(request, period='daily'):
#     if period == 'overall':
#         data = [get_overall_profits()]
#     else:
#         data = get_profit_calculations(period)
    
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="{period}_profits.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Period', 'Revenue', 'COGS', 'Expenses', 'Profit'])  # Header
    
#     for row in data:
#         period_str = row.get('period', 'Overall') or 'Overall'
#         writer.writerow([period_str, row['revenue'], row['cogs'], row['expenses'], row['profit']])
    
#     return response