#admin_palen/views.py
from django.shortcuts import render,redirect
from Accounts.views import User,login_required,user_passes_test,logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from Home.views import home
from Users.models import Orders,Order_items,Wallet,Transactions, Custom_User
from Product.models import Variants, Product, Brand, Category
from .models import Brand_offer, Product_offer, Coupon, Coupon_usage
from django.http import HttpResponse
from django.http import JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import date,timedelta
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from django.db.models import Sum,Count, F
from django.utils.timezone import now
from Users.models import Orders
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from django.template.loader import render_to_string
from io import BytesIO
import pandas as pd, csv 


def create_wallet(user):
    wallet = Wallet.objects.filter(user=user)
    if len(wallet) == 0 :
        wallet = Wallet.objects.create(user = user, balence = 0.00)


@never_cache
@login_required(login_url='admin_signin')
def admin_panel(request):
    today = timezone.now()

    # Get sales data grouped by month
    sales_data = Orders.objects.annotate(month=TruncMonth('order_date')).values('month').annotate(total=Sum('total')).order_by('month')

    labels = [entry['month'].strftime("%Y-%m") for entry in sales_data]
    totals = [entry['total'] for entry in sales_data]

    # Filter totals
    filters = {
        'day': Orders.objects.filter(order_date=today).aggregate(total=Sum('total')),
        'week': Orders.objects.filter(order_date__gte=today - timedelta(days=7)).aggregate(total=Sum('total')),
        'month': Orders.objects.filter(order_date__month=today.month, order_date__year=today.year).aggregate(total=Sum('total')),
        'year': Orders.objects.filter(order_date__year=today.year).aggregate(total=Sum('total')),
        'custom': None,  # Handle custom range filtering separately if needed
    }
    
    top_brands = Brand.objects.annotate( orderitem_count=Count('prodcuts__variants__order_items') ).order_by('-orderitem_count')[:5]
    top_products = Product.objects.annotate( orderitem_count=Count('variants__order_items') ).order_by('-orderitem_count')[:10]
    top_categorys = Category.objects.annotate( orderitem_count=Count('prodcuts__variants__order_items') ).order_by('-orderitem_count')[:4]
    customers = Custom_User.objects.count()
    total_purchase = Variants.objects.aggregate( total=Sum(F('quantity') * F('price')) )
    total_sales = Orders.objects.aggregate(total=Sum('total'))

    total_sales = int((total_sales['total']))
    total_purchase = int((total_purchase['total']))
    
    # for b in top_products:
    #     print(b.name)
        
    # Example: Get user and variants for display
    if request.session.session_key:
        user_id = request.session.get("_auth_user_id")   
        user = User.objects.get(pk=user_id)
        if user.is_staff:
            variants = Variants.objects.all().order_by('created_at').reverse()[:4]
            outofstks = Variants.objects.filter(quantity=0)
            return render(request, 'admin/admin_panel.html', {
                'admin': user,
                'variants': variants,
                'outofstks': outofstks,
                'labels': labels,
                'totals': totals,
                'filters': filters,
                'top_brands': top_brands,
                'top_products': top_products,
                'top_categorys': top_categorys,
                'customers': customers,
                'total_purchase':total_purchase,
                'total_sales':total_sales,
            })
        else:
            return redirect(home)
        
        
def is_staff(user):
    return user.is_staff
