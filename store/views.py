from django.http import request
from store.forms import UserForm
from django.shortcuts import render,redirect
from .models import *
from . import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Customer




# Create your views here.

def store(request):
    products=Product.objects.all()
    content ={'product':products}
    return render(request,'store.html',content)

@login_required(login_url='login')
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer

        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
    else:
        items=[]
        order={"get_cart_total":0,"get_cart_items":0}

    content={'items':items,'order':order}
    return render(request,'cart.html',content)

def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
    else:
        items=[]
        order={"get_cart_total":0,"get_cart_items":0}

    content={'items':items,'order':order}
    return render(request,'checkout.html',content)

def register(request):                                             
    form=UserForm()
    if request.method == 'POST':
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
            user=form.cleaned_data.get('username')
            messages.success(request,'You Have Successely Registered : ' +  user)
            return redirect("login")
       
    content={'form':form}
    return render(request,'register.html',content)

def login_id(request):

    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request,"User Is Not Created ")

    content={}
    return render(request,'login.html',content)




def logout_id(request):
    logout(request)
    return redirect("/")
            
 
def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)