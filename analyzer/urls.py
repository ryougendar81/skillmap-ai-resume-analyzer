from django.urls import path
from .views import (
    dashboard_view,
    history_view,
    detail_view,
    delete_analysis,
    download_pdf,
    payment_view
)

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/history/', history_view, name='history'),
    path('dashboard/detail/<int:analysis_id>/', detail_view, name='detail'),
    path('dashboard/delete/<int:analysis_id>/', delete_analysis, name='delete_analysis'),
    path('dashboard/pdf/<int:analysis_id>/', download_pdf, name='download_pdf'),
    path('payment/', payment_view, name='payment'),
]