from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ExchangeRate


@receiver(post_save, sender=ExchangeRate)
def update_exchange_rate_1(sender, instance, created, **kwargs):
    instance.curr._set_curr_rate()


@receiver(post_delete, sender=ExchangeRate)
def update_exchange_rate_2(sender, instance, **kwargs):
    instance.curr._set_curr_rate()






