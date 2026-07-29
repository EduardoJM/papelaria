from django import template
from wagtail.models import Page
from lists.models import ListIndexPage

register = template.Library()

@register.simple_tag
def main_title(page: Page):
    site = page.get_site()
    root = site.root_page
    specific = root.specific

    if not isinstance(specific, ListIndexPage):
        return None
    
    return specific.main_title
