from django.shortcuts import render,redirect
from Accounts.views import signin
from django.views.decorators.cache import never_cache
from Accounts.views import account_details
from Product.models import Variants
from .models import Custom_User as User,Wishlist,Cart,Address,DeliveryAddress,Orders,Order_items, Wallet, Transactions
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import timedelta
from django.conf import settings
from admin_panel.models import Brand_offer, Product_offer
from admin_panel.models import Coupon,Coupon_usage
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import date
from django.templatetags.static import static
import razorpay
# Create your views here.
def create_wallet(user):
    wallet = Wallet.objects.filter(user=user)
    if len(wallet) == 0 :
        print('hi')
        wallet = Wallet.objects.create(user = user, balence = 0.00)

@never_cache
def view_cart(request):
    if request.user.is_authenticated:
        user = request.user
        carts = Cart.objects.filter(user=user)
        p_offers = Product_offer.objects.all()
        b_offers = Brand_offer.objects.all()
        offerd_product_ides = [p_offer.product.id for p_offer in p_offers]
        offerd_brand_ides = [b_offer.brand.id for b_offer in b_offers]
        c_id =[]
        subtotal = 0
        for cart in carts:
            if cart.variant.product.id in offerd_product_ides:
                for offer in p_offers:
                    if float(cart.unit_price) != (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100):
                        cart.unit_price = (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100)
            elif cart.variant.product.brand.id in offerd_brand_ides :
                for offer in b_offers:
                    if float(cart.unit_price) != (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100):
                        cart.unit_price = (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100)
            else :
                if cart.unit_price != cart.variant.price:
                    cart.unit_price = cart.variant.price
                    cart.unit_price = float(cart.unit_price)
            cart.price = cart.quantity * cart.unit_price
            c_id.append(cart.id)
            subtotal += float(cart.price) 
        tax = (0.08/100) * float(subtotal)
        tax = round(tax, 2)
        total = float(subtotal) +tax 
        total = round(total, 2)
        request.session['carts'] = c_id
        request.session['subtotal'] = int(subtotal)
        request.session['tax'] =  int(tax)
        request.session['total'] =  int(total)
        
        return render(request,'cart.html',
                      {
                            'carts':carts,
                            'subtotal':subtotal,
                            'tax':tax,
                            'total':total,
                            'p_offers': p_offers,
                            'b_offers': b_offers,
                            'offerd_product_ides': offerd_product_ides,
                            'offerd_brand_ides': offerd_brand_ides,
                          })
    else:
        return redirect(signin)
    
def view_address(request, address_id):
    address =Address.objects.get(pk=address_id)
    return JsonResponse({
            'status': 'success',
            'state': address.state,
            'district': address.district,
            'city': address.city,
            'place': address.place,
            'pin': address.pin,
            'house_name': address.house_name,
            'landmark': address.landmark,
            'road': address.road,
            
        }, status=200)
    
@never_cache
def wishlist(request):
    if request.user.is_authenticated:
        user = request.user
        wishlists = Wishlist.objects.filter(user=user)
        print(wishlists)
        p_offers = Product_offer.objects.all()
        b_offers = Brand_offer.objects.all()
        offerd_product_ides = [p_offer.product.id for p_offer in p_offers]
        offerd_brand_ides = [b_offer.brand.id for b_offer in b_offers]
        return render(request,'wishlist.html',
            {
            'wishlists':wishlists,
            'p_offers': p_offers,
            'b_offers': b_offers,
            'offerd_product_ides': offerd_product_ides,
            'offerd_brand_ides': offerd_brand_ides,
            })
    else:
        return redirect(signin)
    
    
@never_cache
def view_orders(request):
    if request.user.is_authenticated:
        order_items = Order_items.objects.filter(user=request.user).order_by('-order__order_date')
        return render(request,'orders.html',{'order_items':order_items})
    else:
        return redirect(signin)
    
@never_cache
def order_details(request,orderitem_id):
    if request.user.is_authenticated:
        order_item = Order_items.objects.get(pk=orderitem_id)
        order_item.order.delivery_date = order_item.order.order_date + timedelta(days=14)  
        order_item.save()
        return render(request,'order_details.html',{'order_item':order_item})
    else:
        return redirect(signin)
    

def add_to_wishlist(request,variant_id):
    if request.user.is_authenticated:
        user = request.user
        variant = Variants.objects.get(pk=variant_id)
        
        if Wishlist.objects.filter(variant=variant, user=user).exists():
            return JsonResponse({'status': 'exists'}, status=200)
        
        Wishlist.objects.create(user=user, variant=variant)
        return JsonResponse({'status': 'added'}, status=200)
    else :
        return JsonResponse({'status': 'unauthenticated'})


