from wagtail.models import Page
from wagtailseo.models import SeoMixin, SeoType, TwitterCard

class ArdoliHomePage(SeoMixin, Page):
    # SEO
    promote_panels = SeoMixin.seo_panels
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE
