from django import forms
from django.urls import reverse
from crispy_forms import helper, layout


class CrispyFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.attrs = {'novalidate': ''}
        self.helper.form_show_errors = True
        self.helper.form_show_labels = False


class LoginForm(CrispyFormMixin, forms.Form):

    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter email address'}
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Enter password'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.form_action = reverse('login')

        header_content = f'''<span>Login to </span><a href="{reverse('home')}" class="text-white">Mapserver</a>'''
        footer_content = f'''<small><span>No account? </span><a href="{reverse('signup')}">Signup</a></small>'''
        form_layout = layout.Layout(
            'email',
            'password',
            layout.HTML(f'''<button type="submit" class="btn btn-primary btn-block my-3">Submit</button>'''),
            layout.HTML(f'''
                <small class="text-muted">Forgotten password? <a href="{reverse('password-reset')}">Reset</a></small>
            ''')
        )

        self.helper.layout = layout.Layout(
            layout.Div(
                layout.HTML(header_content),
                css_class='card-header text-center bg-primary text-white font-weight-bold'
            ),
            layout.Div(
                form_layout,
                css_class='card-body text-center px-5 pt-4 pb-3'
            ),
            layout.Div(
                layout.HTML(footer_content),
                css_class='card-footer text-center'
            ),
        )


class SignupForm(CrispyFormMixin, forms.Form):

    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter email address'}
        )
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Enter password'}
        )
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Confirm password'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.form_action = reverse('signup')

        header_content = f'''<span>Signup to </span><a href="{reverse('home')}" class="text-white">Mapserver</a>'''
        footer_content = f'''<small><span>Already a member? </span><a href="{reverse('login')}">Login</a></small>'''
        form_layout = layout.Layout(
            'email',
            'password1',
            'password2',
            layout.HTML(f'''<button type="submit" class="btn btn-primary btn-block my-3">Submit</button>'''),
        )

        self.helper.layout = layout.Layout(
            layout.Div(
                layout.HTML(header_content),
                css_class='card-header text-center bg-primary text-white font-weight-bold'
            ),
            layout.Div(
                form_layout,
                css_class='card-body text-center px-5 pt-4 pb-3'
            ),
            layout.Div(
                layout.HTML(footer_content),
                css_class='card-footer text-center'
            ),
        )


class PasswordForm(CrispyFormMixin, forms.Form):

    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter email address'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.form_action = reverse('password-reset')

        header_content = 'Reset password'
        footer_content = f'''<a href="{reverse('login')}">Back to login</a>'''
        form_layout = layout.Layout(
            'email',
            layout.HTML(f'''<button type="submit" class="btn btn-primary btn-block my-3">Submit</button>'''),
        )

        self.helper.layout = layout.Layout(
            layout.Div(
                layout.HTML(header_content),
                css_class='card-header text-center bg-primary text-white font-weight-bold'
            ),
            layout.Div(
                form_layout,
                css_class='card-body text-center px-5 pt-4 pb-3'
            ),
            layout.Div(
                layout.HTML(footer_content),
                css_class='card-footer text-center'
            ),
        )


class RCSBForm(CrispyFormMixin, forms.Form):

    code = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter 4-letter PDB code (i.e. 2gb1).'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.form_action = reverse('rcsb')
        self.helper.form_id = 'rcsbForm'
        self.helper.form_show_errors = True
        self.helper.layout = layout.Layout(
            'code',
            layout.HTML(f'''<button type="submit" class="btn btn-success btn-block mty-3">Submit</button>'''),
        )
