from django.contrib import admin
from shops.models import Shop, Furniture, Customer, Driver, Order, OrderDetails

# Register your models here.
admin.site.register(Shop)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Furniture)
admin.site.register(Order)
admin.site.register(OrderDetails)