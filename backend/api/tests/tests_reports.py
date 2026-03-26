from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from .models import Product, Sale, Expense
from .reports import get_profit_calculations

class ProfitReportLogicTests(TestCase):
    def setUp(self):
        # 1. Setup Product with a buying price (for COGS)
        self.laptop = Product.objects.create(
            name="Laptop",
            buying_price=Decimal("600.00"), # COGS base
            price=Decimal("1000.00"),       # Sale price
            stock=10
        )

        # 2. Create a Sale (Jan 15, 2024)
        # Revenue: 1000 * 2 = 2000
        # COGS: 600 * 2 = 1200
        Sale.objects.create(
            product=self.laptop,
            quantity=2,
            total_price=Decimal("2000.00"),
            date=datetime(2024, 1, 15, tzinfo=timezone.utc)
        )

        # 3. Create an Expense (Jan 20, 2024)
        Expense.objects.create(
            title="Internet",
            amount=Decimal("100.00"),
            date=datetime(2024, 1, 20, tzinfo=timezone.utc)
        )

    def test_daily_profit_calculation(self):
        """
        Verify math for a single day. 
        Note: Sale and Expense are on different days in setUp.
        """
        results = get_profit_calculations('daily')
        
        # We expect two entries: one for the 15th (Sale) and one for the 20th (Expense)
        sale_day = next(r for r in results if r['period'] == '2024-01-15')
        expense_day = next(r for r in results if r['period'] == '2024-01-20')

        # Sale day check
        self.assertEqual(sale_day['revenue'], 2000.0)
        self.assertEqual(sale_day['cogs'], 1200.0)
        self.assertEqual(sale_day['profit'], 800.0) # 2000 - 1200

        # Expense day check
        self.assertEqual(expense_day['expenses'], 100.0)
        self.assertEqual(expense_day['profit'], -100.0)

    def test_monthly_profit_aggregation(self):
        """Verify that sales and expenses in the same month are combined."""
        results = get_profit_calculations('monthly')
        
        # Both records are in January 2024
        jan_report = results[0]
        
        expected_profit = 2000.0 - 1200.0 - 100.0 # Rev - COGS - Exp
        self.assertEqual(jan_report['profit'], expected_profit)
        self.assertEqual(jan_report['revenue'], 2000.0)

    def test_invalid_period_raises_error(self):
        """Ensure the function guards against bad input."""
        with self.assertRaises(ValueError):
            get_profit_calculations('hourly')