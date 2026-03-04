# staff/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import json
#from .models import Branch, Staff, Inventory, Sale, Expense, ReportConfiguration
from django.core.serializers import serialize
import openpyxl
from django.db.models import Sum

# Authentication Views
def landing(request):
    return render(request, 'staff/landing.html')

def login_choice(request):
    return render(request, 'staff/login_choice.html')

def admin_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid username or password"

    return render(request, "staff/login_choice.html", {"error": error})

def employee_login(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Employee ID")
            return redirect('employee_login')

    return render(request, 'staff/employee_login.html')

@login_required
def dashboard(request):
    user = request.user
    hour = timezone.now().hour

    if hour < 12:
        greeting = "Good Morning"
    elif hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    context = {
        "greeting": f"{greeting}, {user.username}",
    }
    return render(request, "admin_dashboard.html", context)

# Branch Management Views
@login_required
def branches_list(request):
    """Main branches overview page"""
    branches = Branch.objects.filter(is_active=True)

    # Calculate metrics for each branch
    branches_data = []
    for branch in branches:
        branches_data.append({
            'id': str(branch.id),
            'name': branch.name,
            'branch_type': branch.branch_type,
            'branch_id': branch.branch_id,
            'address': branch.address,
            'email': branch.email,
            'phone': branch.phone,
            'manager_name': branch.manager_name,
            'total_staff': branch.total_staff,
            'total_inventory_value': float(branch.total_inventory_value),
            'monthly_revenue': float(branch.monthly_revenue),
            'performance_score': branch.performance_score,
        })

    context = {
        'branches': branches_data,
        'page_title': 'Branch Management System'
    }
    return render(request, 'staff/branches_list.html', context)

@login_required
def branch_detail(request, branch_id):
    """Branch detail page with all analytics"""
    branch = get_object_or_404(Branch, id=branch_id, is_active=True)

    # Get date ranges for analytics
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)

    # Staff data
    staff_members = Staff.objects.filter(branch=branch, is_active=True)

    # Inventory data
    inventory_items = Inventory.objects.filter(branch=branch, is_active=True)

    # Sales data for last 30 days
    recent_sales = Sale.objects.filter(branch=branch, sale_date__gte=thirty_days_ago)

    # Expense data
    expenses = Expense.objects.filter(branch=branch, expense_date__gte=thirty_days_ago)

    # Performance metrics
    total_revenue = recent_sales.aggregate(total=Sum('revenue'))['total'] or 0
    total_cost = recent_sales.aggregate(total=Sum('cost'))['total'] or 0
    gross_profit = total_revenue - total_cost
    profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

    context = {
        'branch': branch,
        'staff_members': staff_members,
        'inventory_items': inventory_items,
        'recent_sales': recent_sales,
        'expenses': expenses,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'gross_profit': gross_profit,
        'profit_margin': profit_margin,
    }
    return render(request, 'staff/branch_detail.html', context)

