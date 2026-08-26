from django import template
from wagtail.models import Page
from blogs.models import BlogMenuLink

register = template.Library()

@register.simple_tag
def menu_items(page: Page):
    site = page.get_site()
    
    return BlogMenuLink.objects.filter(site=site, parent__isnull=True)

@register.simple_tag
def menu_logo(page: Page):
    site = page.get_site()
    root = site.root_page
    specific = root.specific
    
    if not specific.logo:
        return None
    
    url = specific.logo.get_rendition('fill-120x50').url
    return url
