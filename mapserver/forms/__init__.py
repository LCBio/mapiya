from django import forms
from mapserver import models


class UploadForm(forms.ModelForm):

    class Meta:
        model = models.Upload
        fields = ['file']