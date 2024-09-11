from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('', include('Accounts.urls')),
    path('', include('admin_panel.urls')),
    path('', include('Product.urls')),
    path('', include('Users.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