@never_cache
@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def view_users(request):
    if request.session.session_key:
        user_id = request.session.get("_auth_user_id")
        user = User.objects.get(pk=user_id)
        
    users = User.objects.all().filter(is_staff=False)
    return render(request, 'admin/users.html',{'users':users, 'admin':user})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def restrict_users(request, user_id):
    user = User.objects.get(pk = user_id)
    if user.is_active :
        user.is_active = False
        user.save()
    else :
        user.is_active = True
        user.save()
    return redirect(view_users)

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def edit_user(request, user_id):
    user = User.objects.get(pk = user_id)
    if request.method == 'POST' :
        user.username = request.POST['username']
        user.first_name = request.POST['f_name']
        user.last_name = request.POST['l_name']
        user.email = request.POST['email']
        user.save()
        return redirect(view_users)
    return render(request, 'admin/edit_user.html',{'user':user})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    return render(request, 'admin/profile.html',{'user':user})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_user(request):
    if request.method == 'POST' :
        try :
            email = request.POST.get('email')
            username = request.POST['username']
            password = request.POST['password']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            user = User.objects.create_user(username=username, password=password, email=email, first_name=f_name, last_name=l_name)
            return redirect (view_users)
        except Exception as e:
             messages.error = "This username or email address is already taken. Please choose another one."
             return redirect(add_user)
    return render(request, 'admin/add_user.html')

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_user(request):
    if request.method == 'POST' :
        try :
            email = request.POST.get('email')
            username = request.POST['username']
            password = request.POST['password']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            user = User.objects.create_user(username=username, password=password, email=email, first_name=f_name, last_name=l_name)
            return redirect (view_users)
        except Exception as e:
             messages.error = "This username or email address is already taken. Please choose another one."
             return redirect(add_user)
    return render(request, 'admin/add_user.html')

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_user(request):
    if request.method == 'POST' :
        try :
            email = request.POST.get('email')
            username = request.POST['username']
            password = request.POST['password']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            user = User.objects.create_user(username=username, password=password, email=email, first_name=f_name, last_name=l_name)
            return redirect (view_users)
        except Exception as e:
             messages.error = "This username or email address is already taken. Please choose another one."
             return redirect(add_user)
    return render(request, 'admin/add_user.html')


@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_product_offer(request):
    products = Product.objects.all()
    offeres =Product_offer.objects.all()
    for offer in offeres:
        products = products.exclude(pk = offer.product.id)
    if request.method == 'POST':
        name = request.POST['name']
        product = request.POST['product']
        product = Product.objects.get(pk=product)
        percentage = request.POST['percentage']
        description = request.POST['description']
        product_offer = Product_offer.objects.create(name=name, product=product, description=description, percentage=percentage)
        messages.success(request,'Product offer created')
    return render(request,'admin/add_product_offer.html',{'products':products})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_brand_offer(request):
    brands = Brand.objects.all()
    offeres =Brand_offer.objects.all()
    for offer in offeres:
        brands = brands.exclude(pk = offer.brand.id)
    if request.method == 'POST':
        name = request.POST['name']
        brand = request.POST['brand']
        brand = Brand.objects.get(pk=brand)
        percentage = request.POST['percentage']
        description = request.POST['description']
        brand_offer = Brand_offer.objects.create(name=name, brand=brand, description=description, percentage=percentage)
        messages.success(request,'Brand offer created')
    return render(request,'admin/add_brand_offer.html',{'brands':brands})



@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def add_coupon(request):
        
    if request.method == 'POST':
        expiry = request.POST['date']
        percentage = request.POST['percentage']
        min_amount = request.POST['min_amount']
        max_amount = request.POST['max_amount']
        description = request.POST['description']
        coupon = Coupon.objects.create(expiry=expiry, percentage=percentage, description=description, max_amount=max_amount, min_amount=min_amount)
        messages.success(request,f'Coupon code {coupon.code} created')
    return render(request,'admin/add_coupon.html')



@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def edit_product_offer(request,product_offer_id):
    products = Product.objects.all()
    product_offer = Product_offer.objects.get(pk=product_offer_id)
    offeres =Product_offer.objects.all()
    for offer in offeres:
        products = products.exclude(pk = offer.product.id)
    if request.method == 'POST':
        name = request.POST['name']
        product = request.POST['product']
        product = Product.objects.get(pk=product)
        percentage = request.POST['percentage']
        description = request.POST['description']
        
        product_offer.name=name
        product_offer.product=product
        product_offer.percentage=percentage
        product_offer.description=description
        product_offer.save()
        messages.success(request,'Product offer updated')
    return render(request,'admin/edit_product_offer.html',{'products':products,'product_offer':product_offer})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def edit_brand_offer(request,brand_offer_id):
    brands = Brand.objects.all()
    brand_offer = Brand_offer.objects.get(pk=brand_offer_id)
    offeres =Brand_offer.objects.all()
    for offer in offeres:
        brands = brands.exclude(pk = offer.brand.id)
    if request.method == 'POST':
        name = request.POST['name']
        brand = request.POST['brand']
        brand = Brand.objects.get(pk=brand)
        percentage = request.POST['percentage']
        description = request.POST['description']
        brand_offer.name=name
        brand_offer.brand=brand
        brand_offer.percentage=percentage
        brand_offer.description=description
        brand_offer.save()
        messages.success(request,'Brand offer updated')
    return render(request,'admin/edit_brand_offer.html',{'brands':brands,'brand_offer':brand_offer})


