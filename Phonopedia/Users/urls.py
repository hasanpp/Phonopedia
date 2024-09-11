
from django.contrib import admin
from . import views
from django.urls import path,include

urlpatterns = [
    path('view_cart/', views.view_cart, name='view_cart'),
    path('view_address/<int:address_id>', views.view_address, name='view_address'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('view_orders/', views.view_orders, name='view_orders'),
    path('view_wallet/', views.view_wallet, name='view_wallet'),
    path('order_details/<int:orderitem_id>', views.order_details, name='order_details'),
    path('susses', views.susses, name='susses'),
    path('failed', views.failed, name='failed'),
    
    path('add_to_wishlist/<int:variant_id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('add_to_cart/<int:variant_id>', views.add_to_cart, name='add_to_cart'),
    
    path('remove_from_wishlist/<int:wishlist_id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove_from_cart/<int:cart_id>', views.remove_from_cart, name='remove_from_cart'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('cancel_order/<int:order_item_id>/', views.cancel_order, name='cancel_order'),
    
    path('minus_cart_quantity/<int:cart_id>', views.minus_cart_quantity, name='minus_cart_quantity'),
    path('plus_cart_quantity/<int:cart_id>', views.plus_cart_quantity, name='plus_cart_quantity'),
    
    path('add_address', views.add_address, name='add_address'),
    
    path('checkout', views.checkout, name='checkout'),
    path('order', views.order, name='order'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('retry_Payment/', views.retry_Payment, name='retry_Payment'),
    path('invoice/<int:order_item_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),

]
