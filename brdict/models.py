# from django.contrib import messages
from django.db import models
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

# from wagtail.contrib.routable_page.models import RoutablePageMixin, route
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
class DictEntry(index.Indexed, ClusterableModel):
    en_title = models.CharField('Entry', max_length=255, blank=True)
    en_desc = models.TextField('Description', blank=True, null=True)
    en_notes = models.TextField('Notes and Sources', null=True, blank=True)
    en_created = models.DateTimeField('Created', auto_now_add=True)
    en_updated = models.DateTimeField('Last Updated', auto_now=True)

@register_snippet
class DictEntryM2M(Orderable, models.Model):
    """
    """
    page = ParentalKey('DictPage', related_name='dict_entries', on_delete=models.CASCADE)
    entry = models.ForeignKey('DictEntry', related_name='dictionaries', on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel('entry')
    ]


class DictPeopleRelationship(Orderable, models.Model):
    """
    This defines the relationship between the `People` within the `home`
    app and the DictPage below. This allows People to be added to a DictPage.
    """
    page = ParentalKey('DictPage', related_name='dict_person_relationship', on_delete=models.CASCADE)
    people = models.ForeignKey('home.People', related_name='person_dict_relationship', on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel('people')
    ]


class DictPage(Page):
    introduction = models.TextField(help_text='Dictionary Home', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    body = StreamField(BaseStreamBlock(), verbose_name="Dictionary Page body", blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    date_published = models.DateField("Date of Publication", blank=True, null=True)
    dict_word_count = models.PositiveIntegerField(null=True, editable=False)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle', classname="full"),
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        FieldPanel('date_published'),
        InlinePanel('dict_person_relationship', label="Author(s)", panels=None, min_num=1), ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    api_fields = [
        APIField('introduction'),
        APIField('date_published'),
        APIField('body'),
        APIField('image'),
        # APIField('authors'),  # This will nest the relevant BlogPageAuthor objects in the API response
    ]

    graphql_fields = [
        GraphQLString("introduction"),
        GraphQLString("date_published"),
        GraphQLStreamfield("body"),
        # GraphQLString("author"),
    ]

    def authors(self):
        """
        Returns the DictPage's related People.
        """
        authors = [n.people for n in self.dict_person_relationship.all()]
        return authors

    def set_body_word_count(self):
        pass

    parent_page_types = ['DictIndexPage']
    subpage_types = []


class DictIndexPage(Page):
    """
    Index page for Br Dictionaries.
    We need to alter the page model's context to return the child page objects,
    the DictPage objects, so that it works as an index page
    """
    introduction = models.TextField(help_text='List of Dictionaries', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
    ]
    subpage_types = ['DictPage']

    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(DictIndexPage, self).get_context(request)
        context['dicts'] = DictPage.objects.descendant_of(
            self).live().order_by('-date_published')
        return context

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    def get_dicts(self):
        return DictPage.objects.live().descendant_of(self)
