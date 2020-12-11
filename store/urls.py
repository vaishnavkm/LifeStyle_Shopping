from django.urls import path
from . import views 
from .models import *
from . import admin
from . import forms


urlpatterns = [
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('register/',views.register,name='register'),
    path('login/',views.login_id,name='login'),
    path('logout/',views.logout_id,name='logout'),
    path('update_item/',views.updateItem,name='update_item'),
    


    

]