@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def view_orders(request):
    order_items = Order_items.objects.all()
    return render(request, 'admin/view_orders.html',{'order_items':order_items,})


@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def view_product_offers(request):
    product_offers = Product_offer.objects.all()
    return render(request, 'admin/view_product_offers.html',{'product_offers':product_offers,})


@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def view_brand_offers(request):
    brand_offers = Brand_offer.objects.all()
    return render(request, 'admin/view_brand_offers.html',{'brand_offers':brand_offers,})



@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def edit_order(request,item_id):
    item = Order_items.objects.get(pk=item_id)
    user = item.order.user
    create_wallet(user)
    if request.method == 'POST':
        status = request.POST['status']
        if status == 'cancelled' :
            variant = Variants.objects.get(pk=item.variant.id) 
            variant.quantity += item.quantity
            variant.save()
            if item.order.pyment_status == 'done':
                wallet = Wallet.objects.get(user=user)
                amount = float(item.price) - float(item.order.discount)
                transaction = Transactions.objects.create(order_item=item, wallet=wallet, variant = item.variant, amount = amount)
                item.order.discount = 0
                wallet.balence = float(wallet.balence)
                wallet.balence += float(transaction.amount)
                item.order.save()
                wallet.save()
        elif status == 'delivered':
            order = Orders.objects.get(pk = item.order.id)
            order.pyment_status = 'done'
            order.delivery_date = now()
            order.save()
        elif status == 'returned':
            variant = Variants.objects.get(pk=item.variant.id) 
            variant.quantity += item.quantity
            variant.save()
            if item.order.pyment_status == 'done':
                wallet = Wallet.objects.get(user=user)
                amount = float(item.price) - float(item.order.discount)
                transaction = Transactions.objects.create(order_item=item, wallet=wallet, variant = item.variant, amount = item.price)
                item.order.discount = 0
                wallet.balence = float(wallet.balence)
                wallet.balence += float(transaction.amount)
                item.order.save()
                wallet.save()
        elif item.status == 'cancelled' and status == 'Order placed' :
            variant = Variants.objects.get(pk=item.variant.id) 
            if variant.quantity < item.quantity:
                messages.error('the items is not that much quantity awailabele')
                return redirect(view_orders)
            variant.quantity -= item.quantity
            variant.save()
            if item.order.pyment_status == 'pending':
                wallet = Wallet.objects.get(user=user)
                if wallet.balence >= item.price :
                    transaction = Transactions.objects.create(order_item=item, wallet=wallet, variant = item.variant, amount = item.price)
                    wallet.balence -=transaction.amount
                    wallet.save()
                else :
                    item.order.pyment_method = 'cash on delivery'
        item.status = status
        item.save()
        return redirect(view_orders)
        
    return render(request, 'admin/edit_order.html',{'order':item.order,'item':item})

@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def edit_coupon(request,coupon_id):
    coupon = Coupon.objects.get(pk=coupon_id)
    if request.method == 'POST':
        expiry = request.POST['date']
        percentage = request.POST['percentage']
        description = request.POST['description']
        min_amount = request.POST['min_amount']
        max_amount = request.POST['max_amount']
        coupon.expiry = expiry
        coupon.percentage = percentage
        coupon.min_amount = min_amount
        coupon.max_amount = max_amount
        coupon.description = description
        c = coupon.code
        if len(percentage) == 1:
            percentage = '0' + percentage
        coupon.code = coupon.code[:-2] + percentage
        coupon.save()
        # coupon = Coupon.objects.create(expiry=expiry, percentage=percentage, description=description)
        messages.success(request,f'Coupon code {c} has edited')
        return redirect(list_coupons)
    return render(request,'admin/edit_coupon.html',{'coupon':coupon})





