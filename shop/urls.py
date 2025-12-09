from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='index'),
    path('shop/', views.home, name='shop'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('add-to-cart-ajax/<int:product_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('purchase-success/', views.purchase_success, name='purchase_success'),
    path('account/', views.account, name='account'),
    path('toggle-favourite/<int:product_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]