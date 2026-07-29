from django import template
from django.http import QueryDict
from wagtail.models import Page
from lists.models import MenuLink, ListIndexPage

register = template.Library()

@register.simple_tag
def menu_items(page: Page):
    site = page.get_site()
    root = site.root_page
    
    main_menu = (
        root.get_children()
        .type(MenuLink)
        .live()
    )

    return main_menu

@register.simple_tag
def menu_logo(page: Page):
    site = page.get_site()
    root = site.root_page
    specific = root.specific

    if not isinstance(specific, ListIndexPage):
        return None
    
    if not specific.logo:
        return None
    
    url = specific.logo.get_rendition('fill-180x60').url
    return url

@register.simple_tag
def is_url_equals(request, url, extra):
    if request.path != url:
        return False
    if not extra:
        return True
    
    extra = extra.replace('?', '')
    q = QueryDict(extra)
    if q != request.GET:
        return False

    return True
