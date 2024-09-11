from django.shortcuts import render
from Product.models import Variants
from django.http import JsonResponse
from django.db.models import Q, Count
from Product.models import Product,Variants
from django.db import models
from admin_panel.models import Product_offer,Brand_offer
import json
from django.views.decorators.cache import never_cache

@never_cache
def home(request):
    variants = Variants.objects.all().order_by('created_at').reverse()[:4]
    recently_viewed = request.session.get('recently_viewed', [])
    recently_viewed_variants= Variants.objects.filter(id__in=recently_viewed)
    exclusive = Product_offer.objects.all().order_by('-percentage').first()
    exclusive_v = Variants.objects.filter(product=exclusive.product).first()
    p_offers = Product_offer.objects.all()
    b_offers = Brand_offer.objects.all()
    offerd_product_ides = [p_offer.product.id for p_offer in p_offers]
    offerd_brand_ides = [b_offer.brand.id for b_offer in b_offers]
    return render(request, 'index.html',{
        'variants':variants,
        'recently_viewed_variants':recently_viewed_variants,
        'p_offers':p_offers,
        'b_offers':b_offers,
        'offerd_product_ides': offerd_product_ides,
        'offerd_brand_ides': offerd_brand_ides,
        'exclusive':exclusive,
        'exclusive_v':exclusive_v,
        })
@never_cache
def product_search(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'popularity')

    products = Variants.objects.filter(
        Q(product__name__icontains=query) |
        Q(color__icontains=query)
    )

    if sort_by == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'average_ratings':
        products = products.order_by('-product__average_rating')
    elif sort_by == 'featured':
        products = products.filter(product__is_featured=True)
    elif sort_by == 'new_arrivals':
        products = products.order_by('-product__created_at')
    elif sort_by == 'az':
        products = products.order_by('product__name')
    elif sort_by == 'za':
        products = products.order_by('-product__name')
    else:
        products = products.annotate(order_count=Count('orders')).order_by('-order_count')

    results = [
        {
            'name': product.product.name,
            'image_url': product.image.url,
            'color': product.color,
            'ram': product.ram,
            'rom': product.rom,
            'price': product.price,
        } for product in products
    ]

    return JsonResponse(results, safe=False)
