from urllib import response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from menu.models import FoodItem
from .forms import OrderForm
from .models import Order, OrderedFood, Payment

import simplejson as json

from .utils import generate_order_number, order_total_by_vendor
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site

from .forms import FeedbackForm, GuestOrderForm
from .models import Feedback

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render



@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)

    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal
    
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = OrderForm(request.POST)
        else:
            form = GuestOrderForm(request.POST)
        
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    else:
        form = OrderForm() if request.user.is_authenticated else GuestOrderForm()

    return render(request, 'orders/place_order.html', {'form': form, 'cart_items': cart_items})


def send_push_notification(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',
        {
            'type': 'send_notification',
            'message': message
        }
    )


@login_required(login_url='login')
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number) if request.user.is_authenticated else Order.objects.get(order_number=order_number)
        payment = Payment(
            user = request.user if request.user.is_authenticated else None,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood(
                order=order,
                payment=payment,
                user=request.user if request.user.is_authenticated else None,
                fooditem=item.fooditem,
                quantity=item.quantity,
                price=item.fooditem.price,
                amount=item.fooditem.price * item.quantity
            )
            ordered_food.save()

        mail_subject = 'Thank you for ordering with us.'
        mail_template = 'orders/order_confirmation_email.html'

        ordered_food = OrderedFood.objects.filter(order=order)
        student_subtotal = sum(item.price * item.quantity for item in ordered_food)
        tax_data = json.loads(order.tax_data)
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
            'ordered_food': ordered_food,
            'domain': get_current_site(request),
            'student_subtotal': student_subtotal,
            'tax_data': tax_data,
        }
        send_notification(mail_subject, mail_template, context)

        mail_subject = 'You have received a new order.'
        mail_template = 'orders/new_order_received.html'
        to_emails = set(item.fooditem.vendor.user.email for item in cart_items)
        
        for email in to_emails:
            ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor__user__email=email)
            vendor_id = ordered_food_to_vendor.first().fooditem.vendor.id if ordered_food_to_vendor else None
            context = {
                'order': order,
                'to_email': email,
                'ordered_food_to_vendor': ordered_food_to_vendor,
                'vendor_subtotal': order_total_by_vendor(order, vendor_id)['subtotal'],
                'tax_data': order_total_by_vendor(order, vendor_id)['tax_dict'],
                'vendor_grand_total': order_total_by_vendor(order, vendor_id)['grand_total'],
            }
            send_notification(mail_subject, mail_template, context)

        cart_items.delete()

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('Payments view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        print(tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
    

@login_required(login_url='login')
def submit_feedback(request, order_id, food_item_id):
    order = Order.objects.get(id=order_id, user=request.user)
    food_item = FoodItem.objects.get(id=food_item_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.order = order
            feedback.food_item = food_item
            feedback.save()
            return redirect('order_complete', order_no=order.order_number, trans_id=order.payment.transaction_id)
    else:
        form = FeedbackForm(initial={'food_item': food_item})

    context = {
        'form': form,
        'food_item': food_item,
    }
    return render(request, 'orders/submit_feedback.html', context)

@login_required(login_url='login')
def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = request.POST['status']
    order.save()
    send_push_notification(f"The status of order {order.order_number} has been updated to {order.status}")