import json

from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy
from django.views import generic
from django.core.files import File
from django_tables2 import SingleTableView

from . import models, forms, tables
from users.views import get_identity
from mollib import atom


class Home(SingleTableView):

    table_class = tables.ProjectTable
    table_pagination = False
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        identity = get_identity(self.request)
        if not identity.config:
            identity.config = forms.OptionsForm.DEFAULTS
            identity.save(update_fields=['config'])
        data['options_form'] = forms.OptionsForm(data=identity.config)
        return data

    def get_queryset(self):
        return models.Project.objects.filter(identity=get_identity(self.request))

    def post(self, request, *args, **kwargs):
        identity = get_identity(self.request)
        for file_id in request.FILES:
            models.Project.objects.create(
                identity=identity,
                pdb=File(
                    file=request.FILES[file_id].file,
                    name=request.FILES[file_id].name
                ),
                config=identity.config,
                filename=request.FILES[file_id].name
            )
        table = self.get_table()
        return JsonResponse({
            'success': True,
            'table': table.as_html(request)
        })


class Detail(generic.DetailView):

    model = models.Project
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['plotly'] = {'input-pk': {'value': self.object.pk}}
        return data


class Delete(generic.DeleteView):

    model = models.Project
    template_name = 'delete.html'
    success_url = reverse_lazy('home')


def project_status(request, pk):
    identity = get_identity(request)
    try:
        project = identity.project_set.get(pk=pk)
        if project.error:
            raise models.Project.DoesNotExist
        content = {'progress': json.dumps(project.progress)}
    except models.Project.DoesNotExist:
        content = {'error': 'Error'}
    return JsonResponse(content)


class RCSB(generic.FormView):

    template_name = 'rcsb.html'
    form_class = forms.RCSBForm
    success_url = reverse_lazy('home')

    # TODO: disable submit button after click

    def form_valid(self, form):
        try:
            pdb_code = form.cleaned_data['code']
            pdb_file = atom.PdbFile(pdb_code)
            identity = get_identity(self.request)
            models.Project.objects.create(
                identity=identity,
                pdb=File(
                    name=pdb_code,
                    file=pdb_file.opened_file
                ),
                config=identity.config,
                filename=pdb_code
            )

            return JsonResponse({
                'success': True,
                'url': self.get_success_url()
            })

        except atom.InvalidPdbCode as e:
            form.add_error('code', e)
            return self.form_invalid(form)


def update_options(request):
    identity = get_identity(request)
    form = forms.OptionsForm(data=request.POST)
    if form.is_valid():
        identity.config = form.cleaned_data
        identity.save(update_fields=['config'])
        return JsonResponse({'message': 'Changes saved!'})
    else:
        return JsonResponse({'error': 'Changes not saved!'})


def reset_options(request):
    # TODO: update form only, without homepage reload
    identity = get_identity(request)
    identity.config = forms.OptionsForm.DEFAULTS
    identity.save(update_fields=['config'])
    return redirect('home')


def molstar(request, pk):
    identity = get_identity(request)
    try:
        project = models.Project.objects.get(identity=identity, pk=pk)
    except models.Project.DoesNotExist:
        return Http404

    return HttpResponse(project.fixed_pdb)


def molstar_model(request, pk, model_index):
    identity = get_identity(request)
    # TODO: fix the 404 error
    try:
        project = models.Project.objects.get(identity=identity, pk=pk)
        job = project.job_set.filter(model_index=model_index).first()
        if not job:
            raise models.Project.DoesNotExist
    except models.Project.DoesNotExist:
        return Http404

    return HttpResponse(job.pdb)


class HelpView(generic.TemplateView):

    template_name = 'help-modal.html'


class AboutView(generic.TemplateView):

    template_name = 'about.html'
