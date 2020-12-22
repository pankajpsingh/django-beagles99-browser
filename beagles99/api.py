from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from users.endpoints import UsersAPIViewSet
from wagtail_nav_menus.viewsets import NavMenuViewSet
from django.urls import path


class MyNavMenuViewSet(NavMenuViewSet):
    """
    Our custom Pages API endpoint that allows finding pages by pk or slug
    """

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path('', cls.as_view({'get': 'list'}), name='listing'),
            path('<int:pk>/', cls.as_view({'get': 'retrieve'}), name='detail'),
        ]


# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)
api_router.register_endpoint('users', UsersAPIViewSet)
api_router.register_endpoint('menus', MyNavMenuViewSet)



