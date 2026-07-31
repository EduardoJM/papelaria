from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.contrib.search_promotions.models import Query
from wagtailseo.models import SeoMixin, SeoType, TwitterCard

class ListIndexPage(Page):
    main_title = models.CharField("Título Principal", max_length=150)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Logo"
    )
    
    content_panels = Page.content_panels + [
        "main_title", "logo"
    ]

    def get_context(self, request):
        context = super().get_context(request)
        items = (
            self.get_children()
            .type(ListContentPage)
            .live()
            .order_by('-listcontentpage__date')
        )
        
        paginator = Paginator(items, 12)
        page = request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            items = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            items = paginator.page(paginator.num_pages)

        context['items'] = items
        return context

class ListContentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'ListContentPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class ListContentPage(SeoMixin, Page):
    date = models.DateField(verbose_name="Data")
    description = RichTextField(blank=True, verbose_name="Descrição")
    cover = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        verbose_name="Capa"
    )
    display_label = models.CharField("Label de Visualização", blank=True, default="")
    tags = ClusterTaggableManager(
        through=ListContentPageTag,
        blank=True,
        verbose_name='Tags'
    )

    content_panels = Page.content_panels + [
        "date",
        "description",
        "cover",
        "display_label",
        "tags",
        "properties",
        "images",
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description")
    ]
    
    # SEO
    promote_panels = SeoMixin.seo_panels
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE
    
    def get_context(self, request):
        context = super().get_context(request)
        comments = (
            self.get_children()
            .type(ListContentCommentPage)
            .live()
            .order_by('-listcontentpage__date')
        )
        context['comments'] = comments
        return context

class ListContentPageImage(Orderable):
    page = ParentalKey(ListContentPage, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = ["image", "caption"]

class ListContentPageProperties(Orderable):
    page = ParentalKey(ListContentPage, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=250)
    value = models.CharField(max_length=250)

    panels = ["name", "value"]

class ListContentSearchPage(Page):
    def get_context(self, request):
        context = super().get_context(request)

        search_query = request.GET.get('query', None)
        if search_query:
            search_results = (
                self.get_parent()
                .get_children()
                .type(ListContentPage)
                .live()
                .search(search_query)
            )
            # Log the query so Wagtail can suggest promoted results
            Query.get(search_query).add_hit()
        else:
            search_results = Page.objects.none()

        paginator = Paginator(search_results, 12)
        page = request.GET.get('page')
        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            search_results = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            search_results = paginator.page(paginator.num_pages)

        context['search_results'] = search_results
        context['search_query'] = search_query

        return context

class ListContentCommentPage(Page):
    comment = RichTextField(blank=True, verbose_name="Comentário")

    content_panels = Page.content_panels + ["comment"]

class ListTagContentsPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        site = self.get_site()
        root = site.root_page

        tag = request.GET.get('tag')
        if tag:
            items = (
                root
                .get_children()
                .type(ListContentPage)
                .live()
                .filter(listcontentpage__tags__name=tag)
                .order_by('-listcontentpage__date')
            )

            paginator = Paginator(items, 12)
            page = request.GET.get('page')
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                items = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                items = paginator.page(paginator.num_pages)

            context['items'] = items
        else:
            # TODO: render only tags used in the site here
            pass

        return context


class MenuLink(Page):
    page = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
        verbose_name="Página Interna",
        blank=True,
        null=True,
        related_name='links'
    )
    page_extra = models.CharField("Extra URL", max_length=250, blank=True, default="")
    external_link = models.URLField("Link Externo", blank=True, null=True)

    content_panels = Page.content_panels + ["page", "page_extra", "external_link"]

    @property
    def submenus(self):
        menus = (
            self.get_children()
            .type(MenuLink)
            .live()
        )
        return menus
