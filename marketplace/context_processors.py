from .models import Cart, Tax
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        cart_items = Cart.objects.filter(session_key=session_key)

    for cart_item in cart_items:
        cart_count += cart_item.quantity

    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        cart_items = Cart.objects.filter(session_key=session_key)

    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.id)
        subtotal += (fooditem.price * item.quantity)

    get_tax = Tax.objects.filter(is_active=True)
    for i in get_tax:
        tax_type = i.tax_type
        tax_percentage = i.tax_percentage
        tax_amount = round((tax_percentage * subtotal) / 100, 2)
        tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

    tax = sum(x for key in tax_dict.values() for x in key.values())
    grand_total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
