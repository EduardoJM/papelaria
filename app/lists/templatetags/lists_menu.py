from django import template
from wagtail.models import Page
from lists.models import MenuLink

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
