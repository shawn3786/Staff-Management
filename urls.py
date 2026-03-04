from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),             # root -> landing page
    path('login-choice/', views.login_choice, name='login_choice'),  # separate login choice page
    path('admin-login/', views.admin_login, name='admin_login'),
    path('employee-login/', views.employee_login, name='employee_login'),
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('branches/', views.branches_list, name='branches_list'),
    # Branch Management
    path('branches/', views.branches_list, name='branches_list'),
    path('branches/create/', views.create_branch, name='create_branch'),
    path('branches/<uuid:branch_id>/', views.branch_detail, name='branch_detail'),
    path('branches/<uuid:branch_id>/delete/', views.delete_branch, name='delete_branch'),
    path('api/branches/<uuid:branch_id>/inventory/', views.api_inventory_list, name='api_inventory_list'),
    path('api/branches/<uuid:branch_id>/expenses/', views.api_expense_list, name='api_expense_list'),
    path('api/inventory/create-bulk/', views.api_create_inventory_bulk, name='api_create_inventory_bulk'),
    path('branches/<uuid:branch_id>/export/', views.export_branch_excel, name='export_branch_excel'),
           # Branch Actions
    path('branches/<uuid:branch_id>/sync-sales/', views.sync_sales_data, name='sync_sales_data'),
    path('branches/<uuid:branch_id>/save-report-config/', views.save_report_config, name='save_report_config'),

           # API Endpoints
    path('api/branches/list/', views.api_branches_list, name='api_branches_list'),
    path('api/inventory/create/', views.api_create_inventory, name='api_create_inventory'),
    path('api/expenses/create/', views.api_create_expense, name='api_create_expense'),
    path('api/branches/<uuid:branch_id>/sales-data/', views.branch_sales_data, name='branch_sales_data'),
    path('api/branches/<uuid:branch_id>/performance-data/', views.branch_performance_data, name='branch_performance_data'),

    ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('hire/', views.hire_employee, name='hire_employee'),
#     path('employee/<str:employee_id>/', views.employee_detail, name='employee_detail'),
#     path('employee/<str:employee_id>/terminate/', views.terminate_employee, name='terminate_employee'),
#     path('api/branches/', views.get_branch_data, name='branch_api'),
# ]
