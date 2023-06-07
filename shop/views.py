import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from math import ceil
from django.shortcuts import render, redirect
from django.db import IntegrityError
from .forms import CustomUserCreationForm
from .models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import paytmchecksum
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

#MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'


def home(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        cartItems = ""
        wishlistItems = ""

    rate = requests.get("https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
    if request.method == 'GET':
        currency = request.GET.get('curr', 'INR')
        Rate = rate['conversion_rates'][currency]

    allprods = []
    allcats = {'Cotton', 'Best-Sellers'}
    for cat in allcats:
        prod = Product.objects.filter(subcategory=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        if n == 0:
            continue
        allprods.append([prod, range(1, nslides), nslides])

    params = {'allprods': allprods, 'cartItems': cartItems, 'rate': Rate, 'currency': currency,
              'wishlistItems': wishlistItems}
    return render(request, 'home.html', params)


def SearchMatch(query, item):
    """Return True only when query match item name or catgory or desc"""
    if query in item.desc.lower() \
            or query in item.product_name.lower() \
            or query in item.category.lower() \
            or query in item.subcategory.lower() \
            or query in item.label.lower():
        return True
    else:
        return False


def search(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        cartItems = ""
        wishlistItems = ""

    rate = requests.get("https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
    if request.method == 'GET':
        currency = request.GET.get('curr', 'INR')
        Rate = rate['conversion_rates'][currency]

    query = request.GET.get('search')
    query = query.lower()
    allcats = {i['category'] for i in Product.objects.values('category')}
    allprods = []
    for cat in allcats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if SearchMatch(query, item)]
        if len(prod) != 0:
            allprods.append(prod)
    print(allprods)
    params = {'products': allprods, 'msg': "", 'query': query, 'cartItems': cartItems, 'rate': Rate,
              'currency': currency, 'wishlistItems': wishlistItems}
    if len(allprods) == 0:
        print("hii")
        params = {'products': [], 'msg': "No Product Found", 'query': query, 'cartItems': cartItems, 'rate': Rate,
                  'currency': currency, 'wishlistItems': wishlistItems}
    return render(request, 'search.html', params)


def signup_user(request):
    if request.method == 'POST':
        url = "https://api.zerobounce.net/v2/validate"
        api_key = "3bf08a0f82304a05aa1bf7d6b9a318ee"
        email = request.POST.get('email')
        ip_address = ""  # ip_address can be blank

        params = {"email": email, "api_key": api_key, "ip_address": ip_address}

        response = requests.get(url, params=params)

        # Print the returned json
        response = json.loads(response.content)
        if response['status'] == 'valid':
            if request.POST.get('password1') == request.POST.get('password2'):
                try:
                    user = User.objects.create_user(
                        username=request.POST.get('username'),
                        password=request.POST.get('password1'),
                        email=request.POST.get('email')
                    )
                    user.save()
                    login(request, user)
                    return redirect('/shop/')
                except IntegrityError:
                    return render(request, 'signup_user.html', {'form': CustomUserCreationForm(),
                                                                'error': 'That username has already been taken. '
                                                                         'Please choose a new username'})
            else:
                return render(request, 'signup_user.html',
                              {'form': CustomUserCreationForm(), 'error': 'Passwords did not match'})
        else:
            return render(request, 'signup_user.html',
                          {'form': CustomUserCreationForm(), 'error': 'Enter Valid Email'})
    return render(request, 'signup_user.html', {'form': CustomUserCreationForm()})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            return render(request, 'login_user.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password did not match'})
        else:
            login(request, user)
            return redirect('/shop/')

    return render(request, 'login_user.html', {'form': AuthenticationForm()})


def category_view(request, mycategory):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        cartItems = ""
        wishlistItems = ""

    rate = requests.get(" https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
    if request.method == 'GET':
        currency = request.GET.get('curr', 'INR')
        Rate = rate['conversion_rates'][currency]

    categories = {i['category'] for i in Product.objects.values('category')}
    subcategories = {i['subcategory'] for i in Product.objects.values('subcategory')}
    labels = {i['label'] for i in Product.objects.values('label')}
    if mycategory in subcategories:
        product = Product.objects.filter(subcategory=mycategory)
    elif mycategory in categories:
        product = Product.objects.filter(category=mycategory)
    else:
        product = Product.objects.filter(label=mycategory)
    return render(request, 'categoryview.html',
                  {'products': product, "category": mycategory, 'cartItems': cartItems, 'rate': Rate,
                   'currency': currency, 'wishlistItems': wishlistItems})


def productview(request, mycategory, myid):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        cartItems = ""
        wishlistItems = ""

    rate = requests.get(" https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
    if request.method == 'GET':
        currency = request.GET.get('curr', 'INR')
        Rate = rate['conversion_rates'][currency]

    product = Product.objects.filter(id=myid)
    return render(request, 'productview.html',
                  {'product': product[0], 'cartItems': cartItems, 'rate': Rate, 'currency': currency,
                   'wishlistItems': wishlistItems})


def about(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        cartItems = ""
        wishlistItems = ""

    return render(request, 'about.html', {'cartItems': cartItems, 'wishlistItems': wishlistItems})


@login_required
def logout_user(request):
    logout(request)
    return redirect('/shop/')


def Cart(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        return redirect("/shop/login/")

    rate = requests.get(" https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
    if request.method == 'GET':
        currency = request.GET.get('curr', 'INR')
        Rate = rate['conversion_rates'][currency]

    content = {'items': items, 'order': order, 'cartItems': cartItems, 'rate': Rate, 'currency': currency,
               'wishlistItems': wishlistItems}
    return render(request, 'cart.html', content)


def Wishlist(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.wishlistitem_set.all()
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items
    else:
        return redirect("/shop/login/")

    rate = requests.get("https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
    if request.method == 'GET':
        currency = request.GET.get('curr', 'INR')
        Rate = rate['conversion_rates'][currency]

    content = {'items': items, 'order': order, 'cartItems': cartItems, 'rate': Rate, 'currency': currency,
               'wishlistItems': wishlistItems}
    return render(request, 'wishlist.html', content)


def Checkout(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        wishlistItems = order.get_wishlist_items

        rate = requests.get("https://v6.exchangerate-api.com/v6/e5bfffef0ac7a709699bf03c/latest/INR").json()
        if request.method == 'GET':
            currency = request.GET.get('curr', 'INR')
            Rate = rate['conversion_rates'][currency]
        elif request.method == "POST":
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zipcode = request.POST.get('zipcode', '')
            shippingOrder = ShippingAddress(user=user, order=order, address=address, city=city, state=state,
                                            zipcode=zipcode)
            shippingOrder.save()

            param_dict = {
                'MID': 'WorldP64425474807247',
                'ORDER_ID': str(order.id),
                'TXN_AMOUNT': str(order.get_cart_total),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': "WEBSTAGING",
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
            }
            param_dict['CHECKSUMHASH'] = paytmchecksum.generateSignature(param_dict, MERCHANT_KEY)
            return render(request, 'paytm.html', {'param_dict': param_dict})

    else:
        return redirect("/shop/login/")

    content = {'items': items, 'order': order, 'cartItems': cartItems, 'currency': 'INR',
               'wishlistItems': wishlistItems, 'rate': Rate, 'currency': currency}
    return render(request, 'checkout.html', content)


def updateCart(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    size = data['size']
    color = data['color']
    qty = data['qty']
    qty = int(qty) - 1

    user = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=user, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, size=size, color=color)
    print("hii")
    if action == "add":
        orderItem.quantity = (orderItem.quantity + 1) + qty
    elif action == "remove":
        orderItem.quantity = (orderItem.quantity - 1) + qty

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was Added", safe=False)


def updateWishlist(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    size = data['size']
    color = data['color']
    qty = data['qty']
    qty = qty - 1

    user = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=user, complete=False)

    wishlistItem, created = WishlistItem.objects.get_or_create(order=order, product=product, size=size, color=color)
    print("hii")
    if action == "add":
        wishlistItem.quantity = (wishlistItem.quantity + 1) + qty
    elif action == "remove":
        wishlistItem.quantity = (wishlistItem.quantity - 1) + qty

    wishlistItem.save()

    if wishlistItem.quantity <= 0:
        wishlistItem.delete()

    return JsonResponse("Item was Added", safe=False)


@csrf_exempt
def handlerequest(request):
    # Paytm send post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = paytmchecksum.verifySignature(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print("Order Successful")
            user = request.user
            order, created = Order.objects.get_or_create(user=user, complete=False)
            items = order.orderitem_set.all()
            transaction_id = datetime.datetime.now().timestamp()
            order.transaction_id = transaction_id
            order.complete = True
            order.save()
            tamplate = render_to_string('email_template.html',
                                        {'name': user.username, 'id': order.id, 'product': items})
            email = EmailMessage(
                'Your Order has been placed successfully,Thank you!',
                tamplate,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
        else:
            print("Order was not successful because " + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})
