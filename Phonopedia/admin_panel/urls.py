
from django.contrib import admin
from . import views
from django.urls import path,include

urlpatterns = [
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_panel/profile/<int:user_id>/', views.profile, name='profile'),
    path('admin_panel/view_users', views.view_users, name='view_users'),
    path('admin_panel/list_coupons', views.list_coupons, name='list_coupons'),
    path('admin_panel/add_user', views.add_user, name='add_user'),
    path('admin_panel/add_product_offer', views.add_product_offer, name='add_product_offer'),
    path('admin_panel/add_brand_offer', views.add_brand_offer, name='add_brand_offer'),
    path('admin_panel/add_coupon', views.add_coupon, name='add_coupon'),
    path('admin_panel/restrict_users/<int:user_id>/', views.restrict_users, name='restrict_users'),
    path('admin_panel/edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    
    path('admin_panel/view_orders', views.view_orders, name='view_orders_admin'),
    path('admin_panel/view_product_offers', views.view_product_offers, name='view_product_offers'),
    path('admin_panel/view_brand_offers', views.view_brand_offers, name='view_brand_offers'),
    
    path('admin_panel/edit_order/<int:item_id>', views.edit_order, name='edit_order'),
    path('admin_panel/edit_brand_offer/<int:brand_offer_id>', views.edit_brand_offer, name='edit_brand_offer'),
    path('admin_panel/edit_product_offer/<int:product_offer_id>', views.edit_product_offer, name='edit_product_offer'),
    path('admin_panel/edit_coupon/<int:coupon_id>', views.edit_coupon, name='edit_coupon'),
    
    
    path('admin_panel/block_unblock_order/<int:item_id>', views.block_unblock_order, name='block_unblock_order'),
    path('admin_panel/delete_product_offer/<int:offer_id>', views.delete_product_offer, name='delete_product_offer'),
    path('admin_panel/delete_brand_offer/<int:offer_id>', views.delete_brand_offer, name='delete_brand_offer'),
    path('admin_panel/delete_brand_offer/<int:offer_id>', views.delete_brand_offer, name='delete_brand_offer'),
    path('admin_panel/delete_coupon/<int:coupon_id>', views.delete_coupon, name='delete_coupon'),
    
    path('admin_panel/sales_report', views.sales_report, name='sales_report'),
    
    
    path('admin_panel/download_excel_report', views.download_excel_report, name='download_excel_report'),
    path('admin_panel/download_pdf_report', views.download_pdf_report, name='download_pdf_report'),
    
    
     path('orders/data/', views.get_orders_data, name='orders_data'),
]


