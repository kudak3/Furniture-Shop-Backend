from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from shops.forms import UserForm, ShopForm, UserFormForEdit, FurnitureForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Furniture, Order

# Create your views here.
def home(request):
    if not request.user.is_authenticated:
        return render(request, 'shop/login.html', {"message": None})

    return redirect(order)

@login_required
def account (request):
    user_form = UserFormForEdit(instance = request.user)
    shop_form = ShopForm(instance = request.user.shop)

    if request.method == "POST":
        user_form = UserFormForEdit(request.POST, instance = request.user)
        shop_form = ShopForm(request.POST, request.FILES, instance = request.user.shop)

        if user_form.is_valid() and shop_form.is_valid():
            user_form.save()
            shop_form.save()


    return render(request, 'shop/account.html', {
        "user_form": user_form,
        "shop_form": shop_form
    })

@login_required
def shop_furniture (request):
    furnitures = Furniture.objects.filter(shop = request.user.shop).order_by("id") 

    return render(request, 'shop/furniture.html', {"furnitures" : furnitures})

@login_required
def add_furniture (request):
    form = FurnitureForm()
    if request.method == "POST":
        form = FurnitureForm(request.POST, request.FILES)

        if form.is_valid():
            furniture = form.save(commit=False)
            furniture.shop = request.user.shop
            furniture.save()  
            return redirect(shop_furniture)

    return render(request, 'shop/add_furniture.html', {
        "form" : form
    })

@login_required
def edit_furniture (request, furniture_id):
    form = FurnitureForm(instance = Furniture.objects.get(id = furniture_id))

    if request.method == "POST":
        form = FurnitureForm(request.POST, request.FILES, instance = Furniture.objects.get(id = furniture_id))

        if form.is_valid():
            form.save()  
            return redirect(shop_furniture)

    return render(request, 'shop/edit_furniture.html', {
        "form" : form
    })

@login_required
def order (request):

    if request.method == "POST":
        order = Order.objects.get(id = request.POST["id"], shop = request.user.shop )

        if order.status == Order.COOKING:
            order.status = Order.READY
            order.save()


    orders = Order.objects.filter(shop = request.user.shop).order_by("-id")
    return render(request, 'shop/order.html', {
        "orders" : orders
    })

@login_required
def report (request):
    from datetime import datetime, timedelta

    revenue = []
    orders = []


    today = datetime.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday() )]

    for day in current_weekdays:
        delivered_orders = Order.objects.filter(
            shop = request.user.shop,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue.append(sum(order.total for order in delivered_orders))
        orders.append(delivered_orders.count())

    return render(request, 'shop/report.html', {
        "revenue": revenue,
        "orders" : orders
    })

def login_view(request):
    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, 'shop/login.html', {"message": "Invalid Credentials"})

def logout_view(request):
    logout(request)
    return render(request, 'shop/login.html', {"message": "Logged Out"})

def sign_up(request):
    user_form = UserForm()
    shop_form = ShopForm()

    if request.method == "POST":
        user_form  = UserForm(request.POST)
        shop_form = ShopForm(request.POST, request.FILES)

        if user_form.is_valid() and shop_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_shop = shop_form.save(commit=False)
            new_shop.user = new_user
            new_shop.save()

            login(request, authenticate(
                username = user_form.cleaned_data["username"],
                password = user_form.cleaned_data["password"]
            ))

            return redirect(home)

    return render(request, 'shop/sign_up.html', {
        "user_form": user_form,
        "shop_form": shop_form
    })



