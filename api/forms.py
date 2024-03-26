from django.forms import *
from django.conf import settings

class UploadFileForm(forms.Form):
    file = forms.FileField()

    def handle_uploaded_file(self,file):
        with open(settings.MEDIA_ROOT +'okok', 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)


