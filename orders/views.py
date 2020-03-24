from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from cart.cart import Cart
from suds.client import Client
from django.http import HttpResponse


@login_required
def detail(request, order_id):
	order = get_object_or_404(Order, id=order_id)
	return render(request, 'orders/order.html', {'order':order})

@login_required
def order_create(request):
	cart = Cart(request)
	order = Order.objects.create(user=request.user)
	for item in cart:
		OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
		cart.clear()
	return redirect('orders:detail', order.id)


MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
description = "پرداخت مونگارد"
mobile = '09123456789'
CallbackURL = 'http://localhost:8000/orders/verify/'

@login_required
def payment(request, price):
	global amount
	amount = price
	result = client.service.PaymentRequest(MERCHANT, amount, description, request.user.email, mobile, CallbackURL)
	if result.Status == 100:
		return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
	else:
		return HttpResponse('Error code: ' + str(result.Status))

@login_required
def verify(request):
	if request.GET.get('Status') == 'OK':
		result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
		if result.Status == 100:
			return HttpResponse('Transaction success.')
		elif result.Status == 101:
			return HttpResponse('Transaction submitted')
		else:
			return HttpResponse('Transaction failed.')
	else:
		return HttpResponse('Transaction failed or canceled by user')