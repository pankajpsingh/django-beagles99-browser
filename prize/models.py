# from django.contrib import messages
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TagBase, ItemBase

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.api import APIField
from grapple.models import GraphQLString, GraphQLStreamfield
from home.blocks import BaseStreamBlock


@register_snippet
class PrizeWinner(Orderable, models.Model):
    """
    """
    page = ParentalKey('PrizePage', related_name='prize_winners', on_delete=models.CASCADE)
    winner = models.ForeignKey('home.People', related_name='prizes', on_delete=models.CASCADE)
    year = models.SmallIntegerField()
    book = ParentalKey('product.BookPage', related_name='has_prizes', on_delete=models.CASCADE)
    citation = models.TextField('Citation', null=True, blank=True)
    side_note = models.TextField('Side Note', null=True, blank=True)

    panels = [
        SnippetChooserPanel('people'),
        SnippetChooserPanel('prize'),
    ]


class PrizeTag(TagBase):
    class Meta:
        verbose_name = "prize tag"
        verbose_name_plural = "prize tags"


class TaggedPrize(ItemBase):
    tag = models.ForeignKey(PrizeTag, related_name="tagged_prizes", on_delete=models.CASCADE)
    content_object = ParentalKey(to='PrizePage', on_delete=models.CASCADE, related_name='all_prize_tags')


class PrizePage(Page):
    introduction = models.TextField(help_text='Prize Home', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    body = StreamField(BaseStreamBlock(), verbose_name="Prize Page body", blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    dict_word_count = models.PositiveIntegerField(null=True, editable=False)
    prize_tags = ClusterTaggableManager(through=TaggedPrize, blank=True)
    date_published = models.DateField("Updated on", blank=True, null=True)

    linked_products = models.ManyToManyField('product.ProductPage', )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle', classname="full"),
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        FieldPanel('date_published'),
        FieldPanel('prize_tags'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    api_fields = [
        APIField('introduction'),
        APIField('body'),
        APIField('image'),
        APIField('date_published'),
    ]

    graphql_fields = [
        GraphQLString("introduction"),
        GraphQLStreamfield("body"),
        GraphQLStreamfield("date_published"),
    ]

    parent_page_types = ['PrizeIndexPage']
    subpage_types = []


class PrizeIndexPage(Page):
    """
    Index page for Br Dictionaries.
    We need to alter the page model's context to return the child page objects,
    the DictPage objects, so that it works as an index page
    """
    introduction = models.TextField(help_text='List of Prizes', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    description = StreamField(BaseStreamBlock(), verbose_name="Description", blank=True)
    date_published = models.DateField("Updated on", blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('description'),
        FieldPanel('date_published'),
    ]
    subpage_types = ['PrizePage', ]

    search_fields = Page.search_fields + [
        index.SearchField('description'),
    ]

    api_fields = [
        APIField('introduction'),
        APIField('date_published'),
        APIField('description'),
        APIField('image'),
        # APIField('authors'),  # This will nest the relevant BlogPageAuthor objects in the API response
    ]

    graphql_fields = [
        GraphQLString("introduction"),
        GraphQLString("date_published"),
        GraphQLStreamfield("description"),
        # GraphQLString("author"),
    ]
    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(PrizeIndexPage, self).get_context(request)
        context['prizes'] = PrizePage.objects.descendant_of(self).live().order_by('-date_published')
        return context

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    def get_prizes(self):
        return PrizePage.objects.live().descendant_of(self)

