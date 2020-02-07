from django.template import loader
from django.http import HttpResponse
from .project import Home, UploadDetail


def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('gentella/' + load_template)
    return HttpResponse(template.render(context, request))
