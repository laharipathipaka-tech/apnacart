from django.contrib import admin
from .models import Product, CartItem, Order, UserBudget, GroupBuying


# =========================
# PRODUCT ADMIN
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    list_filter = ('price',)


# =========================
# CART ITEM ADMIN
# =========================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user',)
    search_fields = ('product__name',)


# =========================
# ORDER ADMIN (VERY IMPORTANT)
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


# =========================
# USER BUDGET ADMIN
# =========================
@admin.register(UserBudget)
class UserBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'monthly_limit')
    search_fields = ('user__username',)


# =========================
# GROUP BUYING ADMIN
# =========================
@admin.register(GroupBuying)
class GroupBuyingAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'original_price',
        'current_price',
        'minimum_group_size',
        'current_group_size',
        'created_at',
    )
    readonly_fields = ('created_at',)
