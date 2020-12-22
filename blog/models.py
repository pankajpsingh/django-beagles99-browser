from __future__ import unicode_literals

import string
from bs4 import BeautifulSoup
from django.contrib import messages
from django.db import models
from django.dispatch import receiver
from django.shortcuts import redirect, render

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TagBase, ItemBase

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.core.signals import page_published
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.api import APIField
from grapple.models import GraphQLString, GraphQLStreamfield
from home.blocks import BaseStreamBlock


class BlogPeopleRelationship(Orderable, models.Model):
    """
    This defines the relationship between the `People` within the `home`
    app and the BlogPage below. This allows People to be added to a BlogPage.
    We have created a two way relationship between BlogPage and People using
    the ParentalKey and ForeignKey
    """
    page = ParentalKey('BlogPage', related_name='blog_authors', on_delete=models.CASCADE)
    people = models.ForeignKey('home.People', related_name='blog_posts', on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel('people')
    ]


class BlogTag(TagBase):
    class Meta:
        verbose_name = "blog tag"
        verbose_name_plural = "blog tags"


class TaggedBlog(ItemBase):
    tag = models.ForeignKey(BlogTag, related_name="tagged_blogs", on_delete=models.CASCADE)
    content_object = ParentalKey(to='BlogPage', on_delete=models.CASCADE, related_name='all_blog_tags')


class BlogPage(Page):
    """
    We access the People object with an inline panel that references the
    ParentalKey's related_name in BlogPeopleRelationship. More docs:
    http://docs.wagtail.io/en/latest/topics/pages.html#inline-models
    """
    introduction = models.TextField(help_text='Text to describe the page', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    blog_tags = ClusterTaggableManager(through=TaggedBlog, blank=True)
    date_published = models.DateField("Date article published", blank=True, null=True)
    body_word_count = models.PositiveIntegerField(null=True, editable=False)
    canonical_url = models.URLField(blank=True, max_length=255, null=True, )

    linked_products = models.ManyToManyField('product.ProductPage', )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle', classname="full"),
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        FieldPanel('date_published'),
        InlinePanel('blog_authors', label="Author(s)", panels=None, min_num=1),
        FieldPanel('blog_tags'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('canonical_url'),
    ]

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
        authors = [n.people for n in self.blog_authors.all()]
        return authors

    def set_body_word_count(self):
        body_basic_html = self.body.stream_block.render_basic(self.body)
        body_text = BeautifulSoup(body_basic_html, 'html.parser').get_text()
        remove_chars = string.punctuation + '“”’'
        body_words = body_text.translate(body_text.maketrans(dict.fromkeys(remove_chars))).split()
        self.body_word_count = len(body_words)

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.blog_tags.all()
        for tag in tags:
            tag.url = '/' + '/'.join(s.strip('/') for s in [self.get_parent().url, 'blog-tags', tag.slug])
        return tags

    # Specifies parent to BlogPage as being BlogIndexPages
    parent_page_types = ['BlogIndexPage']

    # Specifies what content types can exist as children of BlogPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []


class BlogIndexPage(RoutablePageMixin, Page):
    """
    We need to alter the page model's context to return the child page objects,
    the BlogPage objects, so that it works as an index page
    RoutablePageMixin is used to allow for a custom sub-URL for the blog-tag views defined above.
    """
    introduction = models.TextField(help_text='Blog Introduction', blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', help_text='Landscape mode only; horizontal width between 1000px and 3000px.')

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
    ]

    subpage_types = ['BlogPage']

    api_fields = [
        APIField('introduction'),
        APIField('image'),
        # APIField('authors'),  # This will nest the relevant BlogPageAuthor objects in the API response
    ]

    graphql_fields = [
        GraphQLString("introduction"),
    ]

    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # http://docs.wagtail.io/en/latest/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        context['posts'] = BlogPage.objects.descendant_of(self).live().order_by('-date_published')
        return context

    # This defines a Custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the BlogIndexPage.
    # More information on RoutablePages is at
    # http://docs.wagtail.io/en/latest/reference/contrib/routablepage.html
    @route(r'^blog-tags/$', name='blog_tag_archive')
    @route(r'^blog-tags/([\w-]+)/$', name='blog_tag_archive')
    def blog_tag_archive(self, request, tag=None):
        try:
            tag = BlogTag.objects.get(slug=tag)
        except BlogTag.DoesNotExist:
            if tag:
                msg = 'There are no blog posts tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {
            'tag': tag,
            'posts': posts
        }
        return render(request, 'blog/blog_index_page.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child BlogPage objects for this BlogPageIndex.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = BlogPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(blog_tags=tag)
        return posts

    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            # Not tags.append() because we don't want a list of lists
            tags += post.get_tags
        tags = sorted(set(tags))
        return tags


@receiver(page_published, sender=BlogPage)
def update_body_word_count_on_page_publish(instance, **kwargs):
    instance.set_body_word_count()
    instance.save(update_fields=['body_word_count'])