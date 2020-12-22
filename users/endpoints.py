from wagtail.api.v2.views import BaseAPIViewSet
from users.models import User


class UsersAPIViewSet(BaseAPIViewSet):

    model = User
    body_fields = BaseAPIViewSet.body_fields + ['username', 'email', 'country', ]
    listing_default_fields = BaseAPIViewSet.listing_default_fields + ['username', 'email', 'country', ]