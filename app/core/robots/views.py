from django.views.generic import TemplateView

class RobotsView(TemplateView):
    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'
