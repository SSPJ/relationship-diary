# Relationship Diary, Seamus Johnston, 2018, GPLv3
from random import choice as randomchoices
from datetime import date, timedelta
from dateutil import parser
import re
import string

from .models import Record

def parse(contact_string):
    contact = {}
    parts = [x.strip() for x in contact_string.split(";")]
    name = parts[0]
    nickname = re.search(r'"([^"]*)"',name)
    if nickname:
        contact['nickname'] = nickname.groups()[0]
        contact['fn'] = re.sub(r'\s?"[^"]*"\s?'," ",name)
    else:
        contact['fn'] = parts[0]
    del parts[0]
    contact['x_pronouns'] = parts[0]
    del parts[0]
    for part in parts:
        try:
            if re.match("birthday", part, re.I) or \
               re.match("born", part, re.I):
                date_raw = part.partition(' ')[2]
                datep = parser.parse(date_raw)
                contact['bday'] = datep if \
                    datep.year != date.today().year else \
                    datep.replace(year=9999)
            elif re.match("anniversary", part, re.I) or \
                 re.match("wedding", part, re.I) or \
                 re.match("married", part, re.I):
                date_raw = part.partition(' ')[2]
                contact['x_anniversary'] = parser.parse(date_raw)
            elif re.match("tel", part, re.I) or \
                 re.match("cell", part, re.I) or \
                 re.sub(r'[^A-Za-z0-9]',"", part).isdigit():
                number = re.sub(r'^(\w\s+)+', "", part)
                contact['tel_cell'] = number
            elif re.match("contact", part, re.I):
                period = part.partition(' ')[2].lower()
                if period == "never":
                    contact['frequency'] = 0
                    contact['next_contact_date'] = date(9999,12,31)
                elif period in ["yearly", "once per year"]:
                    contact['frequency'] = 1
                    contact['next_contact_date'] = Record.get_next_contact_date(1)
                elif period in ["semiannually", "semi-annually", "twice per year", "twice per annum"]:
                    contact['frequency'] = 2
                    contact['next_contact_date'] = Record.get_next_contact_date(2)
                elif period in ["every quarter", "quarterly", "once per quarter"]:
                    contact['frequency'] = 3
                    contact['next_contact_date'] = Record.get_next_contact_date(3)
                elif period in ["every month", "monthly", "once per month"]:
                    contact['frequency'] = 4
                    contact['next_contact_date'] = Record.get_next_contact_date(4)
                elif period in ["twice a month", "biweekly", "twice per month"]:
                    contact['frequency'] = 5
                    contact['next_contact_date'] = Record.get_next_contact_date(5)
                elif period in ["every week", "weekly", "once per week"]:
                    contact['frequency'] = 6
                    contact['next_contact_date'] = Record.get_next_contact_date(6)
                elif period in ["every day", "daily", "once per day"]:
                    contact['frequency'] = 7
                    contact['next_contact_date'] = Record.get_next_contact_date(7)
            elif re.match("org", part, re.I):
                contact['org'] = part.partition(' ')[2]
            elif re.match("title", part, re.I):
                contact['title'] = part.partition(' ')[2]
            elif re.match("categor", part, re.I):
                categories = part.partition(' ')[2]
                contact['categories'] = categories
        except:
            pass

    if 'frequency' not in contact:
        contact['frequency'] = 2
        contact['next_contact_date'] = Record.get_next_contact_date(contact['frequency'])

    return contact

def clean_import(contacts):
    cleaned_contacts = []
    for i, contact in enumerate(contacts):
        parsed = {}
        if 'fn' in contact and contact['fn'] != "":
            parsed['fn'] = contact['fn']
            # mark duplicates, done in view currently
            # for c in contacts[i+1:]:
            #     if c.get('fn',None) == contact['fn']:
            #       parsed['fn'] = contact['fn'] + "_duplicate" + str(i)
            #       break
        elif 'email' in contact:
            parsed['fn'] = contact['email'][0]['value']
        else:
            parsed['fn'] = ''.join(randomchoices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=8))
        parsed['x_pronouns'] = contact.get('x_pronouns', None)
        parsed['org'] = contact.get('org', None)
        parsed['title'] = contact.get('title', None)
        parsed['why'] = contact.get('note', "")
        parsed['x_anniversary'] = contact.get('x_anniversary', None)
        parsed['bday'] = contact.get('bday', None)
        parsed['categories'] = contact.get('categories', None)
        if parsed['categories'] is not None: # space, after, commas
            parsed['categories'] = re.sub(r',([^\s])', r', \1', parsed['categories'])
        parsed['x_phonetic_first_name'] = contact.get('x_phonetic_first_name', None)
        parsed['x_phonetic_last_name'] = contact.get('x_phonetic_last_name', None)
        parsed['nickname'] = contact.get('nickname', None)
        parsed['geo'] = contact.get('geo', None)
        parsed['tz'] = contact.get('tz', None)
        parsed['impp'] = contact.get('impp', None)
        parsed['birthplace'] = contact.get('birthplace', None)

        parsed['frequency'] = contact.get('frequency', 2)
        parsed['next_contact_date'] = contact.get('next_contact_date', date.today() + timedelta(14+i))

        multiple_fields = [
            {'field': 'tel', 'types': ["cell","work","home"]},
            {'field': 'email', 'types': ["personal","work"]},
            {'field': 'adr', 'types': ["home","work"]}]

        for m in multiple_fields:
            if not m['field'] in contact: continue
            for this_one in contact[m['field']]:
                type = this_one.get('type', None)
                if type == "home" and m['field'] == "email": type = "personal"
                field = m['field'] if m['field'] != "adr" else "label"
                parsed_field = '%s_%s' % (field, type)
                parsed_other = '%s_other' % field
                if type in m['types']:
                    if parsed_field not in parsed:
                        parsed[parsed_field] = this_one['value']
                    else:
                        parsed[parsed_field] += ", %s" % this_one['value']
                else:
                    if parsed_other not in parsed:
                        parsed[parsed_other] = this_one['value']
                    else:
                        parsed[parsed_other] += ", %s" % this_one['value']
            del contact[m['field']]

        if 'url' in contact:
            for i, url in enumerate(contact['url']):
                if i > 3: break
                parsed['url_%s' % (i+1)] = contact['url'][i]['value'].replace("\:", ":")
            del contact['url']

        extra_fields = {k:v for k,v in contact.items() if k not in parsed}
        for k,v in extra_fields.items():
          if k not in ['tel','email','adr','label','note']:
              parsed['why'] += "%s: %s -- " % (k,v)

        cleaned_contacts.append(parsed)

    return cleaned_contacts