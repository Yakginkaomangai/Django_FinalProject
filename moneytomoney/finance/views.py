from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, Income, Budget, Tag, Category
from .forms import ExpenseForm, IncomeForm, BudgetForm, TagForm, ProfileForm, CategoryForm
from django.views import View
from django.db.models import Q
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


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
    

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET

        expenses = Expense.objects.filter(user=request.user).order_by('-date')
        incomes = Income.objects.filter(user=request.user).order_by('-date')
        budgets = Budget.objects.filter(user=request.user).order_by('-month')
        tags = Tag.objects.all()

        search = query.get("search")
        if search:
            expenses = expenses.filter(
                Q(title__icontains=search) |
                Q(category__name__icontains=search) |
                Q(payment_method__method__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
            incomes = incomes.filter(
                Q(source__icontains=search)
            )
            budgets = budgets.filter(
                Q(amount__icontains=search)
            )
            tags = tags.filter(name__icontains=search)


        total_expense = sum(e.amount for e in expenses)
        total_income = sum(i.amount for i in incomes)
        remaining_budget = sum(b.amount for b in budgets) - total_expense

        context = {
            "expenses": expenses,
            "incomes": incomes,
            "budgets": budgets,
            "tags": tags,
            "total_expense": total_expense,
            "total_income": total_income,
            "remaining_budget": remaining_budget,
            "search_query": search or "",
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

            # update หรือสร้าง budget ใหม่ถ้าไม่มี
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
            category.user = request.user  # ผูกกับ user
            category.save()
            return redirect('category_create')  # กลับมาหน้าเดิม

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
            form.save()  # Password จะถูกเข้ารหัสโดย set_password() ใน form
            return redirect('dashboard')
        return render(request, 'profile.html', {'form': form})