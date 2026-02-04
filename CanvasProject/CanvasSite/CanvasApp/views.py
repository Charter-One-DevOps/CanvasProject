from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .models import School
from .forms import SchoolForm

#Create you views here.
def test(request, school_name):
    school_object = School.objects.get(name= school_name)
    context = {"school": school_object}
    return render(request, "test.html", context)

def upload_file(request):
    if request.method == "POST":
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect("/success/url/")
    else:
        form = SchoolForm()
    return render(request, "buttons.html", {"form": form})

def handle_uploaded_file(f):
    with open("testing.csv", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

class TestClass(View):

    def get(self, request):
        context = {"form": SchoolForm()}
        return render(request, "buttons.html", context)

    def post(self, request):
        #invalid form
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            self.handle_uploaded_file(request.FILES["file"])
            # return render(request, "buttons.html", self.context)
            return HttpResponseRedirect(f"/Canvas/{form.cleaned_data['school']}")
        return HttpResponse("invalid data")

    @staticmethod
    def handle_uploaded_file(f):
        with open("testing.csv", "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)