@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def block_unblock_order(request,item_id):
    item = Order_items.objects.get(pk=item_id)
    if item.is_active == True:
        item.is_active = False
    else:
        item.is_active = True     
    item.save()
    return redirect(view_orders)




@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def delete_brand_offer(request,offer_id):
    brand_offer = Brand_offer.objects.get(pk=offer_id)
    brand_offer.delete()
    return redirect(view_brand_offers)



@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def delete_product_offer(request,offer_id):
    product_offer = Product_offer.objects.get(pk=offer_id)
    product_offer.delete()
    return redirect(view_product_offers)



@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def delete_coupon(request,coupon_id):
    coupon = Coupon.objects.get(pk=coupon_id)
    coupon.delete()
    return redirect(list_coupons)




@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def list_coupons(request):
    coupons = Coupon.objects.all()
    return render(request,'admin/coupons_list.html',{'coupons':coupons})


def get_filtered_sales(filter_type):
    if filter_type == 'daily':
        return Order_items.objects.filter(order__order_date=date.today(), status = 'delivered')
    elif filter_type == 'weekly':
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_end = week_start + timedelta(days=6)
        return Order_items.objects.filter(order__order_date__gte=week_start, order__order_date__lte=week_end, status = 'delivered')
    elif filter_type == 'monthly':
        return Order_items.objects.filter(order__order_date__month=date.today().month, status = 'delivered')
    elif filter_type == 'yearly':
        return Order_items.objects.filter(order__order_date__year=date.today().year, status = 'delivered')


@login_required(login_url='admin_signin')
@user_passes_test(is_staff, login_url='/') 
def sales_report(request):
    filter_type = request.GET.get('filter_type', 'weekly')
    
    # Initialize order_items to avoid UnboundLocalError
    order_items = get_filtered_sales(filter_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Handle AJAX requests for filtered sales data
        if filter_type == 'daily':
            order_items = Order_items.objects.filter(order__order_date=date.today(), status = 'delivered')
        elif filter_type == 'weekly':
            week_start = date.today() - timedelta(days=date.today().weekday())
            week_end = week_start + timedelta(days=6)
            order_items = Order_items.objects.filter(order__order_date__gte=week_start, order__order_date__lte=week_end, status = 'delivered')
        elif filter_type == 'monthly':
            order_items = Order_items.objects.filter(order__order_date__month=date.today().month, status = 'delivered')
        elif filter_type == 'yearly':
            order_items = Order_items.objects.filter(order__order_date__year=date.today().year, status = 'delivered')

        total_sales = sum([item.price for item in order_items])
        total_discount = sum([item.order.discount for item in order_items])  # Assuming there is a 'discount' field
        total_orders = order_items.count()
        
                
        data = {
            'order_items': list(order_items.values(
                'order__order_date',
                'id',
                'order__delivery_address__name',
                'status',
                'price',
                'unit_price',
                'quantity',
                'order__pyment_status',
                'order__id',
                'order__coupon_usage__coupon__code'
            )),
            
            'total_sales': total_sales,
            'total_discount': total_discount,
            'total_orders': total_orders,
        }
        return JsonResponse(data)

    # Handle non-AJAX request (normal page rendering)
    if filter_type == 'daily':
        order_items = Order_items.objects.filter(order__order_date=date.today(), status = 'delivered')
    elif filter_type == 'weekly':
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_end = week_start + timedelta(days=6)
        order_items = Order_items.objects.filter(order__order_date__gte=week_start, order__order_date__lte=week_end, status = 'delivered')
    elif filter_type == 'monthly':
        order_items = Order_items.objects.filter(order__order_date__month=date.today().month, status = 'delivered')
    elif filter_type == 'yearly':
        order_items = Order_items.objects.filter(order__order_date__year=date.today().year, status = 'delivered')

    coupon_usages = Coupon_usage.objects.all()
    coupon_usage_order_ides = [usage.order.id for usage in coupon_usages]

    context = {
        'order_items': order_items,
        'coupon_usage_order_ides': coupon_usage_order_ides,
        'coupon_usages': coupon_usages,
    }

    return render(request, 'admin/sales_report.html', context)




# def render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html = template.render(context_dict)
#     # result = HTML(string=html).write_pdf()
    
#     # response = HttpResponse(result, content_type='application/pdf')
#     # response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
#     # return response

def download_pdf_report(request):
    filter_type = request.GET.get('filter_type', 'daily')
    order_items = get_filtered_sales(filter_type)

    # Convert queryset to list of dictionaries if needed
    order_items_list = [{
        'date': item.order.order_date,
        'id': item.id,
        'customer_name': item.order.delivery_address.name,
        'payment': item.price,
        'discount': item.order.discount,
        'quantity': item.quantity
    } for item in order_items]

    total_sales = sum([item['payment'] for item in order_items_list])
    total_discount = sum([item.get('discount', 0) for item in order_items_list])  # Adjust based on your data
    total_orders = len(order_items_list)

    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()

    # Create a SimpleDocTemplate object to generate the PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    heading_style = ParagraphStyle(
    name="HeadingStyle",
    fontSize=18,
    alignment=TA_CENTER,
    textColor=HexColor("#124E66"),
    spaceAfter=20  
    
    )

    heading = Paragraph("PhonoPedia", heading_style)

    elements = [heading]

    # Define the table data
    data = [
        ['Date', 'ID', 'Customer Name', 'Payment', 'discount', 'Quantity']  # Table headers
    ]

    for item in order_items_list:
        data.append([
            item['date'],
            item['id'],
            item['customer_name'],
            f"${item['payment']:.2f}",
            item['discount'],
            item['quantity']
        ])

    # Create a Table object
    table = Table(data)

    # Define table styles
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONT', (0, 1), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (0, 1), (-1, -1), '#f9f9f9'),
    ])
    table.setStyle(style)

    # Add the table to the elements list
    elements.append(table)
    styles = getSampleStyleSheet()
    # Add summary information to the elements list
    elements.append(Paragraph(f"Total Sales: ${total_sales:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total Discount: ${total_discount:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total Orders: {total_orders}", styles['Normal']))

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)

    # Create the HTTP response with the PDF content
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response

