from django import forms
def handle_uploaded_file(f):
    with open('1.pdf', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
