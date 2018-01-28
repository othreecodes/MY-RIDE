from django.forms import *
from django.conf import settings

class UploadFileForm(forms.Form):
    file = forms.FileField()

    def handle_uploaded_file(self,file):
        #print type(file), "file.name=",file.name
        # print dir(file)
        destination = open(settings.MEDIA_ROOT +'okok', 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)


