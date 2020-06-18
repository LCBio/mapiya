from django import forms


class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class SignupForm(forms.Form):

    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())


class PasswordForm(forms.Form):

    email = forms.EmailField()
