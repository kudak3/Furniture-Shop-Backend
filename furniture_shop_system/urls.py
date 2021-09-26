from django.contrib import admin
from django.urls import path, re_path, include
from shops import views
from django.conf.urls.static import static
from django.conf import settings
from shops.views import account, shop_furniture, order, report, edit_furniture, add_furniture
from shops import apis


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('sign_up', views.sign_up , name="sign-up"),


    path('account', views.account, name='shop-account'),
    path('furniture', views.shop_furniture, name='shop-furniture'),
    path('furniture/add/', views.add_furniture, name='shop-add-furniture'),
    re_path(r'^furniture/edit/(?P<furniture_id>\d+)/$', views.edit_furniture, name='shop-edit-furniture'),    
    path('order', views.order, name='shop-order'),
    path('report', views.report, name='shop-report'),

    re_path(r'^api/social/', include('rest_framework_social_oauth2.urls')),

    re_path(r'^api/shop/order/notification/(?P<last_request_time>.+)/$', apis.shop_order_notification),


    # API for Customers
    path('api/customer/shops/', apis.customer_get_shops),
    re_path(r'^api/customer/furnitures/(?P<shop_id>\d+)/$', apis.customer_get_furnitures),
    path('api/customer/order/add/', apis.customer_add_order),
    path('api/customer/order/latest/', apis.customer_get_latest_order),
    path('api/customer/driver/location/', apis.customer_driver_location),

    # API for Drivers
    path('api/driver/orders/ready/', apis.driver_get_ready_orders),
    path('api/driver/order/pick/', apis.driver_pick_order),
    path('api/driver/order/latest/', apis.driver_get_latest_order),
    path('api/driver/order/complete/', apis.driver_complete_order),
    path('api/driver/revenue/', apis.driver_get_revenue),
    path('api/driver/location/update/', apis.driver_update_location),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
