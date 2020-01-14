from django.contrib import admin
from django.urls import path
from restaurants import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('sign_up', views.sign_up , name="sign-up"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
