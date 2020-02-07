from django.views import generic
from django.http import JsonResponse
from mapserver import models, forms


def get_identity(request):

    # make sure session is active
    if request.session.session_key is None:
        request.session.save()

    # if user is logged in return his identity, or create a new one
    if request.user.is_authenticated:
        return models.Identity.objects.get_or_create(user=request.user)[0]

    # return identity associated with current session, or create a new one
    else:
        return models.Identity.objects.get_or_create(session_id=request.session.session_key)[0]


class Home(generic.FormView):

    form_class = forms.UploadForm
    template_name = 'mapserver/home.html'

    def form_valid(self, form):

        # TODO: Here call to function which checks for data_type of the form.cleaned_data['file']
        data_type = models.DataType.objects.get(pk=1)

        # create new project
        project = models.Project(
            owner=get_identity(self.request)
        )
        project.save()

        # create new upload object
        upload = models.Upload(
            file=form.cleaned_data['file'],
            type=data_type,
            project=project
        )
        upload.save()

        return JsonResponse({'success': True})


class UploadDetail(generic.DetailView):

    model = models.Upload
    template_name = 'mapserver/upload-detail.html'
