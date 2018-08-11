# Relationship Diary, Seamus Johnston, 2018, GPLv3
import datetime
try:
    from faker import Faker
except ModuleNotFoundError:
    pass
from random import randint, choice
from django.test import TestCase, Client
from .models import Record
from .helpers import parse, clean_import

def fake_contact(g='f'):
    fake = Faker()
    fake_contact = {}
    cat_choices = ["friends", "professional", "club", "volunteering"]
    m_choices = ["they/them/theirs", "he/him/his", "ze/zir/zirs"]
    f_choices = ["they/them/theirs", "she/her/hers", "ze/zir/zirs"]

    fake_contact['fn'] = fake.name_female() if g=='f' else fake.name_male()
    fake_contact['bday'] = fake.date_between(start_date="-98y", end_date="-15y")
    fake_contact['x_anniversary'] = fake.date_between(start_date="-60y", end_date="-2y")
    fake_contact['frequency'] = randint(0,7)
    fake_contact['tel_cell'] = fake.phone_number()
    fake_contact['tel_work'] = fake.phone_number()
    fake_contact['label_work'] = fake.address()
    fake_contact['email_work'] = fake.safe_email()
    fake_contact['categories'] = choice(cat_choices)
    fake_contact['nickname'] = fake.user_name()
    fake_contact['org'] = fake.company()
    fake_contact['title'] = fake.job()
    fake_contact['x_pronouns'] = choice(f_choices) if g=='f' else choice(m_choices)
    return fake_contact

class RecordModelTestCase(TestCase):

    def setUp(self):
        self.yesterday = datetime.date.today() - datetime.timedelta(1)
        self.contact = Record(fn="Jane Sweet",
            bday=datetime.date.today(),
            x_anniversary=datetime.date.today(),
            next_contact_date=self.yesterday)
        self.contact.save()

    def test_is_birthday_returns_true(self):
        self.assertTrue(self.contact.is_birthday)
    def test_is_anniversary_returns_true(self):
        self.assertTrue(self.contact.is_anniversary)
    def test_is_overdue_returns_true(self):
        self.assertTrue(self.contact.is_overdue)
    def test_get_next_contact_date(self):
        offset = [None,356,178,89,30,15,7,1]
        for x in range(1,8):
            expected = datetime.date.today() + datetime.timedelta(offset[x])
            actual = Record.get_next_contact_date(x)
            self.assertEquals(expected, actual)
        self.assertEquals(datetime.date(9999,12,31), Record.get_next_contact_date(0))

class ParseHelperTestCase(TestCase):

    def setUp(self):
        self.all_parts = "Mary \"Lamb\" Moris; they/them/theirs; born July 17, 1987; married 2007-08-02;" + \
        "cell (734) 683-6402; org A company name; title Is a Job; category friends; contact weekly;"
        self.all_parsed = {'nickname': 'Lamb', 'fn': 'Mary Moris', 'x_pronouns': 'they/them/theirs', 'bday': datetime.datetime(1987, 7, 17, 0, 0), 'x_anniversary': datetime.datetime(2007, 8, 2, 0, 0), 'tel_cell': 'cell (734) 683-6402', 'org': 'A company name', 'title': 'Is a Job', 'categories': 'friends', 'frequency': 6}
        self.missing_frequency = "Mary Moris; they/them/theirs; born July 17, 1987"
        self.missing_frequency_parsed = {'fn': 'Mary Moris', 'x_pronouns': 'they/them/theirs', 'bday': datetime.datetime(1987, 7, 17, 0, 0), 'frequency': 2}
        self.missing_birth_year = "Mary Moris; they/them/theirs; born July 17"
        self.missing_birth_year_parsed = {'fn': 'Mary Moris', 'x_pronouns': 'they/them/theirs', 'bday': datetime.datetime(9999, 7, 17, 0, 0), 'frequency': 2}

    def test_parse_all_parts(self):
        expected = self.all_parsed
        actual = parse(self.all_parts)
        self.assertTrue(isinstance(actual['next_contact_date'],datetime.date))
        del actual['next_contact_date']
        self.assertEquals(expected, actual)

    def test_parse_missing_frequency(self):
        expected = self.missing_frequency_parsed
        actual = parse(self.missing_frequency)
        self.assertTrue(isinstance(actual['next_contact_date'],datetime.date))
        del actual['next_contact_date']
        self.assertEquals(expected, actual)

    def test_parse_missing_birth_year(self):
        expected = self.missing_birth_year_parsed
        actual = parse(self.missing_birth_year)
        self.assertTrue(isinstance(actual['next_contact_date'],datetime.date))
        del actual['next_contact_date']
        self.assertEquals(expected, actual)

