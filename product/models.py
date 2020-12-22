import datetime
from decimal import Decimal
# from django.contrib import messages
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TagBase, ItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager

# from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.api import APIField
from grapple.models import GraphQLString, GraphQLStreamfield
from home.blocks import BaseStreamBlock


class ProductTag(TagBase):
    class Meta:
        verbose_name = "product tag"
        verbose_name_plural = "product tags"


class TaggedProduct(ItemBase):
    tag = models.ForeignKey(ProductTag, related_name="tagged_products", on_delete=models.CASCADE)
    content_object = ParentalKey(to='ProductPage', on_delete=models.CASCADE, related_name='all_product_tags')


class ProductPage(Page):
    uid_or_isbn = models.CharField('UID or ISBN', max_length=13, )
    subtitle = models.CharField('Sub title',blank=True, max_length=255)
    introduction = models.TextField('Introduction', help_text='Product Intro', blank=True, null=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    body = StreamField(BaseStreamBlock(), verbose_name="Product Page body", blank=True, null=True)
    date_published = models.DateField("Date of Publication", blank=True, null=True)
    product_tags = ClusterTaggableManager(through=TaggedProduct, blank=True)
    curr = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1)
    list_price = models.DecimalField('List Price', max_digits=10, decimal_places=2, default='0.00')
    discount = models.DecimalField('Discount', max_digits=4, decimal_places=2, default='0.00')
    qty_in_stock = models.DecimalField('Qty in Stock', max_digits=8, decimal_places=2, default='0.00')
    remarks = models.CharField('Remarks', null=True, blank=True, max_length=255)
#     linked_products = models.ManyToManyField('product.ProductPage', null=True, blank=True, related_name='other_linked_products')

    content_panels = Page.content_panels + [
        FieldPanel('uid_or_isbn', classname="full"),
        FieldPanel('subtitle', classname="full"),
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        FieldPanel('date_published'),
        FieldPanel('product_tags'),
        FieldPanel('list_price'),
        FieldPanel('discount'),
        FieldPanel('qty_in_stock'),
        FieldPanel('remarks'),
#         PageChooserPanel('linked_products'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('uid_or_isbn'),
        index.SearchField('subtitle'),
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]

    api_fields = [
        APIField('uid_or_isbn'),
        APIField('subtitle'),
        APIField('introduction'),
        APIField('date_published'),
        APIField('body'),
        APIField('image'),
        APIField('product_tags'),
        APIField('list_price'),
        APIField('discount'),
        APIField('qty_in_stock'),
        APIField('remarks'),
#        APIField('linked_products'),
    ]

    graphql_fields = [
        GraphQLString("subtitle"),
        GraphQLString("introduction"),
        GraphQLString("date_published"),
        GraphQLStreamfield("body"),
        # GraphQLString("author"),
    ]

    parent_page_types = ['ProductIndexPage']
    subpage_types = []


class ProductIndexPage(Page):
    """
    Index page for Br Dictionaries.
    We need to alter the page model's context to return the child page objects,
    the DictPage objects, so that it works as an index page
    """
    introduction = models.TextField(help_text='List of Products', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
    ]
    subpage_types = ['ProductPage']

    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(ProductIndexPage, self).get_context(request)
        context['dicts'] = ProductPage.objects.descendant_of(
            self).live().order_by('-date_published')
        return context

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    def get_dicts(self):
        return ProductPage.objects.live().descendant_of(self)


class BookPage(ProductPage):
    imprint = models.CharField('Publisher Imprint', max_length=254, null=True, blank=True,)
    format = models.ForeignKey("BookFormat", related_name='format_titles', null=True, blank=True,
                               on_delete=models.SET_NULL)
    language = models.ForeignKey("Language", null=True, blank=True, related_name='lang_titles',
                                 on_delete=models.SET_NULL)
    own_pub = models.BooleanField("Own Publication", default=False)
    book_pages = models.PositiveSmallIntegerField('Number of Pages', null=True, blank=True)
    year_of_pub = models.IntegerField('Year of Publication', choices=zip(range(1900, 2050), range(1900, 2050)),
                                      default=int(datetime.date.today().year))

    # authors = models.ManyToManyField('BookAuthorPage', blank=True, null=True, related_name='author_titles', )
    # subjects = models.ManyToManyField('BookSubjectPage', blank=True, null=True, related_name='subject_titles', )

    parent_page_types = ['BookIndexPage']

    content_panels = ProductPage.content_panels + [
        FieldPanel('imprint'),
        SnippetChooserPanel('format'),
        SnippetChooserPanel('language'),
        FieldPanel('own_pub'),
        FieldPanel('book_pages'),
        FieldPanel('year_of_pub'),
 #       FieldPanel('authors'),
  #      FieldPanel('subjects'),
    ]

    search_fields = ProductPage.search_fields + [
  #      index.SearchField('authors'),
   #     index.SearchField('subjects'),
    ]

    api_fields = ProductPage.api_fields +[
        APIField('imprint'),
        APIField('format'),
        APIField('language'),
        APIField('own_pub'),
        APIField('book_pages'),
        APIField('year_of_pub'),
#        APIField('authors'),
#        APIField('subjects'),
    ]

class BookIndexPage(ProductIndexPage):
    subpage_types = ['BookPage']


class BookAuthorPage(Page):
    person = ParentalKey('home.People', on_delete=models.PROTECT, related_name='book_authors')


class BookSubjectPage(Page):
    subpage_types = ['BookPage']


@register_snippet
class BookFormat(models.Model):
    name = models.CharField('Format', max_length=99)

    class Meta:
        verbose_name = 'Book Format'
        verbose_name_plural = 'Book Formats'

    def __str__(self):
        return self.name


@register_snippet
class Language(models.Model):
    name = models.CharField('Language', max_length=99)

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        return self.name


