from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'index.html'


class DetailView(generic.TemplateView):
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        return dict(id=self.kwargs.get('id'))
