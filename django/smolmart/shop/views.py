from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, CartItem, Order, OrderItem

def home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', '')
    page_number = request.GET.get('page', 1)

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category_id:
        products = products.filter(category__id=category_id)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:    
        products = products.filter(price__lte=max_price)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
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
            return redirect('home')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials'})
    return render(request, 'shop/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

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
    
    messages.success(request, f"{product.name} added to cart.")
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
            'message': f"{product.name} added to cart.",
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

    if request.method == "POST":
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("view_cart")

        order = Order.objects.create(user=request.user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect("purchase_success")

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total": total,
    })

@login_required
def purchase_success(request):
    return render(request, "shop/purchase_success.html")


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    context = {'orders': orders}
    return render(request, "shop/order_history.html", context)

# Create your views here.
