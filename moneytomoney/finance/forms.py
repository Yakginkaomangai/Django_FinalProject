from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import Expense, Income, Budget, Tag, Category, PaymentMethod
from django.core.exceptions import ValidationError
from datetime import date

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}),
        strip=False
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Enter your email'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter first name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter last name'}))
    
    package = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        empty_label="Select package",
        widget=forms.Select(attrs={'class':'form-select'}),
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Enter password'}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Enter Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "package")
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email already in use.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

class ExpenseForm(forms.ModelForm):
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
        required=True,
        empty_label="Select Payment Method",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'payment_method', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter expense title'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0.")
        return amount

    def clean_date(self):
        expense_date = self.cleaned_data.get('date')
        if expense_date > date.today():
            raise ValidationError("Date cannot be in the future.")
        return expense_date

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'date', 'category', 'tags']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter income source'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0.")
        return amount

    def clean_date(self):
        income_date = self.cleaned_data.get('date')
        if income_date > date.today():
            raise ValidationError("Date cannot be in the future.")
        return income_date

class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        input_formats=['%Y-%m'],
    )

    class Meta:
        model = Budget
        fields = ['month', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Budget Amount'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Budget amount must be greater than 0.")
        return amount

    def clean_month(self):
        month = self.cleaned_data['month']
        return month.replace(day=1)

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag Name'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Tag.objects.filter(name__iexact=name).exists():
            raise ValidationError("Tag with this name already exists.")
        return name

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError("Category with this name already exists.")
        return name

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")
        return username


class ChangepassForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Old password'})
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'New password'}),
        strip=False
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirm password'}),
        strip=False
    )