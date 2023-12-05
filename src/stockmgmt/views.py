from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.http import HttpResponse,HttpResponseRedirect
import csv
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.db.utils import IntegrityError
from decimal import Decimal
from datetime import datetime
from django.template import RequestContext
from .templatetags.cash_tags import get_total_cash
from django.http import JsonResponse
from django.forms import formset_factory
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate ,login,logout ,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm , PasswordChangeForm ,SetPasswordForm 
from .forms import SignUpForm, EditUserprofileForm , EditAdminprofileForm
from django.contrib.auth.models import User






@login_required
def home(request):
    if request.user.is_authenticated==True:
        title = 'Welcome: This is the Home Page'
        form = StockCreateForm()  # Create an instance of the form
        context = {
            "title": title,
            "form": form,  # Add the form to the context
        }
        return render(request, "home.html", context)
    else:
        return redirect('user_login')

def list_item(request):
    if request.user.is_authenticated==True:
    
        title = 'Stock List'
        form = StockSearchForm(request.POST or None)
        queryset = Stock.objects.all()
        
        context = {
            "title": title,
            "queryset": queryset,
            "form": form
        }
        
        if request.method == 'POST':
            if form.is_valid():
                category_name = form.cleaned_data.get('category')
                item_name = form.cleaned_data.get('item_name')
                
                if category_name:
                    queryset = queryset.filter(category__name__icontains=category_name)

                if item_name:
                    queryset = queryset.filter(item_name__name__icontains=item_name)
            if form['export_to_CSV'].value() == True:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
                writer = csv.writer(response)
                writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
                
                for stock in queryset:
                    writer.writerow([stock.category.name, stock.item_name, stock.quantity])
                
                return response

        context["form"] = form
        context["queryset"] = queryset

        return render(request, "list_item.html", context)
    else:
        return redirect('user_login')

def Add_itemTriger(request):
    if request.user.is_authenticated==True:
        context = {'form': StockCreateForm()}
        messages.success(request, 'Successfully Saved')
        return render(request, 'itemindex.html', context)
    else:
        return redirect('user_login')

def add_items(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = StockCreateForm(request.POST)
            if form.is_valid():
                item_name = form.cleaned_data['item_name']
                category = form.cleaned_data['category']
                account_payable = form.cleaned_data['account_payable']
                quantity = form.cleaned_data['quantity']  
                rate = form.cleaned_data['rate']
                # Check if the item with the same name, category, and rate already exists
                existing_item = Stock.objects.filter(item_name=item_name, category=category, rate=rate).first()
                if existing_item:
                    existing_item.quantity += quantity
                    existing_item.save()
                    # Update the cash by subtracting the account payable
                    cash = AddCash.objects.first()
                    total_value = quantity * rate  # Use existing_item, not instance
                    total_value -= account_payable
                    cash.cash -= total_value
                    cash.save()
                    # Create an action history entry for the stock addition
                    action_message = f'Quantity added to existing item: {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        cash=existing_item,
                    )
                    action_history.save()
                else:
                
                    # If the item doesn't exist, create a new batch number
                    existing_items_same_name_category = Stock.objects.filter(item_name=item_name, category=category)
                    if existing_items_same_name_category.exists():
                        # If items with the same name and category exist, get the highest batch number and increment
                        highest_batch = existing_items_same_name_category.order_by('-batch_number').first().batch_number
                        if highest_batch.startswith('B-'):
                            batch_number_prefix = 'B-'
                            batch_number_suffix = int(highest_batch.split('-')[1]) + 1
                            batch_number = f'{batch_number_prefix}{batch_number_suffix:02d}'
                        else:
                            # If the batch number doesn't follow the expected pattern, set it to 'B-01'
                            batch_number = 'B-01'
                    else:
                        # If no items with the same name and category exist, set the batch number to 'B-01'
                        batch_number = 'B-01'
                    # Set the batch number in the form data
                    form.instance.batch_number = batch_number
                    # Save the form and get the instance
                    instance = form.save()
                    # Calculate the total value of the stock item added
                    total_value = instance.quantity * instance.rate
                    total_value -= instance.account_payable
                    
                    # Retrieve the cash entry
                    cash = AddCash.objects.first()  
                    cash.cash -= total_value 
                    cash.save()
                    action_message = f'Stock added {instance.item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        cash=instance,
                    )
                    action_history.save()

        else:
            form = StockCreateForm()

        context = {
            "form": form,
        }

        return render(request, "purchase_forms.html", context)
    else:
        return redirect('user_login')

