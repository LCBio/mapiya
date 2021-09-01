from django.urls import reverse_lazy
from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views import generic
from django.shortcuts import redirect
from . import models, forms


def get_identity(request):

    if request.user.is_authenticated:
        return models.Identity.objects.get_or_create(user=request.user)[0]

    else:
        request.session.save()
        return models.Identity.objects.get_or_create(session_id=request.session.session_key)[0]


class AlreadyLoggedInMixin:

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class Login(AlreadyLoggedInMixin, generic.FormView):

    template_name = 'users/login.html'
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

    template_name = 'users/login.html'
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

    template_name = 'users/login.html'
    form_class = forms.PasswordForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            models.User.objects.get(email=email)
            # TODO: here password reset logic
            return self.render_to_response(context={'message': 'Link to password reset was sent to: ' + email})
        except models.User.DoesNotExist:
            form.add_error('email', 'Email address not found.')
            return self.form_invalid(form)


def logout(request):
    auth.logout(request)
    return redirect('home')
