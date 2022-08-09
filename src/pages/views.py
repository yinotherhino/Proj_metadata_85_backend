from django.shortcuts import render, redirect, get_object_or_404
from .forms import *

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

# Registration and login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_auth


from django.http import HttpResponse
from django.utils.encoding import smart_str

# -----Packages for extracting metadata-----
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from tinytag import TinyTag
import csv

# from metadata.models import Contact
from django.http import HttpResponseRedirect

import xtracto

from .forms import FileUpload
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.models import User, auth


# STATIC VIEWS


def index(request):
    return render(request, "xtracto/home.html")


def about(request):
    return render(request, "xtracto/About-us.html")


def contact(request):
    return render(request, "xtracto/contact.html")



def faqs(request):
    return render(request, "xtracto/faqs.html")


def docs(request):
    return render(request, "xtracto/docs.html")


# DYNAMIC VIEWS


def pwdreset(request):
    return render(request, "xtracto/pwdreset.html")


def verify(request):
    return render(request, "xtracto/verify.html")


# DYNAMIC VIEWS


def pwdreset(request):
    return render(request, "xtracto/pwdreset.html")


def verify(request):
    return render(request, "xtracto/verify.html")


def docs(request):
    return render(request, "xtracto/docs.html")


# dashboard page with authentication
@login_required
def dashboard(request):
    return render(request, "xtracto/dashboard.html")


def collections(request):
    return render(request, "xtracto/collections.html")


def features(request):
    return render(request, "xtracto/features.html")


def register_request(request):
    if request.method == "POST":
        form = Registrationform(request.POST)
        email = request.POST["username"]
        user = authenticate(request, username=email)
        if user is None:
            if form.is_valid():
                post = form.save(commit=False)
                post.username = request.POST["username"]
                post.email = request.POST["username"]
                post.password = make_password(request.POST["password"])
                messages.success(request, "Registration successful.")
                post.save()

                # login after ctreating account
                user = authenticate(
                    request,
                    username=request.POST["username"],
                    password=request.POST["password"],
                )
                login_auth(request, user)
                # return render(request=request, template_name="xtracto/dashboard.html", context={})
                return redirect("xtracto:dashboard")
            else:
                form = Registrationform()
                return render(request=request, template_name="xtracto/register.html", context={'form': form})

        else:
            messages.error(request, "email Already exists")
            form = Registrationform()
            return render(request=request, template_name="xtracto/register.html", context={'form': form})
    else:
        form = Registrationform()
        return render(
            request=request,
            template_name="xtracto/register.html",
            context={"form": form},
        )


def login_request(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login_auth(request, user)
            return render(request, "xtracto/dashboard.html", {})

        else:
            messages.success(request, "There was an error Logging in.")
            return render(request, "xtracto/login.html", {})

    else:
        return render(request, "xtracto/login.html", {})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("xtracto:home")


# ------Metadata-------#
class view_xtracto(View):
    success_url = reverse_lazy("xtracto:viewXtracto")
    template_name = "xtracto/upload.html"

    def post(self, request):
        form = FileUpload(request.POST, request.FILES)
        context = {"xtracto": []}
        if form.is_valid():

            uploaded_file = request.FILES["upload_file"]
            file_type = uploaded_file.content_type.split("/")

            context["xtracto"].append(
                {"label_name": "File Name", "label_value": uploaded_file.name}
            )
            context["xtracto"].append(
                {"label_name": "Mime Type", "label_value": uploaded_file.content_type}
            )
            context["xtracto"].append(
                {"label_name": "File Size", "label_value": uploaded_file.size}
            )
            context["xtracto"].append(
                {"label_name": "File Type", "label_value": file_type[0].capitalize()}
            )

            if (
                file_type[0] == "video"
                or file_type[0] == "image"
                or file_type[0] == "audio"
            ):

                parser = createParser(uploaded_file)
                xtracto = extractMetadata(parser)

                context["file_name"] = uploaded_file.name
                context["file_size"] = uploaded_file.size
                context["file_type"] = file_type[0].capitalize()
                context["mime_type"] = uploaded_file.content_type

                for line in enumerate(xtracto.exportPlaintext()):
                    if line[0] != 0:
                        label = line[1].split(":")
                        label_name = label[0][1:].split()
                        label_value = label[1][:]

                        if len(label_name) > 1:
                            label_name = f"{label_name[0]}_{label_name[1]}"
                        else:
                            label_name = label_name[0]

                        context["xtracto"].append(
                            {"label_name": label_name, "label_value": label_value}
                        )

            request.session["xtracto"] = context
            return redirect("xtracto:result")
        return render(request, self.template_name, {"form": form})

    def get(self, request):
        form = FileUpload()
        return render(request, self.template_name, {"form": form})


# ---------------------------------#


def result(request):
    xtracto = request.session.get("xtracto")
    context = xtracto
    return render(request, "xtracto/result.html", context)


# ---------------------------------------------#


def download_csv_data(request):
    #  content type
    xtracto = request.session.get("xtracto")
    metadata_label = list(xtracto.keys())[1:]

    response = HttpResponse(content_type="text/csv")
    # file name
    response["Content-Disposition"] = "attachment; filename= label_value.csv"
    # ' "download.csv" '

    writer = csv.writer(response, csv.excel)
    response.write("\ufeff".encode("utf8"))

    metadata_label_name = []
    metadata_label_value = []

    for metadata_val in xtracto["xtracto"]:
        metadata_label_name.append(smart_str(metadata_val["label_name"]))
        metadata_label_value.append(smart_str(metadata_val["label_value"]))

    writer.writerow(metadata_label_name)
    writer.writerow(metadata_label_value)

    return response


# saving the extracted metadata
# still working on this code
# ---------------------------
# def saveMeta(request):
#     template = "save.html"
#     form = saveMetada(request.POST or None)
#     if form.is_valid():
#         form.save()
#         return redirect("/")
#     context = {"form": form}
#     return render(request, template, context)



