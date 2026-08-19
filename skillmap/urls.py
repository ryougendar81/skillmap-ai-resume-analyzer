from django.contrib import admin
from django.urls import path, include
from analyzer.views import landing_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_view, name='landing'),
    path('', include('analyzer.urls')),
    path('accounts/', include('accounts.urls')),
]