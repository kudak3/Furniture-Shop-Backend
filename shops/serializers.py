from rest_framework import serializers

from shops.models import Shop, Furniture, Customer, Driver, Order, OrderDetails


class ShopSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, shop):
        request = self.context.get('request')
        logo_url = shop.logo.url
        return request.build_absolute_uri(logo_url)

    class Meta:
        model = Shop
        fields = ("id", "name", "phone", "address", "logo")

class FurnitureSerializer(serializers.ModelSerializer):

    def get_image(self, furniture):
        request = self.context.get('request')
        image_url = furniture.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Furniture
        fields = ("id", "name", "short_description", "image", "price") 

class OrderCustomerSerializer(serializers.ModelSerializer):
    name= serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")
 
class OrderDriverSerializer(serializers.ModelSerializer):
    name= serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Driver
        fields = ("id", "name", "avatar", "phone", "address")
 

class OrderShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ("id", "name", "phone", "address")
        
class OrderFurnitureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Furniture
        fields = ("id", "name", "price")

class OrderDetailSerializer(serializers.ModelSerializer):
    furniture = OrderFurnitureSerializer

    class Meta:
        model = OrderDetails
        fields = ("id", "furniture", "quantity", "sub_total")


class OrderSerializer(serializers.ModelSerializer):
    customer = OrderCustomerSerializer()
    driver = OrderDriverSerializer()
    shop = OrderShopSerializer()
    order_details = OrderDetailSerializer(many = True)
    status = serializers.ReadOnlyField(source = "get_status_display")

    class Meta:
        model = Order
        fields = ("id", "customer", "shop", "driver", "order_details", "total", "status", "address" )

         