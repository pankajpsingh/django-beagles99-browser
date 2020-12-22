from django import forms
from django.utils.translation import gettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm


class CustomUserEditForm(UserEditForm):
    country = forms.CharField(required=True, label=_("Country"))


class CustomUserCreationForm(UserCreationForm):
    country = forms.CharField(required=True, label=_("Country"))
