from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('screener/', views.screener, name='screener'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
]