def download_excel_report(request):
    filter_type = request.GET.get('filter_type', 'daily')
    order_items = get_filtered_sales(filter_type)
    # Logic to fetch filtered data
    order_items_list = list(order_items.values('order__order_date', 'id', 'order__delivery_address__name', 'status', 'price', 'unit_price', 'quantity'))

    df = pd.DataFrame(order_items_list)
    
    for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']):
        df[col] = df[col].dt.tz_localize(None) 
    
    if 'datetime_column' in df.columns:
        df['datetime_column'] = df['datetime_column'].dt.tz_localize(None)
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    
    df.to_excel(response, index=False)
    return response


def get_orders_data(request):
    time_range = request.GET.get('time_range', 'yearly')

    try:
        if time_range == 'daily':
            # Group by day for daily data
            start_date = now() - timedelta(days=1)
            orders = Orders.objects.filter(order_date__gte=start_date).annotate(
                date=TruncDay('order_date')
            ).values('date').annotate(total=Sum('total')).order_by('date')

        elif time_range == 'weekly':
            start_date = now() - timedelta(weeks=1)
            print('week = ',start_date)
            orders = Orders.objects.filter(order_date__gte=start_date).annotate(
                date=TruncDay('order_date')
            ).values('date').annotate(total=Sum('total')).order_by('date')
            
            
        elif time_range == 'monthly':
            start_date = now() - timedelta(days=30)
            print('monthly',start_date)
            orders = Orders.objects.filter(order_date__gte=start_date).annotate(
                date=TruncWeek('order_date')
            ).values('date').annotate(total=Sum('total')).order_by('date')
            

        elif time_range == 'yearly':
            start_date = now() - timedelta(days=365)
            print('yearly',start_date)
            orders = Orders.objects.filter(order_date__gte=start_date).annotate(
                date=TruncMonth('order_date')
            ).values('date').annotate(total=Sum('total')).order_by('date')
            

        
        data = {
            'labels': [order.get('date').strftime('%Y-%m-%d') for order in orders],
            'totals': [order['total'] for order in orders]
        }

        return JsonResponse(data)

    except Exception as e:
        # Return an error response in case something goes wrong
        return JsonResponse({'error': str(e)}, status=500)