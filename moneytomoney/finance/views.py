from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, Income, Budget, Tag, Category
from .forms import *
from django.views import View
from django.db.models import Q
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from datetime import *

class Login(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})
    
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('dashboard')  

        return render(request,'login.html', {"form":form})


class Logout(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')

class Register(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
        return render(request, 'register.html', {'form': form})

    
class Home(LoginRequiredMixin, View):
    def get(self, request):
        selected_month = request.session.get('selected_month', '')
        return render(request, 'home.html', {'selected_month': selected_month})

    def post(self, request):
        month = request.POST.get('month')
        if month:
            request.session['selected_month'] = month
            return redirect(f"/dashboard/?month={month}")
        return redirect('home')

from django.db.models import Q
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET
        month_str = query.get("month") or request.session.get("selected_month")
        if not month_str:
            return redirect('home')
        try:
            selected_month = datetime.strptime(month_str, "%Y-%m")
        except ValueError:
            return redirect('home')

        request.session['selected_month'] = month_str

        expenses = Expense.objects.filter(
            user=request.user,
            date__year=selected_month.year,
            date__month=selected_month.month
        ).order_by('-date')

        incomes = Income.objects.filter(
            user=request.user,
            date__year=selected_month.year,
            date__month=selected_month.month
        ).order_by('-date')

        budgets = Budget.objects.filter(
            user=request.user,
            month__year=selected_month.year,
            month__month=selected_month.month
        )

        tags = Tag.objects.all()

        search = query.get("search", "")
        a_filter = query.get("a_filter", "")  # field filter

        if search:
            if a_filter == "tags":
                expenses = expenses.filter(tags__name__icontains=search).distinct()
                incomes = incomes.filter(tags__name__icontains=search).distinct()
                tags = tags.filter(name__icontains=search)
            elif a_filter == "categories":
                expenses = expenses.filter(category__name__icontains=search).distinct()
                incomes = incomes.filter(category__name__icontains=search).distinct()
            elif a_filter == "payment_method":
                expenses = expenses.filter(payment_method__method__icontains=search).distinct()
                incomes = Income.objects.none()
            else:
                expenses = expenses.filter(title__icontains=search).distinct()
                incomes = incomes.filter(source__icontains=search).distinct()

        total_expense = sum(e.amount for e in expenses)
        total_income = sum(i.amount for i in incomes)
        total_budget = sum(b.amount for b in budgets)
        remaining_budget = total_budget - total_expense

        context = {
            "expenses": expenses,
            "incomes": incomes,
            "budgets": budgets,
            "tags": tags,
            "total_expense": total_expense,
            "total_income": total_income,
            "remaining_budget": remaining_budget,
            "search_query": search,
            "filter": a_filter,
            "selected_month": selected_month.strftime("%B %Y"),
            "month_str": month_str,
        }
        return render(request, "dashboard.html", context)



class ExpenseCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = ExpenseForm()
        return render(request, "expense.html", {"form": form})

    def post(self, request):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            form.save_m2m()
            return redirect('dashboard')

        return render(request, "expense.html", {"form": form})


class ExpenseUpdate(LoginRequiredMixin, View):
    def get(self, request, expense_id):
        expense = Expense.objects.get(pk=expense_id, user=request.user)
        form = ExpenseForm(instance=expense)
        return render(request, "expense.html", {
            "form": form,
        })

    def post(self, request, expense_id):
        expense = Expense.objects.get(pk=expense_id, user=request.user)
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

        return render(request, "expense.html", {
            "form": form
        })


class ExpenseDelete(LoginRequiredMixin, View):
    def get(self, request, expense_id):
        expense = Expense.objects.get(pk=expense_id)
        expense.delete()

        return redirect("dashboard")


class IncomeCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = IncomeForm()
        return render(request, "income.html", {"form": form})

    def post(self, request):
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            form.save_m2m()
            return redirect('dashboard')

        return render(request, "income.html", {"form": form})


class IncomeUpdate(LoginRequiredMixin, View):
    def get(self, request, income_id):
        income = Income.objects.get(pk=income_id)
        form = IncomeForm(instance=income)
        return render(request, "income.html", {
            "form": form,
        })

    def post(self, request, income_id):
        income = Income.objects.get(pk=income_id)
        form = IncomeForm(request.POST, instance=income)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

        return render(request, "income.html", {
            "form": form
        })


class IncomeDelete(LoginRequiredMixin, View):
    def get(self, request, income_id):
        income = Income.objects.get(pk=income_id)
        income.delete()

        return redirect("dashboard")


class BudgetCreateUpdate(LoginRequiredMixin, View):
    def get(self, request):
        form = BudgetForm()
        return render(request, "budget.html", {"form": form})

    def post(self, request):
        form = BudgetForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            amount = form.cleaned_data['amount']

            budget, created = Budget.objects.update_or_create(
                user=request.user,
                month=month,
                defaults={'amount': amount}
            )
            return redirect('dashboard')

        return render(request, "budget.html", {"form": form})


class TagCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = TagForm()
        tags = Tag.objects.all()
        return render(request, "tag.html", {
            "form": form,
            "tags": tags,
        })

    def post(self, request):
        form = TagForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('tag_create')

        return render(request, "tag.html", {
            "form": form
        })


class TagUpdate(LoginRequiredMixin, View):
    def get(self, request, tag_id):
        tag = Tag.objects.get(pk=tag_id)
        form = TagForm(instance=tag)
        return render(request, "tagedit.html", {
            "form": form,
        })

    def post(self, request, tag_id):
        tag = Tag.objects.get(pk=tag_id)
        form = TagForm(request.POST, instance=tag)

        if form.is_valid():
            form.save()
            return redirect('tag_create')

        return render(request, "tagedit.html", {
            "form": form
        })


class TagDelete(LoginRequiredMixin, View):
    def get(self, request, tag_id):
        tag = Tag.objects.get(pk=tag_id)
        tag.delete()

        return redirect("tag_create")


class CategoryCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = CategoryForm()
        categories = Category.objects.all()
        return render(request, "category.html", {
            "form": form,
            "categories": categories,
        })

    def post(self, request):
        form = CategoryForm(request.POST)
        categories = Category.objects.all()

        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_create')

        return render(request, "category.html", {
            "form": form,
            "categories": categories,
        })


class CategoryUpdate(LoginRequiredMixin, View):
    def get(self, request, category_id):
        category = Category.objects.get(pk=category_id)
        form = CategoryForm(instance=category)
        return render(request, "categoryedit.html", {
            "form": form,
        })

    def post(self, request, category_id):
        category = Category.objects.get(pk=category_id)
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect('category_create')

        return render(request, "categoryedit.html", {
            "form": form
        })


class CategoryDelete(LoginRequiredMixin, View):
    def get(self, request, category_id):
        category = Category.objects.get(pk=category_id)
        category.delete()

        return redirect('category_create')


class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, 'profile.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        return render(request, 'profile.html', {'form': form})


class ChangePassword(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'changepass.html', {"form": form})

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        return render(request, 'changepass.html', {'form': form})
