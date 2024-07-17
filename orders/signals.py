from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    if created:
        # Order created
        message = f"A new order {instance.order_number} has been placed!"
        notify_users_and_vendors(message)
    else:
        # Order updated
        message = f"The status of order {instance.order_number} has been updated to {instance.status}"
        notify_users_and_vendors(message)

def notify_users_and_vendors(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',
        {
            'type': 'send_notification',
            'message': message
        }
    )
