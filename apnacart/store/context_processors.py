from .models import CartItem, UserBudget

def cart_and_budget(request):
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
        budget = UserBudget.objects.filter(user=request.user).first()
        budget_left = budget.monthly_limit if budget else 0
    else:
        cart_count = 0
        budget_left = 0

    return {
        'cart_count': cart_count,
        'budget_left': budget_left
    }