@login_required
@require_http_methods(["POST"])
def create_branch(request):
    """Create a new branch"""

    try:
        data = json.loads(request.body)
        branch = Branch.objects.create(
            name=data.get('name'),
            branch_type=data.get('branch_type'),
            branch_id=data.get('branch_id'),
            email=data.get('email'),
            address=data.get('address'),
            phone=data.get('phone'),
            manager_name=data.get('manager_name')
        )
        return JsonResponse({'success': True, 'branch_id': str(branch.id)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    print("Received data:", data)
@login_required    
@require_http_methods(["DELETE"])
def delete_branch(request, branch_id):
    """Delete a branch (soft delete)"""
    try:
        branch = get_object_or_404(Branch, id=branch_id)
        branch.is_active = False
        branch.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# API Endpoints
@login_required
@require_http_methods(["GET"])
def api_branches_list(request):
    """API endpoint for branches list"""
    branches = Branch.objects.filter(is_active=True)

    branches_data = []
    for branch in branches:
        branches_data.append({
            'id': str(branch.id),
            'name': branch.name,
            'address': branch.address,
            'email': branch.email,
            'phone': branch.phone,
            'manager_name': branch.manager_name,
            'total_staff': branch.total_staff,
            'total_inventory_value': float(branch.total_inventory_value),
            'performance_score': branch.performance_score,
        })

    return JsonResponse({'branches': branches_data})

@login_required
@require_http_methods(["POST"])
def api_create_inventory(request):
    """API endpoint to create inventory item"""
    try:
        data = json.loads(request.body)
        branch_id = data.get('branch')

        if not branch_id:
            return JsonResponse({'success': False, 'error': 'Branch ID is required'})

        branch = get_object_or_404(Branch, id=branch_id)

        inventory_item = Inventory.objects.create(
            branch=branch,
            name=data.get('name'),
            category=data.get('category'),
            current_stock=data.get('current_stock', 0),
            low_stock_alert=data.get('low_stock_alert', 10),
            unit_cost=data.get('unit_cost', 0),
            unit_price=data.get('unit_price', 0),
        )
        return JsonResponse({'success': True, 'id': str(inventory_item.id)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def api_create_expense(request):
    """API endpoint to create expense"""
    try:
        data = json.loads(request.body)
        branch_id = data.get('branch')

        if not branch_id:
            return JsonResponse({'success': False, 'error': 'Branch ID is required'})

        branch = get_object_or_404(Branch, id=branch_id)

        expense = Expense.objects.create(
            branch=branch,
            expense_type=data.get('expense_type'),
            amount=data.get('amount', 0),
            expense_date=data.get('expense_date'),
            description=data.get('description', ''),
        )
        return JsonResponse({'success': True, 'id': str(expense.id)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Data Export and Additional Functions
@login_required
def branch_sales_data(request, branch_id):
    """Get sales data for charts"""
    branch = get_object_or_404(Branch, id=branch_id)

    # Last 7 days sales data
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)

    sales_data = []
    current_date = start_date
    while current_date <= end_date:
        daily_sales = Sale.objects.filter(
            branch=branch,
            sale_date__date=current_date.date()
        ).aggregate(total=Sum('revenue'))['total'] or 0
        sales_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
        current_date += timedelta(days=1)

    return JsonResponse({'sales_data': sales_data})

@login_required
def branch_performance_data(request, branch_id):
    """Get performance data for charts"""
    branch = get_object_or_404(Branch, id=branch_id)

    # Last 12 months performance data
    performance_data = []
    for i in range(11, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        month_sales = Sale.objects.filter(
            branch=branch,
            sale_date__month=month_date.month,
            sale_date__year=month_date.year
        )

        monthly_revenue = month_sales.aggregate(total=Sum('revenue'))['total'] or 0
        monthly_cost = month_sales.aggregate(total=Sum('cost'))['total'] or 0
        monthly_profit = monthly_revenue - monthly_cost
        margin = (monthly_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0

        performance_data.append({
            'month': month_date.strftime('%b %Y'),
            'revenue': float(monthly_revenue),
            'profit': float(monthly_profit),
            'margin': float(margin)
        })

    return JsonResponse({'performance_data': performance_data})



@login_required
def export_branch_excel(request, branch_id):
    """Export branch data as Excel file"""
    branch = get_object_or_404(Branch, id=branch_id)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Branch Data"

    # Add headers
    ws.append(['Branch Name', 'Manager', 'Active Staff', 'Inventory Value', 'Monthly Revenue', 'Performance Score', 'Export Date'])
    ws.append([
        branch.name,
        branch.manager_name,
        branch.total_staff,
        float(branch.total_inventory_value),
        float(branch.monthly_revenue),
        branch.performance_score,
        timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{branch.name}_export.xlsx"'
    wb.save(response)
    return response
@login_required
@require_http_methods(["POST"])
def sync_sales_data(request, branch_id):
    """Sync data with external sales application"""
    try:
        # Simulate API call to sales app
        return JsonResponse({'success': True, 'message': 'Sales data synced successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def save_report_config(request, branch_id):
    """Save report configuration"""
    branch = get_object_or_404(Branch, id=branch_id)

    try:
        data = json.loads(request.body)
        config, created = ReportConfiguration.objects.update_or_create(
            branch=branch,
            defaults={
                'email': data.get('email'),
                'frequency': data.get('frequency', 'monthly'),
                'include_sales': data.get('include_sales', True),
                'include_inventory': data.get('include_inventory', True),
                'include_expenses': data.get('include_expenses', True),
                'include_performance': data.get('include_performance', True),
            }
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



@login_required
@require_http_methods(["GET"])
def api_inventory_list(request, branch_id):
    """API endpoint to list inventory items for a branch"""
    branch = get_object_or_404(Branch, id=branch_id)
    inventory_items = Inventory.objects.filter(branch=branch, is_active=True)
    items = []
    for item in inventory_items:
        items.append({
            'id': str(item.id),
            'name': item.name,
            'category': item.category,
            'current_stock': item.current_stock,
            'low_stock_alert': item.low_stock_alert,
            'unit_cost': float(item.unit_cost),
            'unit_price': float(item.unit_price),
            'total_value': float(item.total_value),
            # Add more fields if needed
        })
    return JsonResponse({'inventory': items})

@login_required
@require_http_methods(["GET"])
def api_expense_list(request, branch_id):
    """API endpoint to list expenses for a branch"""
    branch = get_object_or_404(Branch, id=branch_id)
    expenses = Expense.objects.filter(branch=branch)
    items = []
    for expense in expenses:
        items.append({
            'id': str(expense.id),
            'expense_type': expense.expense_type,
            'amount': float(expense.amount),
            'expense_date': expense.expense_date.strftime('%Y-%m-%d'),
            'description': expense.description,
            # Add more fields if needed
        })
    return JsonResponse({'expenses': items})

@login_required
@require_http_methods(["POST"])
def api_create_inventory_bulk(request):
    """API endpoint to create multiple inventory items"""
    try:
        data = json.loads(request.body)
        branch_id = data.get('branch')
        items = data.get('items', [])
        if not branch_id or not items:
            return JsonResponse({'success': False, 'error': 'Branch ID and items are required'})
        branch = get_object_or_404(Branch, id=branch_id)
        created_ids = []
        for item in items:
            inventory_item = Inventory.objects.create(
                branch=branch,
                name=item.get('name'),
                category=item.get('category'),
                current_stock=item.get('current_stock', 0),
                low_stock_alert=item.get('low_stock_alert', 10),
                unit_cost=item.get('unit_cost', 0),
                unit_price=item.get('unit_price', 0),
            )
            created_ids.append(str(inventory_item.id))
        return JsonResponse({'success': True, 'ids': created_ids})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Employee, Branch
from django.contrib import messages


def dashboard(request):
    employees = Employee.objects.filter(status='active')
    former_employees = Employee.objects.filter(status='terminated')
    return render(request, 'dashboard.html', {
        'employees': employees,
        'former_employees': former_employees
    })


def hire_employee(request):
    if request.method == 'POST':
        data = request.POST

        employee = Employee.objects.create(
            employee_id=data.get('employeeId'),
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            employee_type=data.get('employeeType'),
            role=data.get('role'),
            residence_permit=data.get('residencePermit'),
            contract_details=data.get('contractDetails'),
            contract_expiry=data.get('contractExpiry'),
            hourly_wage=data.get('hourlyWage'),
            bank_name=data.get('bankName'),
            account_number=data.get('accountNumber'),
            social_security=data.get('socialSecurity'),
            tax_id=data.get('taxId'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            emergency_contact=data.get('emergencyContact'),
            emergency_phone=data.get('emergencyPhone'),
            status='active'
        )

        # If branch selected
        branch_id = data.get('branchLocation')
        if branch_id:
            branch = Branch.objects.get(id=branch_id)
            employee.branch = branch
            employee.save()

        messages.success(request, "Employee hired successfully!")
        return redirect('dashboard')

    branches = Branch.objects.all()
    return render(request, 'hire_employee.html', {'branches': branches})


def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    return render(request, 'employee_details.html', {'employee': employee})


def terminate_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.status = 'terminated'
    employee.save()
    messages.error(request, "Employee terminated.")
    return redirect('dashboard')


def get_branch_data(request):
    branches = list(Branch.objects.values())
    return JsonResponse({'branches': branches})
