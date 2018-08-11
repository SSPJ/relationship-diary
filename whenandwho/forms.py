# Relationship Diary, Seamus Johnston, 2018, GPLv3
from datetime import date, timedelta

from django.forms import ModelForm, CharField, Textarea, formset_factory, modelformset_factory
from whenandwho.models import Record

record_fields = ['fn', 'x_pronouns', 'org', 'title', 'why', 
    'tel_cell', 'email_personal', 'email_work', 'label_home', 'url_1', 'bday',
    'categories', 'frequency', 'next_contact_date',
    'x_phonetic_first_name', 'x_phonetic_last_name', 
    'nickname', 'tel_work', 'tel_home', 'tel_other', 'label_work', 
    'label_other', 'email_other',
    'url_2', 'url_3', 'url_4', 
    'x_anniversary', 'geo', 'tz', 'impp', 'birthplace']

record_widgets = {
    'label_work': Textarea(attrs={'class': 'textarea--two-line'}),
    'label_home': Textarea(attrs={'class': 'textarea--two-line'}),
    'label_other': Textarea(attrs={'class': 'textarea--two-line'}),
    'categories': Textarea(attrs={'class': 'textarea--two-line'}),
    'why': Textarea(attrs={'class': 'textarea--two-line'}),
}

class ContactModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContactModelForm,self).__init__(*args, **kwargs)
        self.fields['next_contact_date'].initial = date.today() + timedelta(178)

    class Meta:
        model = Record
        widgets = record_widgets
        fields = record_fields

ContactFormSet = formset_factory(
    ContactModelForm,
    extra=0)