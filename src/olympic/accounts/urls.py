from django.urls import path, include

from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('comment/', comments, name="comments"),
    path('delete-comment/<int:pk>', delete_comment, name="delete"),
    path('delete-user/<int:pk>', delete_user, name="deleteuser"),
    path('acc', get_user_page, name="acc"),

]