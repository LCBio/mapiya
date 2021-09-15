import json
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import generic
from django.core.files import File
from django_tables2 import SingleTableView
from . import models, forms, tables
from users.views import get_identity
from mollib import atom


class Home(SingleTableView):

    table_class = tables.MapTable
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['options_form'] = forms.OptionsForm(identity=get_identity(self.request))
        return data

    def get_queryset(self):
        return models.Map.objects.filter(identity=get_identity(self.request))

    def post(self, request, *args, **kwargs):
        identity = get_identity(self.request)
        for file_id in request.FILES:
            models.Map.objects.create(
                identity=identity,
                pdb=File(
                    file=request.FILES[file_id].file,
                    name=request.FILES[file_id].name
                ),
                filename=request.FILES[file_id].name
            )
        table = self.get_table()
        return JsonResponse({
            'success': True,
            'table': table.as_html(request)
        })


class Detail(generic.DetailView):

    model = models.Map
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['plotly'] = {'input-pk': {'value': self.object.pk}}
        return data


class Delete(generic.DeleteView):

    model = models.Map
    template_name = 'delete.html'
    success_url = reverse_lazy('home')


class RCSB(generic.FormView):

    template_name = 'rcsb.html'
    form_class = forms.RCSBForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        try:
            pdb_code = form.cleaned_data['code']
            pdb_file = atom.PdbFile(pdb_code)
            models.Map.objects.create(
                identity=get_identity(self.request),
                pdb=File(
                    name=pdb_code,
                    file=pdb_file.opened_file
                ),
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
    data = {key: request.POST[key] for key in request.POST if key != 'csrfmiddlewaretoken'}
    identity.config = json.dumps(data)
    identity.save(update_fields=['config'])
    return JsonResponse({'success': True, 'message': 'Config updated'})


def reset_options(request):
    # TODO: update form only, without homepage reload
    identity = get_identity(request)
    identity.config = json.dumps(forms.OptionsForm.DEFAULTS)
    identity.save(update_fields=['config'])
    return redirect('home')
