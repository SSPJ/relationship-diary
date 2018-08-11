# Relationship Diary, Seamus Johnston, 2018, GPLv3
from datetime import date, timedelta
from django.db import models

class Record(models.Model):
    fn = models.CharField(max_length=255, blank=False, null=False, unique=True,
        verbose_name="Full Name", help_text="")
    x_phonetic_first_name = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Phonetic First Name", help_text="")
    x_phonetic_last_name = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Phonetic Last Name", help_text="")
    nickname = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Nickname", help_text="")
    x_pronouns = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Pronouns", help_text="")
    org = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Organization", help_text="")
    # role = models.CharField(max_length=255, null=True, blank=True,
    #     verbose_name="Role", help_text="")
    title = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Job Title", help_text="")
    tel_cell = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Mobile/Cell/Handy", help_text="")
    tel_work = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Work Phone", help_text="")
    tel_home = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Home Phone", help_text="")
    tel_other = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Telephone Other", help_text="")
    label_work = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Work Address", help_text="")
    label_home = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Home Address", help_text="")
    label_other = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Address Other", help_text="")
    email_personal = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Personal Email", help_text="")
    email_work = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Work Email", help_text="")
    email_other = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Email Other", help_text="")
    url_1 = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Url", help_text="")
    url_2 = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Url", help_text="")
    url_3 = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Url", help_text="")
    url_4 = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Url", help_text="")
    bday = models.DateField(null=True, blank=True,
        verbose_name="Birthday", help_text="A date in YYYY-MM-DD format")
    x_anniversary = models.DateField(null=True, blank=True,
        verbose_name="Anniversary", help_text="A date in YYYY-MM-DD format")
    geo = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Geolocation", help_text="A set of coordinates, such as 39.95;-75.1667")
    tz = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Timezone", help_text="A timezone, such as -0500")
    impp = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="IMPP", help_text="")
    birthplace = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Birthplace", help_text="")
    why = models.TextField(null=True, blank=True,
        verbose_name="Why is this person in the address book?", help_text="")
    categories = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Categories", help_text="A comma separated list of categories")
    rev = models.DateTimeField(auto_now=True,
        verbose_name="Revised", help_text="")
    created = models.DateTimeField(auto_now_add=True,
        verbose_name="Created", help_text="")
    next_contact_date = models.DateField(null=True, blank=True,
        verbose_name="Next Contact Date", help_text="A date in YYYY-MM-DD format")
    FREQUENCY_CHOICES = (
      (0, "Never"),
      (1, "Yearly"),
      (2, "Twice per annum"),
      (3, "Quarterly"),
      (4, "Monthly"),
      (5, "Biweekly"),
      (6, "Weekly"),
      (7, "Daily"),
    )
    frequency = models.PositiveSmallIntegerField(choices=FREQUENCY_CHOICES, default=2,
        verbose_name="Desired Frequency of Contact", help_text="")

    def save(self, *args, **kwargs):
        if self.categories:
            Category.string_to_db(self.categories)
        super(Record, self).save(*args, **kwargs)

    @property
    def is_birthday(self):
        if self.bday:
            return date.today().month == self.bday.month \
                and date.today().day == self.bday.day
        else:
            return False

    @property
    def is_anniversary(self):
        if self.x_anniversary:
            return date.today().month == self.x_anniversary.month \
                and date.today().day == self.x_anniversary.day
        else:
            return False

    @property
    def is_overdue(self):
        return self.next_contact_date and self.next_contact_date < date.today()

    @classmethod
    def get_next_contact_date(cls, frequency):
        if frequency == 0:
            return date(9999,12,31)
        if frequency == 1:
            return date.today() + timedelta(356)
        if frequency == 2:
            return date.today() + timedelta(178)
        if frequency == 3:
            return date.today() + timedelta(89)
        if frequency == 4:
            return date.today() + timedelta(30)
        if frequency == 5:
            return date.today() + timedelta(15)
        if frequency == 6:
            return date.today() + timedelta(7)
        if frequency == 7:
            return date.today() + timedelta(1)

class Note(models.Model):
    record = models.ForeignKey('Record', on_delete=models.CASCADE, related_name='note')
    date = models.DateField(auto_now=True)
    note = models.TextField(null=True, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, db_index=True)

    @classmethod
    def string_to_db(cls,string):
        for c in string.split(','):
            obj, created = Category.objects.get_or_create(name=c.strip().lower())
            if created:
                obj.save()