# from django.contrib import messages
from decimal import Decimal
import datetime
from django.db import models
from wagtail.snippets.models import register_snippet


@register_snippet
class Currency(models.Model):
    curr_code = models.CharField('Currency Code', max_length=3, unique=True)
    curr_name = models.CharField('Currency Name', max_length=15, blank=True, null=True)
    curr_symbol = models.CharField('Currency Symbol', max_length=10, blank=True, null=True)
    curr_rate = models.DecimalField('Exchange Rate', max_digits=6, decimal_places=2, default=Decimal('1.00'))

    class Meta:
        get_latest_by = 'curr_code'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def _set_curr_rate(self):
        rset = ExchangeRate.objects.filter(curr__curr_code=self.curr_code, applicable=True)
        self.curr_rate = rset[0].exchange_rate if rset else Decimal('0.00')
        self.save()
        return

    def __str__(self):
        return self.curr_code


@register_snippet
class ExchangeRate(models.Model):
    """
    Conversion Rates Applicable
    """
    curr = models.ForeignKey('Currency', verbose_name='Currency', on_delete=models.CASCADE)
    exchange_rate = models.DecimalField('Exchange Rate', max_digits=6, decimal_places=2, default=Decimal('1.00'))
    effective_date = models.DateField('Effective Date', default=datetime.date.today, )
    applicable = models.BooleanField('Applicable Rate', default=True)

    class Meta:
        ordering = ['-effective_date']
        get_latest_by = 'effective_date'
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'

    def __str__(self):
        display = self.curr.curr_code + ' = ' + str(self.exchange_rate) + ' w.e.f. ' + str(self.effective_date)
        if self.applicable:
            display = display + ' currently applicable.'
        return display
