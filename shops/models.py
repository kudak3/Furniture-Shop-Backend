from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="shop")
    name = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='shop-logo/', blank=False)

    def __str__(self):
        return self.name

class Customer (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    avatar = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)

    def __str__(self):
        return self.user.get_full_name()

class Driver (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    avatar = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    location = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Furniture(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    short_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='furniture_images/', blank=False)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    COOKING = 1
    READY = 2
    ONTHEWAY = 3
    DELIVERED = 4

    STATUS_CHOICES = (
        (COOKING, "Cooking"),
        (READY, "Ready"),
        (ONTHEWAY, "On the way"),
        (DELIVERED, "Delivered"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, blank = True, null = True)
    address = models.CharField(max_length=500)
    total = models.IntegerField()
    status = models.IntegerField(default = 1, choices = STATUS_CHOICES)
    created_at = models.DateTimeField(default = timezone.now)
    picked_at = models.DateTimeField(blank = True, null = True)

    def __str__(self):
        return str(self.id)


class OrderDetails(models.Model):
    order = models.ForeignKey(Order, related_name='order_details', on_delete=models.CASCADE)
    furniture = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sub_total = models.IntegerField()

    def __str__(self):
        return str(self.id)
