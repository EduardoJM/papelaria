from django import template
from wagtail.models import Page
from blogs.models import BlogMenuLink

register = template.Library()

@register.simple_tag
def menu_items(page: Page):
    site = page.get_site()
    root = site.root_page
    
    main_menu = (
        root.get_children()
        .type(BlogMenuLink)
        .live()
    )

    return main_menu
