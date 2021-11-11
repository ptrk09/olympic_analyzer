from django.urls import path, include

from .views import *

urlpatterns = [
    path('find/', index, name="menu"),
    path('test/', test),
    path('logout/', log_out),
]