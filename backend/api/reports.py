# your_app/reports.py
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from decimal import Decimal
from .models import Sale, Expense

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
            'period': p.strftime('%Y-%m-%d') if period == 'daily' else p.strftime('%Y-%m') if period == 'monthly' else p.strftime('%Y'),
            'revenue': float(revenue),  # Convert Decimal to float for JSON serialization
            'cogs': float(cogs),
            'expenses': float(expenses),
            'profit': float(profit)
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
        'revenue': float(revenue),
        'cogs': float(cogs),
        'expenses': float(expenses),
        'profit': float(profit)
    }
