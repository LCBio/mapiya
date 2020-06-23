from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views import generic
from django.core.files import File
from django.shortcuts import redirect
from django_tables2 import SingleTableView
from mapserver import models, forms, tables


def get_identity(request):

    if request.user.is_authenticated:
        return models.Identity.objects.get_or_create(user=request.user)[0]

    else:
        request.session.save()
        return models.Identity.objects.get_or_create(session_id=request.session.session_key)[0]


class HomeView(SingleTableView):

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


class MapDetail(generic.DetailView):

    model = models.Map
    template_name = 'mapserver/map.html'


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
            'labels': labels + [''],
            'points': points,
        }
    except models.Map.DoesNotExist:
        data = {
            'success': False
        }
    return JsonResponse(data=data)


class MapDelete(generic.DeleteView):

    model = models.Map
    template_name = 'mapserver/delete.html'
    success_url = reverse_lazy('home')


class AlreadyLoggedInMixin:

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class LoginView(AlreadyLoggedInMixin, generic.FormView):

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
                user = models.User.objects.get(email=email)
                form.add_error('password', 'Invalid password')
            except models.User.DoesNotExist:
                form.add_error('email', 'User does not exist')
            return self.form_invalid(form)


class SignupView(AlreadyLoggedInMixin, generic.FormView):

    template_name = 'mapserver/login.html'
    form_class = forms.SignupForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        try:
            # check if email is not already taken
            user = models.User.objects.get(email=email)
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
    return redirect('login')
