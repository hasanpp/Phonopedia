
from django.contrib import admin
from . import views
from django.urls import path,include

urlpatterns = [
    path('admin_panel/productlist', views.admin_productlist, name='admin_productlist'),
    path('admin_panel/category_list', views.category_list, name='category_list'),
    path('admin_panel/brand_list', views.brand_list, name='brand_list'),
    path('admin_panel/variants_list/<int:product_id>', views.variants_list, name='variants_list'),
    path('admin_panel/product_list_brand/<int:brand_id>', views.product_list_brand, name='product_list_brand'),
    path('admin_panel/product_list_category/<int:category_id>', views.product_list_category, name='product_list_category'),
    
    path('admin_panel/add_category', views.add_category, name='add_category'),
    path('admin_panel/add_brand', views.add_brand, name='add_brand'),
    path('admin_panel/add_variant/<int:product_id>/', views.add_variant, name='add_variant'),
    path('admin_panel/add_product', views.add_product, name='add_product'),
    
    path('admin_panel/edit_brand_status/<int:brand_id>/', views.edit_brand_status, name='edit_brand_status'),
    path('admin_panel/edit_cateogry_status/<int:cateogry_id>/', views.edit_cateogry_status, name='edit_cateogry_status'),
    path('admin_panel/edit_product_status/<int:product_id>/', views.edit_product_status, name='edit_product_status'),
    path('admin_panel/edit_variant_status/<int:variant_id>/', views.edit_variant_status, name='edit_variant_status'),
    path('admin_panel/edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin_panel/edit_variant/<int:variant_id>/', views.edit_variant, name='edit_variant'),
    path('admin_panel/edit_brand/<int:brand_id>/', views.edit_brand, name='edit_brand'),
    path('admin_panel/edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    
    # path('admin_panel/delete_brand/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    # path('admin_panel/delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # path('admin_panel/delete_cateogry/<int:cateogry_id>/', views.delete_cateogry, name='delete_cateogry'),
    # path('admin_panel/delete_variant/<int:variant_id>/', views.delete_variant, name='delete_variant'),
    
    
    path('list_products', views.list_products, name='list_products'),
    path('list_products/variant_details/<int:variant_id>/', views.variant_details, name='variant_details'),
]