def account_pay(request):
    if request.user.is_authenticated:
        account_payable_values = Stock.objects.all().values('id', 'account_payable', 'timestamp')
        stock_entries = Stock.objects.all()

        context = {
            'account_payable_values': account_payable_values,
            'stock_entries': stock_entries,
        }

        return render(request, "account_payable.html", context)
    else:
        return redirect('user_login')

def update_items(request, pk):
    if request.user.is_authenticated==True:
        queryset = Stock.objects.get(id=pk)
        form = StockUpdateForm(instance=queryset)
        if request.method == 'POST':
            form = StockUpdateForm(request.POST, instance=queryset)
            if form.is_valid():
                # Get the original stock instance
                original_stock = Stock.objects.get(id=pk)
                # Calculate the original total value
                original_total_value = original_stock.quantity * original_stock.rate
                # Update the stock with the new values
                updated_stock = form.save()
                # Calculate the updated total value
                updated_total_value = updated_stock.quantity * updated_stock.rate
                # Calculate the difference in total value
                total_value_difference = updated_total_value - original_total_value
                # Retrieve the cash entry
                cash = AddCash.objects.first()  # You may need to adapt this to your actual cash model
                # Update the cash by adding the difference in total value
                cash.cash -= total_value_difference
                cash.save()
                # Create an action history entry for the stock update
                action_message = f'Stock updated {updated_stock.item_name}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash=updated_stock,
                )
                action_history.save()
                messages.success(request, 'Successfully Updated')
                return redirect('/list_item')

        context = {
            'form': form
        }
        return render(request, 'update_items.html', context)
    else:
        return redirect('user_login')

def delete_items(request, pk):
    stock_instance = Stock.objects.get(id=pk)
    if request.method == 'POST':
        # Retrieve the cash entry
        cash = AddCash.objects.first()  # You may need to adapt this to your actual cash model
        # Calculate the total value of the stock item being deleted
        total_value = stock_instance.quantity * stock_instance.rate
        # Update the cash by adding back the total value
        cash.cash += total_value
        cash.save()
        # Create an action history entry for the stock deletion
        action_message = f'Stock deleted: {stock_instance.item_name}'
        action_history = ActionHistory(
            user=request.user,
            action_type=action_message,
            sale_cash=total_value,  # Assuming you have a field named sale_cash in your ActionHistory model
        )
        action_history.save()

        stock_instance.delete()  # Delete the stock item

        messages.success(request, 'Successfully Deleted')
        return redirect('/list_item')

    context = {
        'stock_instance': stock_instance,
    }
    return render(request, 'delete_items.html', context)

def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)

# def issue_items(request, pk):
# 	queryset = Stock.objects.get(id=pk)
# 	form = IssueForm(request.POST or None, instance=queryset)
# 	if form.is_valid():
# 		instance = form.save(commit=False)
# 		instance.quantity -= instance.issue_quantity
		
# 		messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in Store")
# 		instance.save()

# 		return redirect('/stock_detail/'+str(instance.id))
# 		# return HttpResponseRedirect(instance.get_absolute_url())

# 	context = {
# 		"title": 'Issue ' + str(queryset.item_name),
# 		"queryset": queryset,
# 		"form": form,
# 		"username": 'Issue By: ' + str(request.user),
# 	}
# 	return render(request, "add_items.html", context)

def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity += instance.receive_quantity
		instance.save()
		messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+"s now in Store")
		return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"title": 'Reaceive ' + str(queryset.item_name),
			"instance": queryset,
			"form": form,
			"username": 'Receive By: ' + str(request.user),
		}
	return render(request, "add_items.html", context)

def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    if request.method == 'POST':
        form = ReorderLevelForm(request.POST, instance=queryset)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, f"Reorder level for {instance.item_name} is updated to {instance.reorder_level}")
            return redirect("/list_item")
    else:
        form = ReorderLevelForm(instance=queryset)
    context = {
        "instance": queryset,
        "form": form,
    }
    return render(request, "reorder_level.html", context)

