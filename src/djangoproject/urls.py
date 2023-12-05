"""djangoproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  
from stockmgmt import views
# from django.contrib.auth import views as auth_views
# from registration.backends.default import views as registration_views


       

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('registration.backends.default.urls')),
    # path('loginn/',include('signin.urls')),
    path('home/', views.home, name='home'),
    path('list_item/', views.list_item),
    path('add_items/', views.add_items, name='add_items'),
    path('update_items/<str:pk>/', views.update_items, name="update_items"),
    path('delete_items/<str:pk>/', views.delete_items, name="delete_items"),
    path('stock_detail/<str:pk>/', views.stock_detail, name="stock_detail"),
    # path('issue_items/<str:pk>/', views.issue_items, name="issue_items"),
    path('receive_items/<str:pk>/', views.receive_items, name="receive_items"),
    path('reorder_level/<str:pk>/', views.reorder_level, name="reorder_level"),
    path('addcompany/',views.add_itemcompany, name='addcompany'),
    path('setting_app/', views.Settings_app, name='Settings_app'),
    path('addvender/', views.add_vender, name='addvender'),
    path('addExpense/', views.add_ExpenseCategory, name='addExpense'),
    path('add-items/', views.add_CatItems, name='add-items'),
    path('addcategory/', views.add_category, name='addcategory'),
    # path('make_sale/', views.make_sale, name='make_sale'),
    path('add_cash/', views.add_cash, name='add_cash'),
    path('action_history/', views.action_history, name='action_history'),
    path('returnitem/', views.sales_return, name='returnitem'),
    path('defective-items/', views.defective_item_list, name='defective-items'),
    path('replacement-items/', views.replacement_item, name='replacement-items'),
    path('make_sale/', views.sale_l, name='make_sale'),
    path('create-form/', views.create_form, name='create-form'),
    path('expenses/', views.expenses_list, name='expenses_list'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('Cost-of-goods/', views.CostofGoods, name='Cost-of-goods'),
    path('sales_return_list/', views.sales_return_list, name='sales_return_list'),
    path('purchase_record_list/', views.purchase_record_list, name='purchase_record_list'),
    path('sales_record_list/', views.sales_record_list, name='sales_record_list'),
    path('profit_loss/', views.Profit, name='profit_loss'),
    path('purchase_items/', views.Add_itemTriger, name='purchase_items'),
    path('account_pay/', views.account_pay, name='account_pay'),
    path('stock_return/', views.stock_return, name='stock_return'),
    path('purchase_returns_records/', views.purchase_returns_records, name='purchase_returns_records'),
    path('account_receiveable/', views.account_receiveable, name='account_receiveable'),
    path('balance_sheet/', views.balance_sheet, name='balance_sheet'),
    path('get-items/', views.get_items, name='get_items'),
    path('Replace-create-form/', views.Replace_create_form, name='Replace-create-form'),
    path('Replace_sale/', views.Replace_l, name='Replace_sale'),
    path('add_Equity/', views.add_Equity, name='add_Equity'),


    path("admin/", admin.site.urls),
    path("index", views.index, name="index"),
    path("load_items/", views.load_items, name="load_items"),  # Change the path to "load_items/"


    path('delete_sale/<int:sale_id>/',views.delete_sale, name='delete_sale'),
    path('add_stock/', views.add_stock, name='add_stock'),


    path('get_items/', views.get_items, name='get_items'),


    #new file
    path("",views.user_login,name="user_login"),
    path("signup/", views.sign_up, name="sign_up"),
    path("profile/", views.user_profile, name="user_profile"),
    path("logout/", views.user_logout, name="log_out"),
    path("changepassword/", views.user_change_password, name="changepassword"),
    path("userdetail/<int:id>", views.user_detail, name="user_detail"),


    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('accounts/', include('django.contrib.auth.urls')),  # Use 'accounts/' as the prefix
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # path('accounts/', include('registration.backends.default.urls')),

    # path('forgot-password/', auth_views.PasswordResetView.as_view(template_name='forgot_password.html'), name='forgot_password'),
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='auth_password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    



#     path('list_history/', views.list_history, name='list_history'),
]
