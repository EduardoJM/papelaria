from wagtail.admin.panels import Panel

class BuilderPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        template_name = "pagebuilder/builder.html"
