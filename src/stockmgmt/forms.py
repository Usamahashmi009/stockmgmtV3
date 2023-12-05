from django import forms
from .models import *
from django.forms import inlineformset_factory
from django.forms import formset_factory
from django.forms.widgets import Select
from django.contrib.auth.forms import UserCreationForm , UserChangeForm
from django import forms
from django.contrib.auth.models import User
from dynamic_forms import DynamicField, DynamicFormMixin


# class universityform(forms.Form):
#     category=forms.ModelChoiceField(
#         queryset=Category.objects.all(),
#         initial=Category.objects.first(),
#     )


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['vender', 'category', 'item_name', 'quantity', 'rate', 'company','account_payable']


class BatchForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['batch_number']


    
class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)

    class Meta:
        model = Stock
        fields = ['category', 'item_name']



class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']



class AddItemCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']


# forms.py

class CustomStockWidget(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        # option_value will be the Stock object
        batch_number = option_value.batch_number
        item_name = option_value.item_name.name if option_value.item_name else "N/A"  # Access the name attribute of Itemsmodel
        quantity = option_value.quantity
        rate = option_value.rate



        # Customize the display as needed
        display_text = f"{batch_number} - {item_name} - Quantity: {quantity} - Rate: {rate}"

        return super().render_option(selected_choices, option_value.pk, display_text)

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['stock', 'rate', 'sale_quantity', 'received_by','account_recieveable']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the queryset for the stock field
        stock_field = self.fields['stock']
        stock_queryset = stock_field.queryset

        # Modify the choices for the stock field to include rates
        stocks_with_rates = Stock.objects.filter(rate__isnull=False)
        stock_choices = [(stock.id, f"{stock} - Rate: {stock.rate}") for stock in stocks_with_rates]
        stock_field.choices = stock_choices

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Apply the custom widget to the stock field
    #     self.fields['stock'].widget = CustomStockWidget()


       
class AddExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['Exp','amount']




class AddVenderForm(forms.ModelForm):
    class Meta:
        model = Vender
        fields = ['name']

    


class ExpenseCatForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name']



class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity','rate']



class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity']



class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['reorder_level']



class AddCashForm(forms.ModelForm):
    class Meta:
        model = AddCash
        fields = ['cash']



class AddItemsform(forms.ModelForm):
    class Meta:
        model = Itemsmodel
        fields = ['name' ]



class SalesReturnForm(forms.Form):
    batch_number = forms.ChoiceField(choices=[], required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    item_name = forms.ModelChoiceField(queryset=Itemsmodel.objects.all())
    price = forms.IntegerField()
    quantity = forms.IntegerField()
    action = forms.ChoiceField(
        choices=[('defective', 'Defective'),  ('no_action', 'No action')],
        widget=forms.RadioSelect,
        required=False
    )


    def __init__(self, *args, **kwargs):
        super(SalesReturnForm, self).__init__(*args, **kwargs)
        distinct_batch_numbers = Stock.objects.values_list('batch_number', flat=True).distinct()
        self.fields['batch_number'].choices = [(batch_number, batch_number) for batch_number in distinct_batch_numbers]

# class ReplacementForm(forms.Form):
#     batch_number = forms.ChoiceField(choices=[], required=False, )
#     category = forms.ModelChoiceField(queryset=Category.objects.all())
#     item_name = forms.ModelChoiceField(queryset=Itemsmodel.objects.all())
#     price = forms.IntegerField()
#     quantity = forms.IntegerField()
#     sub_cash = forms.IntegerField()

#     def __init__(self, *args, **kwargs):
#         super(ReplacementForm, self).__init__(*args, **kwargs)
#         distinct_batch_numbers = Stock.objects.values_list('batch_number', flat=True).distinct()
#         self.fields['batch_number'].choices = [(batch_number, batch_number) for batch_number in distinct_batch_numbers]

class ReplacementSaleForm(forms.ModelForm):
    cash_adjust = forms.IntegerField()
    class Meta:
        model = Sale
        fields = ['stock', 'rate', 'sale_quantity','cash_adjust', 'account_recieveable']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the queryset for the stock field
        stock_field = self.fields['stock']
        stock_queryset = stock_field.queryset

        # Modify the choices for the stock field to include rates
        stocks_with_rates = Stock.objects.filter(rate__isnull=False)
        stock_choices = [(stock.id, f"{stock} - Rate: {stock.rate}") for stock in stocks_with_rates]
        stock_field.choices = stock_choices





class SignUpForm(UserCreationForm):
    password2 = forms.CharField(label="Confirm password (again) ",widget= forms.PasswordInput)


    class Meta:
        model = User
        fields = ["username","first_name","last_name","email"]
        labels={"email":"Email"}


class EditUserprofileForm(UserChangeForm):
    password = None
    class Meta:
        model =User
        fields = ["username","first_name","last_name","email", "date_joined","last_login"]
        labels={"email":"Email"}




class EditAdminprofileForm(UserChangeForm):
    password = None
    class Meta:
        model =User
        fields = "__all__"
        labels={"email":"Email"}

class StockReturnForm(forms.ModelForm):
    class Meta:
        model = StockReturn
        fields = ['stock', 'return_quantity']

    def clean_return_quantity(self):
        return_quantity = self.cleaned_data['return_quantity']
        stock = self.cleaned_data.get('stock')

        if stock and return_quantity > stock.quantity:
            raise forms.ValidationError('Not enough stock to return.')

        return return_quantity

class OwnerEquityeForm(forms.ModelForm):
    class Meta:
        model = OwnerEquity
        fields = ['capital']

class ItemForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                     widget=forms.Select(attrs={"hx-get": "load_items/", "hx-target": "#id_item"}))
    item = forms.ModelChoiceField(queryset=Itemsmodel.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.data:
            category_id = int(self.data.get("category"))
            self.fields["item"].queryset = Itemsmodel.objects.filter(category_id=category_id)