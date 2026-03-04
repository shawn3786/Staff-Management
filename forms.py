# staff/forms.py
from django import forms
from .models import Branch, Staff, Inventory, Expense

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'branch_type','branch_id','email', 'address', 'phone', 'manager_name']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'category', 'sku', 'current_stock', 'low_stock_alert', 'unit_cost', 'unit_price', 'supplier']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'description', 'expense_date', 'is_recurring', 'recurrence_frequency']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }