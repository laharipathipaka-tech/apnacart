from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.utils.timezone import now

from .models import Product, CartItem, UserBudget, GroupBuying, Order


# =========================
# HOME + SEARCH
# =========================
def home(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q)
    return render(request, 'store/home.html', {'products': products})


# =========================
# REGISTER
# =========================
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()  # ✅ password is hashed properly
            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()

    return render(request, 'store/register.html', {'form': form})

# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'store/login.html')


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# =========================
# ADD TO CART
# =========================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        item.quantity += 1

    item.save()
    messages.success(request, "Product added to cart")
    return redirect('cart')


# =========================
# CART
# =========================
@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })


# =========================
# INCREASE CART ITEM
# =========================
@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')


# =========================
# DECREASE CART ITEM
# =========================
@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')


# =========================
# REMOVE CART ITEM
# =========================
@login_required
def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart")
    return redirect('cart')


# =========================
# CHECKOUT + BUDGET LIMIT
# =========================
@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    budget, _ = UserBudget.objects.get_or_create(
        user=request.user,
        defaults={'monthly_limit': 10000}
    )

    # Monthly spent (orders)
    month_start = now().replace(day=1)
    spent = Order.objects.filter(
        user=request.user,
        created_at__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    if spent + total > budget.monthly_limit:
        messages.error(request, "⚠ You are exceeding your monthly budget!")

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total,
        'limit': budget.monthly_limit,
        'spent': spent,
        'remaining': budget.monthly_limit - spent
    })


# =========================
# GROUP BUYING
# =========================
@login_required
def join_group(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    group, _ = GroupBuying.objects.get_or_create(
        product=product,
        defaults={
            'original_price': product.price,
            'current_price': product.price,
            'minimum_group_size': 3,
            'current_group_size': 0
        }
    )

    group.current_group_size += 1

    if group.current_group_size >= group.minimum_group_size:
        group.current_price = group.original_price * 0.9  # 10% discount

    group.save()
    messages.success(request, "You joined the group buying deal!")

    return redirect('home')