class CleanImportTestCase(TestCase):

    def setUp(self):
        self.single_JSON_vcard = [{'fn': 'Dr. John Doe', 'why': 'reasons', 'x_anniversary': '1989-05-10', 'bday': '1970-03-10', 'categories': 'swimmers,bikers', 'x_phonetic_first_name': 'Jooohn', 'x_phonetic_last_name': 'dó', 'nickname': 'Jon,Johnny', 'geo': '39.95;-75.1667', 'tz': '-0500', 'impp': [{'value': 'dude@aim.org'}], 'birthplace': 'Maida Vale, London, England', 'frequency': '1', 'adr': [{'type': 'home', 'value': '  232 Endwv Avenue New York NY 10004 '}, {'type': 'work', 'value': '  6743 Lebbro Street\\, 18th Floor New York NY 10004 '}], 'email': [{'value': 'otherthings@yahoo.com'}, {'type': 'home', 'value': 'example@example.org'}, {'type': 'home', 'value': 'beingathome@gmail.com'}], 'url': [{'value': 'http\\://www.google.com/profiles/madeup'}, {'value': 'archiveofourown.org/users/breathedout/'}], 'x-ablabel': 'PROFILE', 'note': 'A note about things', 'org': 'Spam Detection Squad Foundation', 'tel': [{'type': 'cell', 'value': '(771) 737-8257'}, {'type': 'home', 'value': '+12222557178'}, {'type': 'main', 'value': '+13333651326'}], 'title': 'Janitor', 'x_pronouns': 'ter/tem'}]
        self.cleaned_vcard = [{'fn': 'Dr. John Doe', 'x_pronouns': 'ter/tem', 'org': 'Spam Detection Squad Foundation', 'title': 'Janitor', 'why': 'A note about thingsx-ablabel: PROFILE -- ', 'x_anniversary': '1989-05-10', 'bday': '1970-03-10', 'categories': 'swimmers, bikers', 'x_phonetic_first_name': 'Jooohn', 'x_phonetic_last_name': 'dó', 'nickname': 'Jon,Johnny', 'geo': '39.95;-75.1667', 'tz': '-0500', 'impp': [{'value': 'dude@aim.org'}], 'birthplace': 'Maida Vale, London, England', 'frequency': '1', 'tel_cell': '(771) 737-8257', 'tel_home': '+12222557178', 'tel_other': '+13333651326', 'email_other': 'otherthings@yahoo.com', 'email_personal': 'example@example.org, beingathome@gmail.com', 'label_home': '  232 Endwv Avenue New York NY 10004 ', 'label_work': '  6743 Lebbro Street\\, 18th Floor New York NY 10004 ', 'url_1': 'http://www.google.com/profiles/madeup', 'url_2': 'archiveofourown.org/users/breathedout/'}]
        self.multi_JSON_vcard = [{'fn': '8tracks Support', 'email': [{'value': 'support@8tracks.com'}]}, {'fn': 'Ally Bank Lost Card', 'tel': [{'type': 'cell', 'value': '1-877-247-2559'}]}, {'fn': 'Amtrak Train Status', 'tel': [{'value': '(800) 872-7245'}]}]
        self.cleaned_vcards = [{'fn': '8tracks Support', 'x_pronouns': None, 'org': None, 'title': None, 'why': '', 'x_anniversary': None, 'bday': None, 'categories': None, 'x_phonetic_first_name': None, 'x_phonetic_last_name': None, 'nickname': None, 'geo': None, 'tz': None, 'impp': None, 'birthplace': None, 'frequency': 2, 'email_other': 'support@8tracks.com'}, {'fn': 'Ally Bank Lost Card', 'x_pronouns': None, 'org': None, 'title': None, 'why': '', 'x_anniversary': None, 'bday': None, 'categories': None, 'x_phonetic_first_name': None, 'x_phonetic_last_name': None, 'nickname': None, 'geo': None, 'tz': None, 'impp': None, 'birthplace': None, 'frequency': 2, 'tel_cell': '1-877-247-2559'}, {'fn': 'Amtrak Train Status', 'x_pronouns': None, 'org': None, 'title': None, 'why': '', 'x_anniversary': None, 'bday': None, 'categories': None, 'x_phonetic_first_name': None, 'x_phonetic_last_name': None, 'nickname': None, 'geo': None, 'tz': None, 'impp': None, 'birthplace': None, 'frequency': 2, 'tel_other': '(800) 872-7245'}]
        self.nameless_vcard = [{'fn': '', 'email': [{'value': 'android@duolingo.com'}]}]
        self.cleaned_nameless_vcard = [{'fn': 'android@duolingo.com', 'x_pronouns': None, 'org': None, 'title': None, 'why': '', 'x_anniversary': None, 'bday': None, 'categories': None, 'x_phonetic_first_name': None, 'x_phonetic_last_name': None, 'nickname': None, 'geo': None, 'tz': None, 'impp': None, 'birthplace': None, 'frequency': 2, 'email_other': 'android@duolingo.com'}]

    def test_clean_import_handles_single_JSON_vcard(self):
        expected = self.cleaned_vcard
        actual = clean_import(self.single_JSON_vcard)
        # get_next_contact_date() is tested in RecordModelTestCase, won't test here
        for i in actual: del i['next_contact_date']
        self.assertEquals(expected, actual)

    def test_clean_import_handles_multiple_JSON_vcards(self):
        expected = self.cleaned_vcards
        actual = clean_import(self.multi_JSON_vcard)
        for i in actual: del i['next_contact_date']
        self.assertEquals(expected, actual)

    def test_clean_import_handles_vcard_without_name(self):
        expected = self.cleaned_nameless_vcard
        actual = clean_import(self.nameless_vcard)
        for i in actual: del i['next_contact_date']
        self.assertEquals(expected, actual)
