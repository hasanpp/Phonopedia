from django.shortcuts import render,redirect, get_object_or_404
from .models import Variants,Product,Category,Brand, SecondaryImages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from .forms import BrandForm,VariantForm
from .format import crop_image
from django.http import JsonResponse
from admin_panel.views import is_staff
from admin_panel.models import Product_offer,Brand_offer
# Create your views here.
@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def admin_productlist(request):
    products = Product.objects.all()
    return render(request, 'admin/product_list.html', {'products':products})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def variants_list(request, product_id):
    request.session['product_id'] = product_id
    product = Product.objects.get(pk = product_id)
    variants = Variants.objects.filter(product = product_id)
    return render(request, 'admin/variants_list.html', {'variants':variants,'product':product})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def product_list_brand(request, brand_id):
    brand = Brand.objects.get(pk = brand_id)
    products = Product.objects.filter(brand=brand)
    return render(request, 'admin/product_lists.html', {'products':products,'brand':brand})

@login_required(login_url='admin_signin') 
@user_passes_test(is_staff, login_url='/')  
def product_list_category(request, category_id):
    category = Category.objects.get(pk = category_id)
    products = Product.objects.filter(category = category)
    return render(request, 'admin/product_lists.html', {'products':products,'category':category})

@login_required(login_url='admin_signin')  
@user_passes_test(is_staff, login_url='/') 
def add_product(request):
    if request.method == 'POST' :
        name = request.POST['name']
        description = request.POST['description']
        category_id = request.POST['category']
        category = Category.objects.get(id=category_id)
        brand_id = request.POST['brand']
        brand = Brand.objects.get(id=brand_id)
        operating_system = request.POST['operating_system']
        processor = request.POST['processor']
        screen_size = request.POST['screen_size']
        product = Product.objects.create(name=name, description=description, category=category, brand=brand, operating_system=operating_system, processor=processor, screen_size=screen_size)
        messages.success(request,'Product added')
        return redirect(add_product)
    categoryes = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'admin/add_product.html',{'categoryes':categoryes, 'brands':brands})

@login_required(login_url='admin_signin')  
@user_passes_test(is_staff, login_url='/') 
def add_variant(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        print('post')
        form = VariantForm(request.POST, request.FILES)
        if form.is_valid():
            print('valid')
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            
            # Save secondary images
            files = request.FILES.getlist('secondary_images')
            for f in files:
                cropped_image =crop_image(f,target_ratio=(1,1))
                SecondaryImages.objects.create(variant=variant, image=cropped_image)
            
            messages.success(request, 'Variant added successfully')
            return redirect('variants_list', product_id=product.id)
        else:
            print(form.errors)  # Print form errors to the console for debugging
            
    else:
        form = VariantForm()

    return render(request, 'admin/add_variant.html', {'form': form, 'product': product})
    

@login_required(login_url='admin_signin')    
@user_passes_test(is_staff, login_url='/') 
def category_list(request):
    categoryes = Category.objects.all()
    return render(request, 'admin/category_list.html', {'categoryes':categoryes})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        category = Category.objects.create(name=name,description=description)
        messages.success(request, 'Brand was created successfully')
        return redirect(add_category)
    return render(request, 'admin/add_category.html')

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'admin/brand_list.html', {'brands':brands})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand was created successfully')
            return redirect('add_brand')
        else:
            print(form.errors)
            messages.error(request, 'There was an error creating the brand.')
    else:
        form = BrandForm()
    
    return render(request, 'admin/add_brand.html', {'form': form})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def edit_brand_status(request, brand_id):
    brand = Brand.objects.get(pk =brand_id)
    if brand.is_active :
        brand.is_active = False
        brand.save()
    else :
        brand.is_active = True
        brand.save()
    return redirect(brand_list)

@login_required(login_url='admin_signin') 
@user_passes_test(is_staff, login_url='/') 
def edit_product_status(request, product_id):
    product = Product.objects.get(pk =product_id)
    if product.is_active :
        product.is_active = False
        product.save()
    else :
        product.is_active = True
        product.save()
    return redirect(admin_productlist)

@login_required(login_url='admin_signin') 
@user_passes_test(is_staff, login_url='/') 
def edit_variant_status(request, variant_id):
    variant = Variants.objects.get(pk =variant_id)
    if variant.is_active :
        variant.is_active = False
        variant.save()
    else :
        variant.is_active = True
        variant.save()
    return redirect(variants_list,product_id =variant.product.id) 

@login_required(login_url='admin_signin') 
@user_passes_test(is_staff, login_url='/') 
def edit_cateogry_status(request, cateogry_id):
    cateogry = Category.objects.get(pk =cateogry_id)
    if cateogry.is_active :
        cateogry.is_active = False
        cateogry.save()
    else :
        cateogry.is_active = True
        cateogry.save()
    return redirect(category_list)


@login_required(login_url='admin_signin')
def edit_product(request, product_id):
    product = Product.objects.get(pk =product_id)
    category = Category.objects.get(pk=product.category.id)
    categoryes = Category.objects.all()
    brand = Brand.objects.get(pk=product.brand.id)
    brands = Brand.objects.all()
    if request.method == 'POST' :
        name = request.POST['name']
        description = request.POST['description']
        category_id = request.POST['category']
        category = Category.objects.get(id=category_id)
        brand_id = request.POST['brand']
        brand = Brand.objects.get(id=brand_id)
        operating_system = request.POST['operating_system']
        processor = request.POST['processor']
        screen_size = request.POST['screen_size']
        
        product = Product.objects.get(pk =product_id)
        
        product.name = name
        product.description = description
        product.category = category
        product.brand = brand
        product.operating_system = operating_system
        product.processor = processor
        product.screen_size = screen_size
        
        product.save()
        messages.success(request,'Product updated')
        return redirect(admin_productlist)
    return render(request, 'admin/edit_product.html', {'product':product,'category':category,'brand':brand,'brands':brands,'categoryes':categoryes})


