import json
import uuid

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *



# Create your views here.
def store(request):
    if request.user.is_authenticated:
        """ For Authenticated Users. """

        customer = request.user.customer

        """Create or Get order items if present then fetch only those items whose complete status is false"""

        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        """ For Unauthenticated Users. """

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0} 
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems':cartItems
    }
    return render(request, 'store/store.html', context=context)

def details(request, pk):
    product = Product.objects.get(id=pk)
    context = {
        'product': product
    }
    return render(request, 'store/details.html', context=context)

def cart(request):
    if request.user.is_authenticated:
        """ For Authenticated Users. """
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        """ For Unauthenticated Users. """

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']


    context = {'items':items, 'order': order,
        'cartItems':cartItems
    }
    return render(request, 'store/cart.html', context=context)

def checkout(request):
    if request.user.is_authenticated:
        """ For Authenticated Users. """
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        """ For Unauthenticated Users. """

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0} 
        cartItems = order['get_cart_items']

    context = {'items':items, 'order': order, 
        'cartItems':cartItems}
    return render(request, 'store/checkout.html', context=context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        if orderItem.quantity is None:
            orderItem.quantity = 0
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@csrf_exempt
def processOrder(request):
    transaction_id = uuid.uuid4()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(request.POST.get('total'))
        order.transaction_id = transaction_id
        print("Price from frontend: ", total)
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        if order.shipping == True:
            print("hello")
            ShippingAddress.objects.create(
                customer = customer, order = order, address = request.POST.get('address'), city = request.POST.get('city'),\
                    state = request.POST.get('state'), zipcode = request.POST.get('zipcode')
            )
    else:
        print("user is not logged in...")
    return JsonResponse('Order is processing...', safe = False)