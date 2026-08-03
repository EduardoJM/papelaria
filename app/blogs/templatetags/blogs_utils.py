from django import template
from wagtail.models import Page

register = template.Library()

@register.simple_tag
def root_page(page: Page):
    site = page.get_site()
    root = site.root_page
    return root.specific
