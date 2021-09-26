import json

from django.utils import timezone
from oauth2_provider.models import AccessToken
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from shops.models import Shop, Furniture, Order, OrderDetails, Driver
from shops.serializers import ShopSerializer, FurnitureSerializer, OrderSerializer

##############
 # CUSTOMERS
##############

def customer_get_shops(request):
    shops = ShopSerializer(
        Shop.objects.all().order_by("id"),
        many = True,
        context = {"request" : request}
    ).data

    return JsonResponse({"shops": shops})


def customer_get_furnitures(request, shop_id):
    furnitures = FurnitureSerializer(
        Furniture.objects.filter(shop_id = shop_id).order_by("id"),
        many = True,
        context = {"request" : request}
    ).data

    return JsonResponse({"furnitures" : furnitures })

@csrf_exempt
def customer_add_order(request):
    """
        params:
            access_token
            shop_id
            address
            order_details (json format), example:
                [{"furniture_id": 1, "quantity": 2}, {"furniture_id": 2, "quantity": 3}]
            
            return: 
                {"status": success}

    """
    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"), 
        expires__gt = timezone.now())

    # Get Profile
    customer = access_token.user.customer

    # Check whether customer has any order that is not delivered
    if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
        return JsonResponse({"status" : "failed", "error" : "Your last order must be completed."})

    # Check Address
    if not request.POST["address"]:
        return JsonResponse({"status": "failed", "error": "Address is required."})

    # Get Order Details
    order_details = json.loads(request.POST["order_details"])

    order_total = 0

    for furniture in order_details:
        order_total += Furniture.objects.get(id = furniture["furniture_id"]).price * furniture["quantity"]
 
    if len(order_details) > 0:
        # Step 1 - Create an Order
        order = Order.objects.create(
            customer = customer,
            shop_id = request.POST["shop_id"],
            total = order_total,
            status = Order.COOKING,
            address = request.POST["address"]
        )

        # Step 2 - Create Order details
        for furniture in order_details:
            OrderDetails.objects.create(
                order = order,
                furniture_id = furniture["furniture_id"],
                quantity = furniture["quantity"],
                sub_total = Furniture.objects.get(id = furniture["furniture_id"]).price * furniture["quantity"]
        )

        return JsonResponse({"status": "success" })

def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), 
        expires__gt = timezone.now())

    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer = customer).last()).data    
    
    return JsonResponse({"order": order})

def customer_driver_location(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), 
        expires__gt = timezone.now())

    customer = access_token.user.customer

    # set driver's location related to this customer's current order.
    current_order = Order.objects.filter(customer = customer, status = Order.ONTHEWAY).last()
    location = current_order.driver.location

    return JsonResponse({"location": location})

 ##############
 # RESTAURANT
 ##############   

def shop_order_notification(request, last_request_time):
    notification = Order.objects.filter(shop = request.user.shop,
        create_at__gt = last_request_time).count()


    return JsonResponse({"notification" : notification})

##############
 # DRIVER
############## 

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status = Order.READY, driver = None).order_by("id"),
        many = True
    ).data

    return JsonResponse({"orders": orders})

@csrf_exempt
# POST params: access_token, order_id
def driver_pick_order(request):
    if request.method == "POST":
        # Get Token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"), 
        expires__gt = timezone.now())


        # Get Driver
        driver = access_token.user.driver

        # Check if driver can only pick up one order at the same time
        if Order.objects.filter(driver = driver).exclude(status = Order.ONTHEWAY):
            return JsonResponse({"status": "failed", "error": "You can only pick one order"})

        try:
            order = Order.objects.get(
                id = request.POST["order_id"],
                driver = None,
                status = Order.READY
            )

            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()
            
            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This order has been picked up by another"})    
    
    return JsonResponse({})

# Get params: access token
def driver_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), 
        expires__gt = timezone.now())

    driver = access_token.user.driver
    order = OrderSerializer(
        Order.objects.filter(driver = driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"order": order})

# POST params: access_token, order_id
@csrf_exempt
def driver_complete_order(request):
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"), 
        expires__gt = timezone.now())

    driver = access_token.user.driver

    order = Order.objects.get(id = request.POST["order_id"], driver = driver)
    order.status = Order.DELIVERED
    order.save()

    return JsonResponse({"status": "success"})

#GET params: access_token
def driver_get_revenue(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"), 
        expires__gt = timezone.now())

    driver = access_token.user.driver

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday() )]

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver = driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue[day.strftime("%a")]  = sum(order.total for order in orders) 


    return JsonResponse({"revenue": revenue})

#POST - params: access_token, "lat,lng"
@csrf_exempt
def driver_update_location(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"), 
            expires__gt = timezone.now())

        driver = access_token.user.driver

        # Set location string => database
        driver.location = request.POST["location"]
        driver.save()

        return JsonResponse({"status" : "success"})



