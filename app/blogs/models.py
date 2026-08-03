from django import forms
from django.db import models
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import MultiFieldPanel, FieldPanel
from wagtail.models import Page
from wagtail.search import index
from wagtail.fields import RichTextField
from wagtailseo.models import SeoMixin, SeoType, TwitterCard
from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField

class BlogIndexPage(SeoMixin, Page):
    BLOG_STYLES_CHOICES = (
        ("enterprise", "Enterprise"),
    )
    blog_style = models.CharField(
        verbose_name="Estilo",
        max_length=80,
        choices=BLOG_STYLES_CHOICES,
    )
    featured_posts_tag = models.CharField(
        verbose_name="Tag de posts principais",
        default='',
        max_length=250
    )
    featured_card_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        verbose_name="Capa do Card Principal",
        blank=True,
        null=True,
        default=None
    )
    featured_title = models.CharField(
        verbose_name='Título do Card Principal',
        max_length=250,
        blank=True,
        default=''
    )
    featured_subtitle = models.CharField(
        verbose_name='Subtítulo do Card Principal',
        max_length=250,
        blank=True,
        default=''
    )
    featured_link = models.URLField(
        verbose_name='Link do Card Principal',
        blank=True,
        default=''
    )

    content_panels = Page.content_panels + [
        "blog_style",
        "featured_posts_tag",
        "featured_title",
        "featured_card_image",
        "featured_subtitle",
        "featured_link",
    ]

    # SEO
    promote_panels = SeoMixin.seo_panels
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE
    
    def get_template(self, request, *args, **kwargs):
        return "blogs/%s/%s.html" % (
            self.blog_style,
            "blog_index_page"
        )
    
    def get_context(self, request):
        page = request.GET.get('page')
        context = super().get_context(request)

        # select base articles
        articles = self.get_children().type(BlogArticlePage).live()
        # filter by category
        category = request.GET.get('category')
        if category:
            articles = articles.filter(
                blogarticlepage__category__name=category
            )
        # filter by tag
        tag = request.GET.get('tag')
        if tag:
            articles = articles.filter(
                blogarticlepage__tags__name=tag
            )

        # sort articles
        articles = articles.order_by('-first_published_at')
        
        # paginate articles
        paginator = Paginator(articles, 12)
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            articles = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            articles = paginator.page(paginator.num_pages)

        context['articles'] = articles

        if page or category or tag:
            # if page, category or tag applied, empty featured posts
            featured_articles = []
        else:
            featured_articles = (
                self.get_children()
                .type(BlogArticlePage)
                .filter(blogarticlepage__tags__name=self.featured_posts_tag)
                .live()
                .order_by('-first_published_at')
            )[:3]

        context['featured_articles'] = featured_articles
        return context

class BlogArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogArticlePage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

@register_snippet
class BlogAuthor(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = ["name", "author_image"]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)

    panels = ["name"]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class BlogArticlePage(SeoMixin, Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    cover = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        verbose_name="Capa",
        blank=True,
        null=True,
        default=None
    )
    tags = ClusterTaggableManager(through=BlogArticlePageTag, blank=True)
    authors = ParentalManyToManyField(BlogAuthor, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, blank=True, null=True, default=None)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            "date",
            FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
            'tags',
            'category'
        ], heading="Informações do Post"),
        MultiFieldPanel(["cover", "intro"], heading="Resumo do Post"),
        "body"
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body")
    ]
    
    # SEO
    promote_panels = SeoMixin.seo_panels
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE

    def get_template(self, request, *args, **kwargs):
        site = self.get_site()
        root = site.root_page
        return "blogs/%s/%s.html" % (
            root.specific.blog_style,
            "blog_article_page"
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['disable_header'] = True
        return context

class BlogMenuLink(Page):
    page = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
        verbose_name="Página Interna",
        blank=True,
        null=True,
        related_name='bloglinks'
    )
    page_extra = models.CharField("Extra URL", max_length=250, blank=True, default="")
    external_link = models.URLField("Link Externo", blank=True, null=True)

    content_panels = Page.content_panels + ["page", "page_extra", "external_link"]

    @property
    def submenus(self):
        menus = (
            self.get_children()
            .type(BlogMenuLink)
            .live()
        )
        return menus

    def serve(self, request, *args, **kwargs):
        if self.page:
            url = self.page.get_url(request)
            extra = self.page_extra or ""
            return redirect(url + extra)
        elif self.external_link:
            return redirect(self.external_link)
        return redirect('/')

class BlogAuthorsListPage(SeoMixin, Page):
    # SEO
    promote_panels = SeoMixin.seo_panels
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE

class BlogAuthorPage(SeoMixin, Page):
    author = models.ForeignKey(
        BlogAuthor,
        on_delete=models.CASCADE,
        verbose_name='Autor'
    )

    content_panels = Page.content_panels + ['author']

    # SEO
    promote_panels = SeoMixin.seo_panels
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE
