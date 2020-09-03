from django.http import JsonResponse
from django.utils.html import format_html
from django.template import Template, Context
from django.urls import reverse_lazy
from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views import generic
from django.core.files import File
from django.shortcuts import redirect
from django_tables2 import SingleTableView
from mapserver import models, forms, tables
from mollib import atom
import json


def get_identity(request):

    if request.user.is_authenticated:
        return models.Identity.objects.get_or_create(user=request.user)[0]

    else:
        request.session.save()
        return models.Identity.objects.get_or_create(session_id=request.session.session_key)[0]


class Home(SingleTableView):

    table_class = tables.MapTable
    template_name = 'mapserver/home.html'

    def get_queryset(self):
        return models.Map.objects.filter(identity=get_identity(self.request))

    def post(self, request, *args, **kwargs):
        identity = get_identity(self.request)
        for file_id in request.FILES:
            mapobj = models.Map.objects.create(
                identity=identity,
                pdb=File(
                    file=request.FILES[file_id].file,
                    name=request.FILES[file_id].name
                ),
                filename=request.FILES[file_id].name
            )
            mapobj.save_matrix()
        t = self.get_table()
        return JsonResponse({
            'success': True,
            'table': t.as_html(request)
        })


class Detail(generic.DetailView):

    model = models.Map
    template_name = 'mapserver/map.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['table'] = tables.NGLTable(mapobj=self.object)
        return data


class NGLAddRep(generic.View):

    def post(self, request, pk):
        try:
            mapobj = models.Map.objects.get(pk=pk)
            rep = models.Representation.objects.create(
                map=mapobj,
                name='New'
            )
            html = Template('''
                <tr {{ row.attrs.as_html }}>
                    {% for column, cell in row.items %}
                        <td {{ column.attrs.td.as_html }}>{{ cell }}</td>
                    {% endfor %}
                </tr>
            ''').render(context=Context({
                'row': next(r for r in tables.NGLTable(mapobj=mapobj).rows if r.record == rep)
            }))
            return JsonResponse({
                'success': True,
                'addRep': html
            })

        except models.Map.DoesNotExist as e:
            return JsonResponse({
                'success': True,
                'error': e
            })


class NGLDelRep(generic.View):

    def post(self, request, pk):
        try:
            rep = models.Representation.objects.get(pk=pk)
            key = f'rep_{rep.pk}'
            rep.delete()
            return JsonResponse({
                'success': True,
                'delRep': key
            })

        except models.Representation.DoesNotExist as e:
            return JsonResponse({
                'success': True,
                'error': str(e)
            })


class NGLUpdateRep(generic.View):

    def post(self, request, pk):
        try:
            rep = models.Representation.objects.get(pk=pk)
            name = request.POST.get('name')
            val = request.POST.get('value')

            if name == 'name':
                rep.name = val
            elif name == 'selection':
                rep.selection = val
            elif name == 'color':
                rep.color = models.NGLColorScheme.objects.get(keyword=val)
            elif name == 'representation':
                rep.representation = models.NGLRepresentation.objects.get(keyword=val)

            rep.save()
            key = f'rep_{rep.pk}'
            return JsonResponse({
                'success': True,
                'updateRep': key
            })

        except models.Representation.DoesNotExist as e:
            return JsonResponse({
                'success': True,
                'error': str(e)
            })


class NGLOptions(generic.View):

    def get(self, request, pk):

        data = {'success': True}

        try:
            rep = models.Representation.objects.get(pk=pk)
            keyword = request.GET.get('keyword')
            if keyword is None:
                default_options = json.loads(rep.representation.options)
                options = {key: option['default'] for key, option in default_options.items()}
                if rep.options:
                    options.update(json.loads(rep.options))
                data['options'] = options

            elif keyword == 'representation':
                data['html'] = forms.ngl_options_form_factory(rep).as_table()

            elif keyword == 'color':
                data['html'] = forms.ngl_options_form_factory2(rep).as_table()

        except models.Representation.DoesNotExist as e:
            data['error'] = str(e)

        return JsonResponse(data)


