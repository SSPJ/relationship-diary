# Relationship Diary, Seamus Johnston, 2018, GPLv3
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, DeleteView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.views.decorators.cache import never_cache

from whenandwho.models import Record, Category, Note
from .forms import ContactModelForm, ContactFormSet
from .helpers import clean_import, parse

from datetime import date
import csv
import re
import json
import logging
logger = logging.getLogger(__name__)

class RecordListView(ListView):
    """ This class displays the main contact list on the index page """

    template_name = "whenandwho/record_list.html"

    def get_queryset(self, **kwargs):
      if 'category' in self.kwargs:
        return Record.objects \
                .filter(categories__icontains=self.kwargs['category']) \
                .order_by('next_contact_date')
      return Record.objects.order_by('next_contact_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories_list'] = Category.objects.all()
        return context

class RecordDetailView(DetailView):
    """ This class displays the contact's detail page and associated notes """

    model = Record
    template_name = "whenandwho/record_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['http_referer_category'] = self.request.META['HTTP_REFERER'] \
            .partition('category/')[2][:-1]
        context['notes_list'] = Note.objects \
            .filter(record=self.kwargs['pk']) \
            .order_by('date')
        return context

class RecordDeleteView(DeleteView):
    """ This class confirms deletion of a given contact """

    model = Record
    template_name = "whenandwho/record_confirm_delete.html"
    success_url = "/"

def record_create_view(request):
    """ Displays an empty form for creating a new contact """
    if request.method == "POST":
        form = ContactModelForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return redirect("detail", pk=instance.pk)
    else:
        form = ContactModelForm()
    return render(request, "whenandwho/record_form.html", {'form': form})

def record_edit_view(request, pk):
    """ Displays a pre-filled form for editing a contact """
    record = get_object_or_404(Record, pk=pk)
    if request.method == "POST":
        form = ContactModelForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("detail", pk=pk)
    else:
        form = ContactModelForm(instance=record)
    return render(request, "whenandwho/record_form.html", {'form': form})

def populate(request):
    """ AJAX method for converting a vCard parsed by vcardparser.js into contact(s)

    It will clean and save the contacts directly if there are 20 or more,
    otherwise it will display them as a formset on the index page for user edits
    """
    process_direct = False

    if request.is_ajax():
        logger.debug(request.body)
        cleaned_import = clean_import(json.loads(request.body))
        logger.debug(cleaned_import)
        formset = ContactFormSet(initial=cleaned_import)
        if len(cleaned_import) <= 20:
            return render(request, "whenandwho/record_populate.html", {"formset": formset})
        else:
            process_direct = True

    if process_direct == False:
        formset = ContactFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
            return redirect("index")
        else:
            return render(request, "whenandwho/record_populate.html", {"formset": formset})

    if process_direct == True:
        for i, contact in enumerate(cleaned_import):
            if Record.objects.filter(fn=contact['fn']).exists():
                contact['fn'] = contact['fn'] + "_duplicate" + str(i)
            c = Record.objects.create(**contact)
        return HttpResponse(status=204)
    return HttpResponse(status=404)

def create_note(request, pk):
    """ AJAX method for saving notes associated with a contact """
    record = get_object_or_404(Record, pk=pk)
    note_text = request.body.decode("utf-8")
    logger.debug(note_text)
    note = Note(record=record,note=note_text)
    note.save()
    return HttpResponse(status=204)

def water(request, pk):
    """ AJAX method for updating the date a contact is due to be contacted """
    record = get_object_or_404(Record, pk=pk)
    record.next_contact_date = Record.get_next_contact_date(record.frequency)
    record.save()
    return HttpResponse(status=204)

def quick_add(request):
    """ AJAX method for parsing a string into a contact and saving it """
    if request.is_ajax():
        new_contact = parse(request.body.decode("utf-8"))
        instance, created = Record.objects.update_or_create(defaults=new_contact,fn=new_contact['fn'])
        if created:
          return HttpResponse('<a href="/detail/%s">%s</a> has been added.' % (instance.pk,instance.fn))
        return HttpResponse('<a href="/detail/%s">%s</a> has been updated.' % (instance.pk,instance.fn))
    return HttpResponse(status=404)

def download(request):
    """ Returns all contacts as a CSV file """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts_%s.csv"' % date.today()

    writer = csv.writer(response)
    fields = [r.name for r in Record._meta.get_fields() if r.name != 'note' and r.name != 'id']
    writer.writerow(fields)
    for record in Record.objects.all():
        writer.writerow([getattr(record, field) for field in fields])

    return response