def add_itemcompany(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddItemCompanyForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addcompany')
        else:
            form = AddItemCompanyForm()

        add_companies = Company.objects.all()

        context = {
            'form': form,
            'add_companies': add_companies
        }

        return render(request, 'add_company.html', context)
    else:
        return redirect('user_login')

def Settings_app (request):
    return render(request, 'settings.html')

def add_vender(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddVenderForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addvender')  # Redirect to the same page after adding a vendor
        else:
            form = AddVenderForm()

        vendors = Vender.objects.all()  # Fetch the list of vendors from the database

        context = {
            'form': form,
            'vendors': vendors,  # Add the vendors list to the context
        }

        return render(request, 'add_vender.html', context)
    else:
        return redirect('user_login')

def add_ExpenseCategory(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = ExpenseCatForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addExpense')  # Redirect to the same page after adding a vendor
        else:
            form = ExpenseCatForm()

        ex = Expense.objects.all()  # Fetch the list of vendors from the database

        context = {
            'form': form,
            'ex': ex,  # Add the vendors list to the context
        }

        return render(request, 'add_ExpenseCategory.html', context)
    else:
        return redirect ('user_login')

def add_category(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddCategoryForm(request.POST)
            if form.is_valid():
                form.save()    
                return redirect('addcategory')  # Redirect to the same page after adding a vendor
        else:
            form = AddCategoryForm()

        category = Category.objects.all()  # Fetch the list of vendors from the database
        

        context = {
            'form': form,
            'category': category,
        }

        return render(request, 'add_category.html', context)
    else:
        return redirect ('user_login')

def add_CatItems(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddItemsform(request.POST)
            if form.is_valid():
                form.save()
                return redirect('add-items')  # Redirect to the same page after adding a vendor
        else:
            form = AddItemsform()

        Item = Itemsmodel.objects.all()  # Fetch the list of vendors from the database

        context = {
            'form': form,
            'Item': Item,  # Add the vendors list to the context
        }

        return render(request, 'add_item_name.html', context)
    else:
        return redirect ('user_login')



def sale_l(request):
    if request.user.is_authenticated==True:
        context = {'form': SaleForm()}
        return render(request, 'index.html', context)
    else:
        return redirect ('user_login')

def create_form(request): #this is make_sale function
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = SaleForm(request.POST)
            batchform = BatchForm(request.POST)
            if form.is_valid():
                stock = form.cleaned_data['stock']
                sale_quantity = form.cleaned_data['sale_quantity']
                rate = form.cleaned_data['rate']
                item_name = stock.item_name
                total_amount = sale_quantity * rate
                if sale_quantity <= stock.quantity:
                    stock.quantity -= sale_quantity
                    stock.save()  # Update the stock quantity
                    sale = form.save()
                    timestamp = datetime.now()
                    # Create an action history entry for the main sale
                    action_type = f'Sale Made - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_type,
                        sale_cash=sale_quantity * rate,
                        timestamp=timestamp
                    )
                    action_history.save()

                    # Update the cash by subtracting the main sale amount
                    cash = AddCash.objects.first()  # Get the cash entry (you may need to adapt this part)
                    cash.cash += total_amount
                    cash.cash -= sale.account_recieveable  # Use the sale's account_recieveable field
                    cash.save()

                    cogs_model_instance = COGSModel.objects.first()
                    cogs_model_instance.cogs_sum += sale_quantity * stock.rate
                    cogs_model_instance.save()

                else:
                    messages.error(request, f"INSUFFICIENT STOCK! {stock.item_name}")
            else:
                messages.error(request, "Form is not valid")

        else:
            form = SaleForm()

        return render(request, 'forms.html', {'form': form})
    else:
        return redirect ('user_login')

def account_receiveable(request):
    account_recieveable_values = Sale.objects.all().values('id', 'account_recieveable', 'Date_time','received_by')

    context = {
        'account_recieveable_values': account_recieveable_values,
    }

    return render(request, "account_recieveable.html", context)


def calculate_total_cash():
    total_cash = AddCash.objects.aggregate(Sum('cash'))['cash__sum'] or 0
    return total_cash

def log_action(request, action_type, item_name=None):
    if request.user.is_authenticated:
        if item_name:
            action_type_with_item = f'{action_type} - {item_name}'
        else:
            action_type_with_item = action_type
        ActionHistory.objects.create(user=request.user, action_type=action_type_with_item)

def action_history(request):
    if request.user.is_authenticated==True:
        total_cash = calculate_total_cash()
        history_entries = ActionHistory.objects.all().order_by('-timestamp')
        total_value = 0
        for entry in history_entries:
            if entry.cash:
                entry.total_value = entry.cash.quantity * entry.cash.rate
                entry.remaining_amount = entry.total_value - total_cash
            else:
                entry.total_value = 0
                entry.remaining_amount = 0

            entry.save()

        context = {
            'history_entries': history_entries,
            'form': AddCashForm(),
            'total_cash': total_cash,
            'total_value': total_value
        }

        return render(request, 'action_history.html', context)
    else:
        return redirect ('user_login')

def add_cash(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddCashForm(request.POST)
            if form.is_valid():
                cash_amount = form.cleaned_data['cash']
                # Save the new cash record to the database
                AddCash.objects.create(cash=cash_amount)
                action_message = f'Cash added- {cash_amount}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash_hand=cash_amount,
                )
                action_history.save()
                return redirect('action_history')

        else:
            form = AddCashForm()

        # Calculate the total cash by summing up the 'cash' field in the AddCash model
        total_cash = AddCash.objects.aggregate(Sum('cash'))['cash__sum']

        # Query all the cash records from the database to display them on the page.
        cash_records = AddCash.objects.all()
        

        return render(request, 'your_template.html', {'form': form, 'cash_records': cash_records, 'total_cash': total_cash})
    else:
        return redirect ('user_login')

def defective_item_list(request):
    if request.user.is_authenticated==True:
    
        defective_items = DefectiveItem.objects.all()

        title= 'Defective Items List'
        context = {
            'title':title,
            'defective_items': defective_items,

        }

        return render(request, 'defective_items.html', context)
    else:
        return redirect ('user_login')

def replacement_item(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
            form1 = ReplacementForm(request.POST)
            
            if form.is_valid() and form1.is_valid():
                batch_number = form.cleaned_data['batch_number']
                category = form.cleaned_data['category']
                item_name = form.cleaned_data['item_name']
                price = form.cleaned_data['price']
                quantity = form.cleaned_data['quantity']
                action = form.cleaned_data['action']
                # Access cleaned data from ReplacementForm
                
                stock_item, created = Stock.objects.get_or_create(batch_number=batch_number, category=category, item_name=item_name)
                if quantity > stock_item.quantity:
                    messages.error(request, 'Insufficient stock quantity!')
                    
                else:
                    stock_item.quantity -= quantity
                    total_cash = AddCash.objects.first()
                    if hasattr(total_cash, 'cash'):
                        total_cash.cash += price
                        total_cash.save() 

                    # Update profit in the ActionHistory model
                    action_message = f'Sale Return - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        sale_cash=+sub_cash, 
                        timestamp=datetime.now()
                    )
                    action_history.save()

                    stock_item.save()
                    title = 'Replacement'
                    context = {
                        'title': title,
                        'form1': form1,
                        'total_cash': calculate_total_cash(),
                    }

                    return render(request, 'replacement_item.html', context)

        else:
            category = None
            item_name = None
            price = None
            quantity = None
            action = None

            form = SalesReturnForm()
            form1 = ReplacementForm()

            title = 'Replacement'
            context = {
                'title': title,
                'form1': form1,
                'total_cash': calculate_total_cash(),
            }

            return render(request, 'replacement_item.html', context)

        return render(request, 'replacement_item.html', {'form': form, 'form1': form1})
    else:
        return redirect ('user_login')


def stock_return(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = StockReturnForm(request.POST)
            if form.is_valid():
                stock = form.cleaned_data['stock']
                return_quantity = form.cleaned_data['return_quantity']

                # Check if there is enough stock to return
                if stock.quantity < return_quantity:
                    return render(request, 'stock_return.html', {'form': form, 'error_message': 'Not enough stock to return.'})

                # Create a StockReturn entry
                stock_return_entry = StockReturn.objects.create(stock=stock, return_quantity=return_quantity)

                # Update the stock quantity
                stock.quantity -= return_quantity
                stock.save()

                # Calculate the total value returned
                total_value_returned = stock_return_entry.return_quantity * stock.rate  # Adjust this based on your model

                # Adjust the cash
                cash_entry = AddCash.objects.first()

                if cash_entry:
                    cash_entry.cash += total_value_returned
                    cash_entry.save()

                # Add a success message
            messages.success(request, 'Stock returned successfully!')

        else:
            form = StockReturnForm()

        return render(request, 'stock_return.html', {'form': form})
    else:
        return redirect('user_login') 

def purchase_returns_records(request):
    purchase_returns = StockReturn.objects.all()
    for purchase_return in purchase_returns:
        purchase_return.total_value_returned = purchase_return.stock.rate * purchase_return.return_quantity

    context = {
        'purchase_returns': purchase_returns,
    }

    return render(request, 'purchase_returns_records.html', context)

def sales_return_list(request):
    if request.user.is_authenticated:
        sales_data = Sale.objects.all()

        context = {
            'sales_data': sales_data,
        }

        return render(request, 'sales_return_list.html', context)
    else:
        return redirect('user_login')


def purchase_record_list(request):
    purchase_data = Stock.objects.all()
    return render(request, 'purchase_record_list.html', {'purchase_data': purchase_data})

def sales_record_list(request):
    sales_data = Sale.objects.all()

    context = {
        'sales_data': sales_data,
    }

    return render(request, 'sales_record_list.html', context)

def add_expense(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddExpenseForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                form.save()

                total_cash = AddCash.objects.first()
                total_cash.cash -= amount  # Subtract the amount from the cash attribute
                total_cash.save()
                return redirect('expenses_list')
        

        else:
            form = AddExpenseForm()

        return render(request, 'add_expense.html', {'form': form})
    else:
        return redirect ('user_login')

def expenses_list(request):
    if request.user.is_authenticated==True:
        expenses = Expenses.objects.all()
        return render(request, 'expenses_list.html', {'expenses': expenses})
    else:
        return redirect('user_login')

def total_sales (request):
    total_sales = ActionHistory.objects.aggregate(Sum('sale_cash'))['sale_cash__sum'] or 0
    return total_sales

def total_cogs (request):
    total_values_sum = sum(item['total_values'] for item in total_values_list)
    
    return total_values_sum


def CostofGoods(request):
    if request.user.is_authenticated==True:
    
        total_values_list = []

        # Assuming you have a Sale model with a ForeignKey to Stock
        sales = Sale.objects.all()

        for sale in sales:
            stock = sale.stock
            total_values = sale.sale_quantity * stock.rate
            total_values_list.append({
                'sale_datetime': sale.Date_time,  # Use the Date_time field for sale datetime
                'category': stock.category,
                'item_name': stock.item_name,
                'sale_quantity': sale.sale_quantity,
                'stock_rate': stock.rate,
                'total_values': total_values,
            })

        # Calculate the total values sum using a separate function
        # total_values_sum = sum(item['total_values'] for item in total_values_list)
        # request.session['total_values_sum'] = total_values_sum

        context = {
            'total_values_list': total_values_list,
            # 'total_values_sum': total_values_sum,
        }

        return render(request, 'CostofGoods.html', context)
    else:
        return redirect('user_login')

def calculate_sum_Expense():
    total_expense = Expenses.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    return total_expense


def sales_return(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
            if form.is_valid():
                batch_number = form.cleaned_data['batch_number']
                category = form.cleaned_data['category']
                item_name = form.cleaned_data['item_name']
                price = form.cleaned_data['price']
                quantity = form.cleaned_data['quantity']
                action = form.cleaned_data['action']

                if action == 'defective':
                    defective_item = DefectiveItem(
                        batch_number=batch_number,
                        category=category,
                        item_name=item_name,
                        price=price,
                        quantity=quantity
                    )
                    defective_item.save()

                    total_cash = AddCash.objects.first()
                    if hasattr(total_cash, 'cash'):
                        total_cash.cash -= price * quantity
                        total_cash.save()

                    return redirect('/list_item')

                # elif action=='replace':
                #     # Store the item in the database without subtracting from AddCash
                #     total_values_list = []
                #     stock_item, created = Stock.objects.get_or_create(batch_number=batch_number,category=category, item_name=item_name)
                #     stock_item.quantity += quantity
                #     stock_item.save()
                #     total_cash = AddCash.objects.first()
                #     if hasattr(total_cash, 'cash'):
                #         total_cash.cash -= price * quantity
                #         total_cash.save()
                    
                #     # Calculate the total sales by calling the total_sales function
                #     total_sales_value = total_sales(request)    
                #     sales = Sale.objects.all()
                #     for sale in sales:
                #         stock = sale.stock
                #         total_values = sale.sale_quantity * stock.rate
                #         total_values_list.append({
                #             'total_values': total_values,
                #         })
                        
                #     total_expense= calculate_sum_Expense()        
                #     COGS_sum = sum(sum(dictionary.values()) for dictionary in total_values_list)
                #     GrossP = total_sales_value - COGS_sum
                #     Net_Profit=GrossP-total_expense
                #     total_sales_value = total_sales(request) 
                    
                #     print('COGS',total_sales_value - price )
                #     print('COGS',COGS_sum )
                #     print('COGS',GrossP )
                #     print('COGS',Net_Profit)

                #     #ye hehehjee
                #     branch_id = request.POST.get('sale_cash')
                #     branch_instance = ActionHistory.objects.get(pk=branch_id)
                #     branch_instance.delete()
                    
                #     # return redirect('Replace_sale')
                #     return redirect('make_sale')
                    
                    

                else:
                    total_cash = AddCash.objects.first()
                    if hasattr(total_cash, 'cash'):
                        total_cash.cash -= price * quantity
                        
                        total_cash.save()

                    # Add quantity to the related database
                    stock_item, created = Stock.objects.get_or_create(batch_number=batch_number, category=category, item_name=item_name)
                    stock_item.quantity += quantity
                    stock_item.save()
                    # Calculate the return amount
                    cogs_model_instance = COGSModel.objects.first()
                    if cogs_model_instance is None:
                        cogs_model_instance = COGSModel.objects.create(cogs_sum=0)

                    cogs_model_instance.cogs_sum -= stock_item.rate * quantity
                    cogs_model_instance.save()

                    return_amount = price * quantity
                    action_message = f'Sale Return - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        sale_cash = -return_amount,  # Use negative return_amount to deduct from profit
                        timestamp=datetime.now()
                    )
                    action_history.save()


                    

                return redirect('/list_item')

        else:
            form = SalesReturnForm()

        context = {
        'form': form,
        

    }

        return render(request, 'sales_return.html', context)
    else:
        return redirect ('user_login')


def Profit(request):
    if request.user.is_authenticated:
        total_values = 0
        # Calculate the total sales by calling the total_sales function
        total_sales_value = total_sales(request)    
        sales = Sale.objects.all()
        for sale in sales:
            stock = sale.stock
            # Add the value of each sale to total_values
            total_values += sale.sale_quantity * stock.rate
        
        total_expense = calculate_sum_Expense()
        cogs_model_instance, created = COGSModel.objects.get_or_create(defaults={'cogs_sum': 0})
        # Calculate COGS_sum based on the current value in cogs_model_instance
        total_values = cogs_model_instance.cogs_sum

        # Calculate other financial metrics
        GrossP = total_sales_value - total_values
        Net_Profit = GrossP - total_expense
        
        context = {
            "COGS_sum":total_values,
            "total_sales_value":total_sales_value,
            'GrossP':GrossP,
            'total_expense': total_expense,
            'Net_Profit': Net_Profit,
        }
        
        return render(request, 'Profit_loss.html', context)
    else:
        return redirect ('user_login')
    # else:
    #     return redirect ('user_login')
    #     GrossP = total_sales_value - COGS_sum
    #     Net_Profit=GrossP-total_expense
        
        
    #     context = {
    #         "COGS_sum":COGS_sum,
    #         "total_sales_value":total_sales_value,
    #         'GrossP':GrossP,
    #         'total_expense': total_expense,
    #         'Net_Profit': Net_Profit,
        
            
    #     }
        
    #     return render(request, 'Profit_loss.html', context)






@require_GET
def get_categories(request):
    batch_number = request.POST.get('batch_number')
    categories = YourModel.objects.filter(batch_number=batch_number).values_list('category', flat=True).distinct()
    return JsonResponse({'categories': list(categories)})

def sign_up(request):
    if request.method =="POST":

        fm = SignUpForm(request.POST)
        if fm.is_valid():
            messages.success(request,"Account created successfully::")
            fm.save()
            return HttpResponseRedirect("/signup/")
    else:
        fm = SignUpForm()

    context={
        "form":fm
    }
    return render(request, 'signin/signup.html', context)

def user_login(request):
    if not request.user.is_authenticated:
        if request.method =="POST":
            fm = AuthenticationForm(request=request,data = request.POST)
            if fm.is_valid():
                user_name = fm.cleaned_data['username']
                user_password = fm.cleaned_data['password']
                user = authenticate(username=user_name,password=user_password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect("/home")

        else:
            fm = AuthenticationForm()
        context={
            "form":fm
            }
        return render(request, 'signin/userlogin.html', context)
    else:
        return HttpResponseRedirect("/home")
    

def user_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.user.is_superuser == True:
                fm =EditAdminprofileForm(request.POST , instance = request.user)
                users = User.objects.all()
            else:
                fm =EditUserprofileForm(request.POST , instance = request.user)
                users = None
            if fm.is_valid():
                messages.success(request, "profile successfully updated !!!")
                fm.save()
        else:
            if request.user.is_superuser == True:
                fm = EditAdminprofileForm(instance = request.user)
                users = User.objects.all()
            else:
                fm = EditUserprofileForm(instance = request.user)
                users = None
            # fm =EditUserprofileForm(instance = request.user)
        context={
            "name": request.user.username,
            "form":fm,
            "users":users
        }
        return render(request, "signin/profile.html", context)
    else:
        return HttpResponseRedirect("/login/")

def user_logout(request):
    logout(request)
    return redirect("user_login")

def user_change_password(request):
    # password2 = forms.CharField(label="Confirm password (again) ",widget= forms.PasswordInput)
    if request.user.is_authenticated:
        if request.method == "POST":
            fm =PasswordChangeForm(user = request.user , data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request , fm.user)
                messages.success(request,"Passwaor changed successfully::")
                return HttpResponseRedirect("/profile/")
        else:
            fm =PasswordChangeForm(user = request.user)
        context= {
            "form":fm
        }
        return render (request, "signin/changepassword.html", context)
    else:
        return HttpResponseRedirect("/login/")

def user_detail(request , id):
    
    if request.user.is_authenticated:
        pi  = User.objects.get(pk=id)
        fm = EditAdminprofileForm(instance = pi)
        context = {
            "form":fm
        }
        
        return render(request , "signin/userdetail.html",context)
    else:
        return HttpResponseRedirect("/login/")


def Replace_l(request):
    if request.user.is_authenticated==True:
        context = {'form': ReplacementSaleForm()}
        return render(request, 'indexsale.html', context)
    else:
        return redirect ('user_login')

def Replace_create_form(request): 
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = ReplacementSaleForm(request.POST)
            batchform = BatchForm(request.POST)
            if form.is_valid():
                stock = form.cleaned_data['stock']
                sale_quantity = form.cleaned_data['sale_quantity']
                rate = form.cleaned_data['rate']
                cash_adjust = form.cleaned_data['cash_adjust']
                item_name = stock.item_name
                # total_amount = sale_quantity * rate
                if sale_quantity <= stock.quantity:
                    stock.quantity -= sale_quantity
                    stock.save()  # Update the stock quantity
                    sale = form.save()
                    timestamp = datetime.now()
                    # total = request.session.get('total_values_sum', 0) + cash_adjust
                    # Create an action history entry for the main sale
                    amount = sale_quantity*rate
                    print('Rate:', rate)
                    amount -= cash_adjust
                    total = request.session['COGS_sum'] - amount
                    print('Total COGS', total)
                    # totatl.save()

                    print('Cash adjust:', sale_quantity)
                    print('The amount:', amount)
                    action_type = f'Replace Made - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_type,
                        sale_cash=amount,
                        timestamp=timestamp
                    )
                    action_history.save()

                    # Update the cash by subtracting the main sale amount
                    cash = AddCash.objects.first()  # Get the cash entry (you may need to adapt this part)
                    cash.cash += amount
                    cash.cash -= sale.account_recieveable  # Use the sale's account_recieveable field
                    cash.save()
                else:
                    messages.error(request, f"INSUFFICIENT STOCK! {stock.item_name}")
            else:
                messages.error(request, "Form is not valid")

        else:
            form = ReplacementSaleForm()

        return render(request, 'formsSale.html', {'form': form})
    else:
        return redirect ('user_login')


def get_items(request):
    category_id = request.GET.get('category_id')
    items = Itemsmodel.objects.filter(category_id=category_id).values()
    item_list = list(items)
    return JsonResponse(item_list, safe=False)


def delete_sale(request, sale_id):
    qoute = get_object_or_404(ActionHistory, pk=sale_id)
    if request.method == 'POST':
        qoute.delete()
        return redirect('action_history')
    context = {
        'qoute': qoute,
    }
    return render(request, 'action_history.html', context)

def add_Equity(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = OwnerEquityeForm(request.POST)  # Corrected the form name
            if form.is_valid():
                capital_amount = form.cleaned_data['capital']
                # Save the new equity record to the database
                OwnerEquity.objects.create(capital=capital_amount)
                
                # Add the equity amount to the cash
                AddCash.objects.create(cash=capital_amount)
                action_message = f'Owner Equity- {capital_amount}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash_hand=capital_amount,
                )
                action_history.save()
        else:
            form = OwnerEquityeForm()

        # Calculate the total equity by summing up the 'capital' field in the OwnerEquity model
        total_equity = OwnerEquity.objects.aggregate(Sum('capital'))['capital__sum']

        # Query all the equity records from the database to display them on the page.
        equity_records = OwnerEquity.objects.all()

        return render(request, 'OwnerEquity.html', {'form': form, 'equity_records': equity_records, 'total_equity': total_equity})
    else:
        return redirect('user_login')

def balance_sheet(request):
    total_values = 0
    sales = Sale.objects.all()

    for sale in sales:
        stock = sale.stock
        # Add the value of each sale to total_values
        total_values += sale.sale_quantity * stock.rate

    total_expense = calculate_sum_Expense()
    cogs_model_instance = COGSModel.objects.first() 
    # Calculate COGS_sum based on the current value in cogs_model_instance
    if cogs_model_instance is not None:
        total_values = cogs_model_instance.cogs_sum
    else:
        # Handle the case when there is no COGSModel instance
        total_values = 0 
        


    total_equity = OwnerEquity.objects.aggregate(Sum('capital'))['capital__sum']
    total_Stock = sum(stock.subtotal for stock in Stock.objects.all())
    total_accountRecievable = Sale.objects.aggregate(Sum('account_recieveable'))['account_recieveable__sum']
    total_accountPayable = Stock.objects.aggregate(Sum('account_payable'))['account_payable__sum']
    cash_in_hand = AddCash.objects.aggregate(Sum('cash'))['cash__sum']
    Total_sales = ActionHistory.objects.aggregate(Sum('sale_cash'))['sale_cash__sum']

    print('Stock Before',total_Stock)
    for sale in sales:
            stock = sale.stock
            total_rates = sale.sale_quantity * stock.rate
            total_Stock+=total_rates
            print('Rate',total_rates)
        
    
    Profit = Total_sales - total_values 
    Net_Profit = Profit - total_expense
    print('Stock after',total_Stock)
    


    context = {
        'total_equity':total_equity,
        'total_Stock':total_Stock,
        'total_accountRecievable':total_accountRecievable,
        'total_accountPayable':total_accountPayable,
        'cash_in_hand':cash_in_hand,
        'Total_sales':Total_sales,
        
        'Net_Profit':Net_Profit,
        
    }

    return render(request, 'balance_sheet.html', context)




def index(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data["category"])
            print(form.cleaned_data["item"])
        else:
            print(form.errors)
    else:
        form = ItemForm()
    return render(request, 'indexxx.html', {"form": form})

def load_items(request):
    category_id = request.GET.get("category")
    items = Itemsmodel.objects.filter(category_id=category_id)
    return render(request, "item_options.html", {"items": items})


def add_stock(request):
    if request.method == 'POST':
        stock_form = StockForm(request.POST)
        if stock_form.is_valid():
            stock_form.save()
            return redirect('index')
    else:
        stock_form = StockForm()

    return render(request, 'add_stock.html', {'stock_form': stock_form})