from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F
from .models import Product, Category, CartItem, Order, OrderItem, Favourite, Game
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
import json
import random
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def landing_page(request):
    games = Game.objects.all()
    random_skins = list(Product.objects.all())
    random.shuffle(random_skins)
    random_skins = random_skins[:20]

    context = {
        'games': games,
        'random_skins': random_skins,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'shop/index.html', context)

def home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', '')
    page_number = request.GET.get('page', 1)

    products = Product.objects.all().order_by('id')
    categories = Category.objects.all()

    champions = Product.objects.values_list('champion_name', flat=True).distinct().order_by('champion_name')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(champion_name__icontains=query) |
            Q(skin_name__icontains=query) |
            Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(category__id=category_id)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:    
        products = products.filter(price__lte=max_price)

    champion_filter = request.GET.get('champion', '')
    if champion_filter:
        products = products.filter(champion_name=champion_filter)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    paginator = Paginator(products, 25)
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        fav_ids = set(Favourite.objects.filter(user=request.user).values_list('product_id', flat=True))
        for p in page_obj:
            p.is_favourited = p.id in fav_ids
    else:
        for p in page_obj:
            p.is_favourited = False

    context = {
        'products': page_obj,
        'categories': categories,
        'champions': champions,
        'query': query,
        'category_id': category_id,
        'sort': sort_by,
        'page_obj': page_obj,
    } 

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('shop/products_list.html', context, request=request)
        pagination_html = render_to_string('shop/pagination.html', context, request=request)
        return JsonResponse({'html': html, 'pagination': pagination_html})

    return render(request, 'shop/home.html', context)

def user_register(request):
    if request.method =='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'shop/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'shop/register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'shop/register.html', {'error': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created ! You are logged in now')
        return redirect('login')
    
    return render(request, 'shop/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials'})
    return render(request, 'shop/login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum([item.subtotal() for item in cart_items])
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} カートに追加しました.")
    return redirect('view_cart')

@login_required
def add_to_cart_ajax(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': f"{product.name} カートに追加しました。",
            'cart_count': CartItem.objects.filter(user=request.user).count()
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    context = {
        "cart_items": cart_items,
        "total": total,
        "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY, 
    }

    return render(request, "shop/checkout.html", context)

@login_required
def purchase_success(request):
    return render(request, "shop/purchase_success.html")


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    context = {'orders': orders}
    return render(request, "shop/order_history.html", context)

@login_required
def toggle_favourite(request, product_id):
    product = Product.objects.get(id=product_id)
    fav, created = Favourite.objects.get_or_create(
        user=request.user, 
        product=product
    )

    if not created:
        fav.delete()

    return JsonResponse({'status': 'ok'})

@login_required
def account(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    favourites = Product.objects.filter(favourite__user=request.user)

    return render(request, 'shop/account.html', {
        'orders': orders, 
        'favourites': favourites
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    is_favourited = False
    if request.user.is_authenticated:
        is_favourited = Favourite.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'is_favourited': is_favourited
    }
    return render(request, 'shop/item_detail.html', context)

@login_required
def create_payment_intent(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items) 
    if total == 0:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    intent = stripe.PaymentIntent.create(
        amount=int(total), 
        currency='jpy',
        automatic_payment_methods={'enabled': True},
        metadata={
            "user_id": request.user.id
        }
    )

    return JsonResponse({
        'clientSecret': intent.client_secret
    })

def send_order_confirmation_email(user, order):
    subject = f"Order Confirmation - #{order.user_order_number}"
    html_message = render_to_string('shop/email/order_confirmation.html', {
        'user': user,
        'order': order
    })

    # Tentuin penerima berdasarkan developer mode
    if getattr(settings, 'DEVELOPER_MODE', False):
        recipient = [getattr(settings, 'DEVELOPER_EMAIL')]
    else:
        recipient = [user.email]

    email = EmailMessage(
        subject,
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        recipient,
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        user_id = payment_intent['metadata'].get('user_id')
        if not user_id:
            return HttpResponse(status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(status=400)

        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return HttpResponse(status=200)

        total = sum(item.subtotal() for item in cart_items)

        with transaction.atomic():
            order = Order.objects.create(user=user, total=total)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart_items.delete()

            send_order_confirmation_email(user, order)

    return HttpResponse(status=200)


# Create your views here.