def add_to_cart(request,variant_id):
    if request.user.is_authenticated:
        user = request.user
        variant = Variants.objects.get(pk=variant_id)
        
        p_offers = Product_offer.objects.all()
        b_offers = Brand_offer.objects.all()
        offerd_product_ides = [p_offer.product.id for p_offer in p_offers]
        offerd_brand_ides = [b_offer.brand.id for b_offer in b_offers]
        if variant.product.id in offerd_product_ides :
            for offer in p_offers:
                if offer.product.id == variant.product.id :
                    if variant.product.brand.id in offerd_brand_ides:
                        for b_offer in b_offers:
                            if b_offer.percentage > offer.percentage:
                                unit_price = float(variant.price) - (float(variant.price)*float(b_offer.percentage))/100
                            else:
                                unit_price = float(variant.price) - (float(variant.price)*float(offer.percentage))/100
                    else :
                        unit_price = float(variant.price) - (float(variant.price)*float(offer.percentage))/100
        elif variant.product.brand.id in offerd_brand_ides:
            for offer in b_offers:
                if offer.brand.id == variant.product.brand.id:
                    unit_price = float(variant.price) - (float(variant.price)*float(offer.percentage))/100 
        else:
            unit_price = variant.price
        cart_item, created = Cart.objects.get_or_create(user=user, variant=variant,unit_price=unit_price)
        if not created:
            if cart_item.quantity < cart_item.variant.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({'status': 'quantity_updated'}, status=200)
            return JsonResponse({'status': 'max'}, status=200)
        return JsonResponse({'status': 'added'}, status=200)
    else :
        return JsonResponse({'status': 'unauthenticated'})



def remove_from_wishlist(request,wishlist_id):
    wishlist = Wishlist.objects.get(pk=wishlist_id)
    wishlist.delete()
    return redirect('wishlist')
def remove_from_cart(request,cart_id):
    cart = Cart.objects.get(pk=cart_id)
    cart.delete()
    return redirect(view_cart)
def cancel_order(request,order_item_id):
    create_wallet(request.user)
    order_item = Order_items.objects.get(pk=order_item_id)
    if order_item.order.pyment_status == 'done':
        wallet = Wallet.objects.get(user=request.user)
        amount = float(order_item.price) - float(order_item.order.discount)
        transaction = Transactions.objects.create(order_item=order_item, wallet=wallet, variant = order_item.variant, amount = amount)
        order_item.order.discount = 0
        wallet.balence = float(wallet.balence)
        wallet.balence += float(transaction.amount)
        order_item.order.save()
        wallet.save()
    order_item.status = 'cancelled'
    order_item.is_active = False
    variant = Variants.objects.get(pk=order_item.variant.id) 
    variant.quantity += order_item.quantity
    variant.save()
    order_item.save()
    return redirect(view_orders)

def delete_address(request,address_id):
    address = Address.objects.get(pk=address_id)
    address.delete()
    return redirect(account_details)