def map_tiles(request, pk):
    try:
        map_obj = models.Map.objects.get(pk=pk)
        dim = int(request.GET.get('dim')) - 20

        chains = [(x, int(y)) for x, y in [_.split(':') for _ in map_obj.chains.split()]]
        sum_len = sum(x[1] for x in chains)
        dims = [round(x[1] * dim / sum_len) for x in chains]

        def get_rect(w, h, x, y):
            return f'<rect class="map-tile" x="{x}" y="{y}" width="{w}" height="{h}"></rect>'

        x = y = 0
        rects = []
        for dy in dims:
            for dx in dims:
                rects.append(get_rect(dx, dy, x, y))
                x += dx
            x = 0
            y += dy

        rects = '\n'.join(rects)
        html = f'<svg width="{dim}" height="{dim}">{rects}</svg>'

        data = {
            'success': True,
            'html': format_html(html)
        }
    except (models.Map.DoesNotExist, TypeError):
        data = {
            'success': False
        }
    return JsonResponse(data=data)


def map_data(request, pk):
    try:
        map_obj = models.Map.objects.get(pk=pk)
        matrix = map_obj.matrix
        labels = map_obj.labels
        points = [
            {
                'x': i,
                'y': j,
                'xNgl': labels[i],
                'yNgl': labels[j],
                'value': matrix[i][j]
            } for i in range(len(labels)) for j in range(len(labels))
        ]
        data = {
            'success': True,
            'chains': map_obj.chains,
            'labels': labels + [''],
            'points': points,
        }
    except models.Map.DoesNotExist:
        data = {
            'success': False
        }
    return JsonResponse(data=data)


class Delete(generic.DeleteView):

    model = models.Map
    template_name = 'mapserver/delete.html'
    success_url = reverse_lazy('home')


class RCSB(generic.FormView):

    template_name = 'mapserver/rcsb.html'
    form_class = forms.RCSBForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        try:
            pdb_code = form.cleaned_data['code']
            pdb_file = atom.PdbFile(pdb_code)
            map_obj = models.Map.objects.create(
                identity=get_identity(self.request),
                pdb=File(
                    name=pdb_code,
                    file=pdb_file.opened_file
                ),
                filename=pdb_code
            )
            map_obj.save_matrix()

            return JsonResponse({
                'success': True,
                'url': self.get_success_url()
            })

        except atom.InvalidPdbCode as e:
            form.add_error('code', e)
            return self.form_invalid(form)


class AlreadyLoggedInMixin:

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class Login(AlreadyLoggedInMixin, generic.FormView):

    template_name = 'mapserver/login.html'
    form_class = forms.LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = auth.authenticate(self.request, email=email, password=password)
        if user is not None:
            auth.login(self.request, user)
            return super().form_valid(form)
        else:
            try:
                models.User.objects.get(email=email)
                form.add_error('password', 'Invalid password')
            except models.User.DoesNotExist:
                form.add_error('email', 'User does not exist')
            return self.form_invalid(form)


class Signup(AlreadyLoggedInMixin, generic.FormView):

    template_name = 'mapserver/login.html'
    form_class = forms.SignupForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        try:
            # check if email is not already taken
            models.User.objects.get(email=email)
            form.add_error('email', 'User with this email already exists')
            return self.form_invalid(form)
        except models.User.DoesNotExist:
            # check if passwords match
            if password1 != password2:
                form.add_error('password2', 'Passwords don\'t match')
                return self.form_invalid(form)
            # validate password
            try:
                validate_password(password1)
                user = models.User.objects.create_user(email=email, password=password1)
                identity = get_identity(self.request)
                identity.user = user
                identity.session = None
                identity.save()
                auth.login(self.request, user)
                return super().form_valid(form)

            except ValidationError as e:
                form.add_error('password1', e.messages)
                return self.form_invalid(form)


class PasswordReset(generic.FormView):

    template_name = 'mapserver/login.html'
    form_class = forms.PasswordForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = models.User.objects.get(email=email)
            # TODO: here password reset logic
            return self.render_to_response(context={'message': 'Link to password reset was sent to: ' + email})
        except models.User.DoesNotExist:
            form.add_error('email', 'Email address not found.')
            return self.form_invalid(form)


def logout(request):
    auth.logout(request)
    return redirect('home')
