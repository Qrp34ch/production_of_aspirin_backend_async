# lab8_async/urls.py
from django.contrib import admin
from django.urls import path
from calculator.views import calculate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calculate/', calculate, name='calculate'),
]