def plus_cart_quantity(request, cart_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(pk=cart_id)
        
        if cart.quantity < cart.variant.quantity :
            cart.quantity += 1
            cart.price = cart.quantity * cart.unit_price
            cart.save()
            carts = Cart.objects.filter(user=request.user)
            subtotal=0
            for c in carts:
                subtotal +=c.price
            request.session['subtotal'] = int(subtotal)
            tax = (0.08/100) * float(subtotal)
            total = float(subtotal) +tax
            request.session['tax'] =  int(tax)
            request.session['total'] =  int(total)
            return JsonResponse({
                'status': 'success',
                'quantity': cart.quantity,
                'price': cart.price,
                'subtotal': subtotal,
            }, status=200)
        return JsonResponse({'status': 'max'}, status=200)
    return JsonResponse({'status': 'unauthenticated'}, status=403)
def minus_cart_quantity(request, cart_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(pk=cart_id)
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.price = cart.quantity * cart.unit_price
            cart.save()
            carts = Cart.objects.filter(user=request.user)
            subtotal=0
            for c in carts:
                subtotal +=c.price
            request.session['subtotal'] = int(subtotal)
            tax = (0.08/100) * float(subtotal)
            total = float(subtotal) +tax
            request.session['tax'] =  int(tax)
            request.session['total'] =  int(total)
            return JsonResponse({
                'status': 'success',
                'quantity': cart.quantity,
                'price': cart.price,
                'subtotal': subtotal,
                'total':subtotal+400
            }, status=200)
        
        return JsonResponse({'status': 'min_quantity'}, status=200)
    
    return JsonResponse({'status': 'unauthenticated'}, status=403)


def add_address(request):
    if request.method == 'POST':
        id = request.POST['id']
        if id != 'old':
            address = Address.objects.get(pk=id)
            state = request.POST['state']
            city = request.POST['city']
            place = request.POST['place']
            pin = request.POST['pin']
            road = request.POST['road']
            house_name = request.POST['house_name']
            landmark = request.POST['landmark']
            address.state=state
            address.city =city
            address.place =place
            address.pin =pin
            address.road =road
            address.house_name =house_name
            address.landmark =landmark
            address.city =city
            address.save()
        else :
            state = request.POST['state']
            district = request.POST['district']
            city = request.POST['city']
            place = request.POST['place']
            pin = request.POST['pin']
            road = request.POST['road']
            house_name = request.POST['house_name']
            landmark = request.POST['landmark']
            user = request.user
            address = Address.objects.create(state=state,district=district,city=city,place=place,pin=pin,road=road,house_name=house_name,landmark=landmark,user=user)
            address.save()
    return redirect(account_details)

@csrf_exempt
def order(request):
    user = request.user
    c_id = request.session.get('carts', [])
    tax = request.session.get('tax', 0)
    
    # Fetch the cart items
    carts = [Cart.objects.get(pk=id) for id in c_id]
    
    
    subtotal = request.session['subtotal']
    print(subtotal)
    total = subtotal + tax

    if request.method == 'POST':
        
        state = request.POST.get('state')
        district = request.POST.get('district')
        city = request.POST.get('city')
        place = request.POST.get('place')
        pin = request.POST.get('pin')
        road = request.POST.get('road')
        house_name = request.POST.get('house_name')
        landmark = request.POST.get('landmark')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        pymd = request.POST.get('pymd') 
        pyst = request.POST.get('pyst')
        coupon_code =  request.POST.get('coupon_code')
        save_address = request.POST.get('save_address')
        discount = 0
        coupon_usage = 0
        
        if save_address == 'yes':
            print ('hi')
            Address.objects.create(
                state = state,
                district = district,
                city = city,
                place = place, 
                pin = pin,
                road = road,
                landmark = landmark,
                house_name = house_name,
                user = user
            )

        
        if coupon_code :
            
            coupon = Coupon.objects.get(code=coupon_code)
            discount = int(total) *(int(coupon.percentage)/100)
            
            total = float(total)
            total -= float(discount)   
            
            coupon_usage = Coupon_usage.objects.create(user=user,coupon=coupon)
        # Create the DeliveryAddress
        delivery_address = DeliveryAddress.objects.create(
            state=state,
            district=district,
            city=city,
            place=place,
            pin=pin,
            house_name=house_name,
            road=road,
            landmark=landmark,
            name=name,
            phone=phone,
        )
        
        if pymd == 'wallet payment' :
            wallet = Wallet.objects.get(user=user)
            wallet.balence = float(wallet.balence) - float(total)
            wallet.save()
            pyst = 'done'
        # Create the Order
        order = Orders.objects.create(
            delivery_address=delivery_address,
            pyment_method=pymd,
            pyment_status=pyst,
            subtotal=subtotal,
            tax=tax,
            discount=discount,  
            total=total,
            user=user
        )
        
        
        if pymd == 'wallet payment' :
            transaction = Transactions.objects.create(order=order, wallet=wallet, type = 'debit', amount = total)
        
        if coupon_usage != 0:
            coupon_usage.order = order
            coupon_usage.save()
        # Create Order Items
        for cart in carts:
            Order_items.objects.create(
                order=order,
                variant=cart.variant,
                unit_price=cart.unit_price,
                price=cart.unit_price * cart.quantity,
                quantity=cart.quantity,
                status='Order placed',
                user=user,
            )
            cart.variant.quantity = int(cart.variant.quantity) - int(cart.quantity)
            cart.variant.save()
        cart_items = Cart.objects.filter(user=request.user)
        cart_items.delete()
        del request.session['carts']
        
        return JsonResponse({
            'status': 'success',
            # 'razorpay_order_id': razorpay_order_id,
            'razorpay_key': settings.RAZORPAY_API_KEY,
            'amount': total
        }, status=200)
    return JsonResponse({'status': 'failed'}, status=200)

      
def checkout(request):
    user = User.objects.get(username = request.user)
    addresses = Address.objects.filter(user = user)
    c_id = request.session['carts']
    tax = request.session['tax']
    p_offers = Product_offer.objects.all()
    b_offers = Brand_offer.objects.all()
    offerd_product_ides = [p_offer.product.id for p_offer in p_offers]
    offerd_brand_ides = [b_offer.brand.id for b_offer in b_offers]
    
    
    carts = []
    for id in c_id:
        c = Cart.objects.get(pk=id)
        carts.append(c)
    price = 0 
    subtotal = 0
    for cart in carts:
        if cart.variant.product.id in offerd_product_ides:
            for offer in p_offers:
                if float(cart.unit_price) != (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100):
                    cart.unit_price = (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100)
        elif cart.variant.product.brand.id in offerd_brand_ides :
            for offer in b_offers:
                if float(cart.unit_price) != (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100):
                    cart.unit_price = (float(cart.variant.price) - (float(cart.variant.price)*float(offer.percentage))/100)
        else :
            if cart.unit_price != cart.variant.price:
                cart.unit_price = cart.variant.price
                cart.unit_price = float(cart.unit_price)
        cart.price = cart.unit_price * cart.quantity
        cart.price = float(cart.price)
        subtotal += cart.price
        if not cart.variant.is_active :
            messages.error(request,f'!The product {cart.variant.product.name} is currently unavailable! Please remove it from cart to continue')
            return redirect(view_cart)
        elif cart.variant.quantity == 0 :
            messages.error(request,f'!The product {cart.variant.product.name} is now out of stock! We\'ll update our inventory as soon as possible. Please remove the product from your cart to proceed.')
            return redirect(view_cart)
        elif cart.variant.quantity < cart.quantity :
            messages.error(request,f'!The product {cart.variant.product.name} is only awailable {cart.variant.quantity} pieces! We\'ll update our inventory as soon as possible. Please decrease the quantity to proceed.')
            return redirect(view_cart)
    if len(carts) == 0:
            messages.error(request,'Plese add a product to cart for proceed.')
            return redirect(view_cart)
    coupon_code = request.session.get('coupon_code', 0)

    if coupon_code != 0 :
        total = request.session['total']
        
    total = subtotal + tax + 50
    amount = int(total)*100
    amount = int(amount)
    c_date  = date.today()
    coupons = Coupon.objects.filter(expiry__gt = c_date, min_amount__lte = total, max_amount__gte = total)
    coupon_usages = Coupon_usage.objects.filter(user=user)
    for usage in coupon_usages :
        code = usage.coupon.code
        print(code)
        coupons = coupons.exclude(code = code)
        
    wallet = Wallet.objects.get(user=user) 
    request.session['subtotal'] = int(subtotal)
    total = round(total, 2)
    return render(request,'check_out.html', {'user':user,'addresses':addresses,'subtotal':subtotal,'tax':tax,'total':total,'carts':carts, 'amount':amount, 'coupons':coupons, 'wallet':wallet})


def susses(request):
    return render(request,'susses.html')


def failed(request):
    return render(request,'failed.html')



# def verify_payment(request):
#     if request.method == "POST":
#         razorpay_payment_id = request.POST.get('razorpay_payment_id')
#         razorpay_order_id = request.POST.get('razorpay_order_id')
#         razorpay_signature = request.POST.get('razorpay_signature')

#         try:
#             # Verify the payment signature using Razorpay
#             # razorpay_client.utility.verify_payment_signature({
#             #     'razorpay_order_id': razorpay_order_id,
#             #     'razorpay_payment_id': razorpay_payment_id,
#             #     'razorpay_signature': razorpay_signature
#             # })

#             # Update the order with the payment ID
#             order = Orders.objects.get(razorpay_order_id=razorpay_order_id)
#             order.payment_id = razorpay_payment_id
#             order.status = 'Paid'
#             order.save()

#             return JsonResponse({'status': 'success'})

#         except razorpay.errors.SignatureVerificationError as e:
#             return JsonResponse({'status': 'failed', 'error': str(e)}, status=400)

def view_wallet(request):
    create_wallet(request.user)
    wallet = Wallet.objects.get(user=request.user)
    transactions = Transactions.objects.all()
    return render(request,'wallet.html',{'wallet':wallet,'transactions':transactions})

def retry_Payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        pyst = request.POST.get('pyst')
        orders = Orders.objects.get(pk=order_id)
        orders.pyment_status = pyst
        orders.save()
        return JsonResponse({
            'status': 'success',
            # 'razorpay_order_id': razorpay_order_id,
            'razorpay_key': settings.RAZORPAY_API_KEY,
            
        }, status=200)

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'Plese apply a coupon code'})
        total_price = float(request.POST.get('total_price')) 
        coupon = Coupon.objects.get(code=coupon_code)
        discount = int(total_price) *(int(coupon.percentage)/100)
        total = int(total_price) - discount
        # Update session or order with the discounted price
        amount = int(total)*100
        amount = int(amount)
        request.session['total'] = total
        request.session['amount'] = amount
        request.session['discount'] = discount
        request.session['coupon_code'] = coupon_code
        
        return JsonResponse({
            'success': True,
            'total':total,
            'discount':discount,
            'coupon_code':coupon_code,
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def generate_invoice_pdf(request, order_item_id):
    order_item = Order_items.objects.get(id=order_item_id) 
    template_path = 'invoice.html' 
    context = {'order_item': order_item}

    # Render the template to a string
    template = get_template(template_path)
    html = template.render(context)

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # If there's an error, show some fallback HTML
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
















