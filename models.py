# staff/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
#from models import Branch



# class Branch(models.Model):

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100, unique=True)
#     branch_type = models.CharField(max_length=20)
#     branch_id = models.CharField(max_length=6, unique=True)
#     email = models.EmailField()
#     address = models.TextField()
#     phone = models.CharField(max_length=15)
#     manager_name = models.CharField(max_length=100)
#     opening_date = models.DateField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name_plural = "Branches"
#         ordering = ['name']

#     def __str__(self):
#         return self.name

#     @property
#     def total_staff(self):
#         return self.staff_set.filter(is_active=True).count()

#     @property
#     def total_inventory_value(self):
#         return sum(item.total_value for item in self.inventory_items.filter(is_active=True))

#     @property
#     def monthly_revenue(self):
#         from django.utils import timezone
#         from django.db.models import Sum
#         current_month = timezone.now().month
#         current_year = timezone.now().year
#         sales = self.sales.filter(
#             sale_date__month=current_month,
#             sale_date__year=current_year
#         ).aggregate(total=Sum('revenue'))['total']
#         return sales or 0

#     @property
#     def total_profit(self):
#         from django.db.models import Sum
#         sales_data = self.sales.aggregate(
#             total_revenue=Sum('revenue'),
#             total_cost=Sum('cost')
#         )
#         revenue = sales_data['total_revenue'] or 0
#         cost = sales_data['total_cost'] or 0
#         return revenue - cost

#     @property
#     def profit_margin(self):
#         from django.db.models import Sum
#         sales_data = self.sales.aggregate(
#             total_revenue=Sum('revenue'),
#             total_cost=Sum('cost')
#         )
#         revenue = sales_data['total_revenue'] or 0
#         cost = sales_data['total_cost'] or 0
#         if revenue == 0:
#             return 0
#         return ((revenue - cost) / revenue) * 100

#     @property
#     def performance_score(self):
#         # Calculate performance based on various metrics
#         base_score = 70  # Base score
#         if self.monthly_revenue > 10000:
#             base_score += 15
#         if self.profit_margin > 20:
#             base_score += 15
#         return min(base_score, 100)


# class Staff(models.Model):
#     POSITION_CHOICES = [
#         ('manager', 'Manager'),
#         ('supervisor', 'Supervisor'),
#         ('cashier', 'Cashier'),
#         ('chef', 'Chef'),
#         ('waiter', 'Waiter'),
#         ('cleaner', 'Cleaner'),
#         ('other', 'Other'),
#     ]

#     DEPARTMENT_CHOICES = [
#         ('management', 'Management'),
#         ('kitchen', 'Kitchen'),
#         ('service', 'Service'),
#         ('sales', 'Sales'),
#         ('support', 'Support'),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     position = models.CharField(max_length=20, choices=POSITION_CHOICES)
#     department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
#     email = models.EmailField()
#     phone = models.CharField(max_length=15)
#     hire_date = models.DateField()
#     salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name_plural = "Staff"
#         ordering = ['last_name', 'first_name']

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} - {self.position}"

#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"


# class Inventory(models.Model):
#     CATEGORY_CHOICES = [
#         ('food', 'Food'),
#         ('beverage', 'Beverage'),
#         ('supplies', 'Supplies'),
#         ('equipment', 'Equipment'),
#         ('other', 'Other'),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory_items')
#     name = models.CharField(max_length=100)
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
#     sku = models.CharField(max_length=50, unique=True)
#     current_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
#     low_stock_alert = models.IntegerField(default=10, validators=[MinValueValidator(0)])
#     unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     supplier = models.CharField(max_length=100, blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['name']

#     def __str__(self):
#         return f"{self.name} - {self.branch.name}"

#     @property
#     def total_value(self):
#         return self.current_stock * self.unit_cost

#     @property
#     def profit_per_unit(self):
#         return self.unit_price - self.unit_cost

#     @property
#     def margin_percentage(self):
#         if self.unit_price == 0:
#             return 0
#         return (self.profit_per_unit / self.unit_price) * 100

#     @property
#     def stock_status(self):
#         if self.current_stock == 0:
#             return 'out_of_stock'
#         elif self.current_stock <= self.low_stock_alert:
#             return 'low_stock'
#         else:
#             return 'in_stock'


# class Sale(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='sales')
#     inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
#     quantity = models.IntegerField(validators=[MinValueValidator(1)])
#     revenue = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     profit = models.DecimalField(max_digits=10, decimal_places=2)
#     sale_date = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-sale_date']

#     def save(self, *args, **kwargs):
#         self.profit = self.revenue - self.cost
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Sale: {self.inventory_item.name} - {self.quantity} units"


# class Expense(models.Model):
#     EXPENSE_TYPES = [
#         ('supplier', 'Supplier Cost'),
#         ('rent', 'Rent'),
#         ('utilities', 'Utilities'),
#         ('salaries', 'Salaries'),
#         ('maintenance', 'Maintenance'),
#         ('marketing', 'Marketing'),
#         ('other', 'Other'),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='expenses')
#     expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
#     amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     description = models.TextField(blank=True)
#     expense_date = models.DateField()
#     is_recurring = models.BooleanField(default=False)
#     recurrence_frequency = models.CharField(max_length=20, blank=True, choices=[
#         ('weekly', 'Weekly'),
#         ('monthly', 'Monthly'),
#         ('quarterly', 'Quarterly'),
#         ('yearly', 'Yearly'),
#     ])
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-expense_date']

#     def __str__(self):
#         return f"{self.get_expense_type_display()} - {self.amount}"


# class ReportConfiguration(models.Model):
#     FREQUENCY_CHOICES = [
#         ('weekly', 'Weekly'),
#         ('monthly', 'Monthly'),
#         ('quarterly', 'Quarterly'),
#     ]

#     branch = models.OneToOneField(Branch, on_delete=models.CASCADE)
#     email = models.EmailField()
#     frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
#     include_sales = models.BooleanField(default=True)
#     include_inventory = models.BooleanField(default=True)
#     include_expenses = models.BooleanField(default=True)
#     include_performance = models.BooleanField(default=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Report Config - {self.branch.name}"
# class ProfitLoss(models.Model):
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="profit_loss_reports")
#     month = models.DateField()  # store month as YYYY-MM-01
#     total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     def __str__(self):
#         return f"{self.branch.name} - {self.month.strftime('%B %Y')}"




from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.location})"


class Employee(models.Model):
    EMPLOYEE_TYPE = (
        ('office', 'Office Staff'),
        ('production', 'Production'),
        ('branch', 'Branch Work'),
    )

    STATUS = (
        ('active', 'Active'),
        ('terminated', 'Terminated'),
    )

    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)

    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE)
    role = models.CharField(max_length=120, null=True, blank=True)

    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    residence_permit = models.CharField(max_length=100, null=True, blank=True)
    contract_details = models.TextField(null=True, blank=True)
    contract_expiry = models.DateField(null=True, blank=True)

    hourly_wage = models.FloatField(null=True, blank=True)

    bank_name = models.CharField(max_length=120, null=True, blank=True)
    account_number = models.CharField(max_length=120, null=True, blank=True)

    social_security = models.CharField(max_length=120, null=True, blank=True)
    tax_id = models.CharField(max_length=120, null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    emergency_contact = models.CharField(max_length=120, null=True, blank=True)
    emergency_phone = models.CharField(max_length=120, null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS, default='active'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"
