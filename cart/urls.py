from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<int:pk>/', views.add_to_cart, name='add'),
    path('update/<int:pk>/', views.update_cart_item, name='update'),
    path('remove/<int:pk>/', views.remove_from_cart, name='remove'),
]
