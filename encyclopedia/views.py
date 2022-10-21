from django import forms
from django.shortcuts import render
from . import util
from markdown2 import markdown
import random


class NewPageForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea())


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    page = util.get_entry(title)
    if page is None:
        return render(request, "encyclopedia/entry-not-found.html")
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "page": markdown(page)
        })


def search(request):
    query = request.GET["q"]
    page = util.get_entry(query)
    if page is None:
        return render(request, "encyclopedia/search.html", {
            "entries": [entry for entry in util.list_entries() if query.lower() in entry.lower()]
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": query,
            "page": markdown(page)
        })


def create(request):
    errors = []
    form = NewPageForm()
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title.lower() not in [e.lower() for e in util.list_entries()]:
                util.save_entry(title, content)
                return entry(request, title)
            else:
                errors.append("Existing title")
        else:
            errors.append("Invalid field filling")

    return render(request, "encyclopedia/create.html", {
        "form": form,
        "errors": errors
    })


def edit(request, title):
    error = None
    if request.method == "POST":
        if request.POST["content"]:
            util.save_entry(title, request.POST["content"])
            return entry(request, title)
        else:
            error = "The content must be filled"

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": util.get_entry(title),
        "error": error
    })


def random_entry(request):
    return entry(request, random.choice(util.list_entries()))