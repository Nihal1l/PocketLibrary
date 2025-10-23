
from django.contrib import admin
from django.urls import path, include
from .views import api_root_view
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
     path('admin/', admin.site.urls),
    path('', api_root_view),
    path('api/v1/', include('api.urls'), name='api-root'),
] + debug_toolbar_urls()
