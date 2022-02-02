import markdown2
from random import seed, random
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django import forms
from . import util

class CreateEntryForm(forms.Form):
    title = forms.CharField(widget = forms.TextInput(attrs = {'class': 'form-field', 'autofocus': True}), label = "Title", required = True)
    content = forms.CharField(widget = forms.Textarea(attrs = {'class': 'form-field'}), label = "Content", required = True)

def index(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        content = util.get_entry(query)
        if content is not None:
            page = markdown2.markdown(content)
            return HttpResponseRedirect(f"wiki/{query}")
        results = []
        for entry in util.list_entries():
            if query in entry:
                results.append(entry)
        return render(request, 'encyclopedia/search.html', {
            "query": query,
            "results": results
        })
        
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, entry):        
    content = util.get_entry(entry)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "error": "Entry not found",
            "message": f'No results for "{entry}".'
        })
        
    page = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "page": page
    })
    
def create(request):
    if request.method == 'POST':
        form = CreateEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            for entry in util.list_entries():
                if title == entry:
                    return render(request, "encyclopedia/error.html", {
                        "error": "Duplicate Entry",
                        "message": f'The entry with title "{entry}" already exists.'
                    })
            with open(f"entries/{title}.md", "w") as entry:
                content = f"# {title}\n\n{form.cleaned_data['content']}"
                entry.write(content)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'encyclopedia/error.html', {
                "error": "Invalid page",
                "message": ""
            })
    return render(request, "encyclopedia/create.html", {
        "form": CreateEntryForm()
    })
    
def edit(request, entry):
    if request.method == "POST":
        editedContent = request.POST.get('content')
        for storedEntry in util.list_entries():
            if entry == storedEntry:
                with open(f"entries/{entry}.md", "w") as entryToEdit:
                    content = f"# {entry}\n\n{editedContent}"
                    entryToEdit.write(content)
        return HttpResponseRedirect(reverse('wiki', args = [entry]))
    content = util.get_entry(entry).partition("\n")[2]
    return render(request, 'encyclopedia/edit.html', {
        "entry": entry,
        "content": content
    })
    
def random_page(request):
    prnum = random()
    entries = util.list_entries()
    return HttpResponseRedirect(reverse('wiki', args = [entries[int(prnum * len(entries))]]))