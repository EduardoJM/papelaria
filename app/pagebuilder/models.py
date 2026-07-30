from django.db import models
from wagtail.models import Page
from wagtail.models.panels import PanelPlaceholder
from wagtail.admin.panels import TabbedInterface, TitleFieldPanel, ObjectList


class BuilderPage(Page):
    page_content = models.TextField("Conteúdo da Página", blank=True, default="")

    builder_panels = [
        PanelPlaceholder("pagebuilder.panels.BuilderPanel", [], {})
    ]

    edit_handler = TabbedInterface([
        ObjectList(Page.content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='Promote'),
        ObjectList(builder_panels, heading='Builder'),
    ])
