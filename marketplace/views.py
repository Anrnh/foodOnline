from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserProfile
from .context_processors import get_cart_counter, get_cart_amounts
from menu.models import Category, FoodItem

from vendor.models import Vendor, OpeningHour
from django.db.models import Prefetch
from .models import Cart, Tax
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from datetime import date, datetime
from orders.forms import OrderForm


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')
    
    # Check current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            fooditem = FoodItem.objects.get(id=food_id)
            if request.user.is_authenticated:
                user = request.user
                cart_item, created = Cart.objects.get_or_create(user=user, fooditem=fooditem)
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                session_key = request.session.session_key
                cart_item, created = Cart.objects.get_or_create(session_key=session_key, fooditem=fooditem)
                
            if not created:
                cart_item.quantity += 1
            else:
                cart_item.quantity = 1
            cart_item.save()

            return JsonResponse({'status': 'Success', 'message': 'Item added to cart', 'cart_counter': get_cart_counter(request), 'qty': cart_item.quantity, 'cart_amount': get_cart_amounts(request)})
        except FoodItem.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
    return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def decrease_cart(request, food_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            fooditem = FoodItem.objects.get(id=food_id)
            if request.user.is_authenticated:
                user = request.user
                cart_item = Cart.objects.get(user=user, fooditem=fooditem)
            else:
                session_key = request.session.session_key
                cart_item = Cart.objects.get(session_key=session_key, fooditem=fooditem)
            
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': cart_item.quantity, 'cart_amount': get_cart_amounts(request)})
        except FoodItem.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
    return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        cart_items = Cart.objects.filter(session_key=session_key).order_by('created_at')
        
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)



def delete_cart(request, cart_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            if request.user.is_authenticated:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
            else:
                session_key = request.session.session_key
                cart_item = Cart.objects.get(session_key=session_key, id=cart_id)
            
            if cart_item:
                cart_item.delete()
                return JsonResponse({'status': 'Success', 'message': 'Cart item has been deleted!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'Cart Item does not exist!'})
    return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

        
def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        keyword = request.GET['keyword']

        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        
        vendor_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)

def checkout(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_items = Cart.objects.filter(session_key=session_key).order_by('created_at')

    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        default_values = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone': request.user.userprofile.phone,
            'email': request.user.email,
            'address': user_profile.address,
            'country': user_profile.country,
            'state': user_profile.state,
            'city': user_profile.city,
            'poscode': user_profile.poscode,
        }
        form = OrderForm(initial=default_values)
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': sum(item.fooditem.price * item.quantity for item in cart_items),
        'tax_dict': get_tax_dict(cart_items),  # Assuming you have a function to calculate tax
        'grand_total': calculate_grand_total(cart_items)  # Assuming you have a function to calculate the grand total
    }
    return render(request, 'marketplace/checkout.html', context)

def get_tax_dict(cart_items):
    subtotal = sum(item.fooditem.price * item.quantity for item in cart_items)
    tax_dict = {}
    get_tax = Tax.objects.filter(is_active=True)
    for tax in get_tax:
        tax_amount = round((tax.tax_percentage * subtotal) / 100, 2)
        tax_dict[tax.tax_type] = {str(tax.tax_percentage): tax_amount}
    return tax_dict

def calculate_grand_total(cart_items):
    subtotal = sum(item.fooditem.price * item.quantity for item in cart_items)
    tax_dict = get_tax_dict(cart_items)
    tax_total = sum(tax_amount for tax in tax_dict.values() for tax_amount in tax.values())
    return subtotal + tax_total