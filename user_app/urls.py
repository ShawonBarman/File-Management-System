from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='signup'),
    path('login/', views.user_login, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('accounts/login/', views.user_login, name='signin'),
]
