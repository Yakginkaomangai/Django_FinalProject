from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'), 
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),

    path('expenses/add/', views.ExpenseCreate.as_view(), name='expense_create'),
    path('expenses/<int:expense_id>/edit/', views.ExpenseUpdate.as_view(), name='expense_update'),
    path('expenses/<int:expense_id>/delete/', views.ExpenseDelete.as_view(), name='expense_delete'),

    path('incomes/add/', views.IncomeCreate.as_view(), name='income_create'),
    path('incomes/<int:income_id>/edit/', views.IncomeUpdate.as_view(), name='income_update'),
    path('incomes/<int:income_id>/delete/', views.IncomeDelete.as_view(), name='income_delete'),

    path('budget/', views.BudgetCreateUpdate.as_view(), name='budget_create'),

    path('tags/add/', views.TagCreate.as_view(), name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.TagUpdate.as_view(), name='tag_update'),
    path('tags/<int:tag_id>/delete/', views.TagDelete.as_view(), name='tag_delete'),
    
    path('categories/add/', views.CategoryCreate.as_view(), name='category_create'),
    path('categories/<int:category_id>/edit/', views.CategoryUpdate.as_view(), name='category_update'),
    path('categories/<int:category_id>/delete/', views.CategoryDelete.as_view(), name='category_delete'),

    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('profile/changepassword/', views.ChangePassword.as_view(), name='change_pass'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register')
]