@login_required(login_url='admin_signin')
def edit_variant(request, variant_id):
    variant = get_object_or_404(Variants, id=variant_id)

    if request.method == 'POST':
        # Retrieve form data
        color = request.POST.get('color')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        ram = request.POST.get('ram')
        rom = request.POST.get('rom')

        # Retrieve images
        primary_image = request.FILES.get('image')
        secondary_images = request.FILES.getlist('secondary_images')

        # Update the Variant object with new data
        variant.color = color
        variant.quantity = quantity
        variant.price = price
        variant.ram = ram
        variant.rom = rom

        # Update primary image if a new one is uploaded
        if primary_image:
            variant.image = primary_image

        # Clear existing secondary images if new ones are uploaded
        if secondary_images:
            variant.secondaryimage_set.all().delete()
            for image in secondary_images:
                variant.secondaryimage_set.create(image=image)

        # Save the changes
        variant.save()

        # Display a success message
        messages.success(request, 'Variant updated successfully!')
        return redirect('variants_list', product_id=variant.product.id)  # Redirect to some view

    variant = Variants.objects.get(pk = variant_id)
    secondary_images = SecondaryImages.objects.filter(variant = variant)
    return render(request,'admin/edit_variant.html',{'variant':variant,'secondary_images':secondary_images})


@login_required(login_url='admin_signin')
def edit_brand(request,brand_id):
    brand = Brand.objects.get(pk=brand_id)
    if request.method == 'POST' :
        brand.name = request.POST['name']
        brand.description = request.POST['description']
        brand.save()
        return redirect(brand_list) 
    return render(request,'admin/edit_brand.html',{'brand':brand})

@login_required(login_url='admin_signin')
def edit_category(request,category_id):
    category = Category.objects.get(pk=category_id)
    if request.method == 'POST' :
        category.name = request.POST['name']
        category.description = request.POST['description']
        category.save()
        return redirect(category_list) 
    return render(request,'admin/edit_category.html',{'category':category})

def list_products(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    variants = Variants.objects.all()
    products = Product.objects.all()
    p_offers = Product_offer.objects.all()
    offerd_product_ides = [p_offer.product.id for p_offer in p_offers]
    b_offers = Brand_offer.objects.all()
    offerd_brand_ides = [b_offer.brand.id for b_offer in b_offers]
    # Assuming colors are stored in a specific field
    colors = Variants.objects.values_list('color', flat=True).distinct()
    
    context = {
        'variants': variants,
        'products': products,
        'p_offers': p_offers,
        'b_offers': b_offers,
        'offerd_product_ides': offerd_product_ides,
        'offerd_brand_ides': offerd_brand_ides,
        'categories': categories,
        'brands': brands,
        'colors': colors,
    }
    return render(request,'product_list.html',context)

def variant_details(request, variant_id):
    variant = Variants.objects.get(pk=variant_id)
    product = variant.product
    brand = product.brand
    # relaated_products = Product.objects.filter(brand = brand)
    same_variants = Variants.objects.filter(product = product)
    relaated_variants = Variants.objects.filter(product__brand = brand)[:4]
    # print(relaated_variants)
    if len(relaated_variants) > 4:
        relaated_variants = relaated_variants[1:4]
    secondary_images = SecondaryImages.objects.filter(variant = variant_id)
    p_offers = Product_offer.objects.filter(product = product)
    b_offers = Brand_offer.objects.filter(brand = brand)
    if p_offers :
        # print(p_offers[0].percentage)
        if b_offers and b_offers[0].percentage > p_offers[0].percentage:
            offer = float(b_offers[0].percentage)
            offerd_price = float(variant.price) - (float(variant.price)*offer)/100 
            offer = b_offers[0]
        else :
            offer = float(p_offers[0].percentage)
            offerd_price = float(variant.price) - (float(variant.price)*offer)/100 
            offer = p_offers[0]
    elif b_offers :
        offer = float(b_offers[0].percentage)
        offerd_price = float(variant.price) - (float(variant.price)*offer)/100 
        offer = b_offers[0]
    else :
        offer = 0
        offerd_price = variant.price - (variant.price*offer)/100 
    recently_viewed = request.session.get('recently_viewed', [])
    if str(variant_id) in recently_viewed:
        recently_viewed.remove(str(variant_id))
    recently_viewed.insert(0, str(variant_id))
    request.session['recently_viewed'] = recently_viewed[:4]
    pp_offers = Product_offer.objects.all()
    offerd_product_ides = [p_offer.product.id for p_offer in pp_offers]
    bb_offers = Brand_offer.objects.all()
    offerd_brand_ides = [b_offer.brand.id for b_offer in bb_offers]
    return render(request, 'variant_details.html',{
        'variant':variant,
        'secondary_images':secondary_images, 
        'relaated_variants':relaated_variants, 
        'same_variants':same_variants, 
        'offer':offer,
        'offerd_price':offerd_price,
        'p_offers': pp_offers,
        'b_offers': bb_offers,
        'offerd_product_ides': offerd_product_ides,
        'offerd_brand_ides': offerd_brand_ides,
        })
      
