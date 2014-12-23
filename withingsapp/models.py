import arrow

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from math import pow
from withings import WithingsCredentials, WithingsApi


UserModel = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class WithingsUser(models.Model):
    user = models.OneToOneField(UserModel)
    withings_user_id = models.IntegerField()
    access_token = models.TextField()
    access_token_secret = models.TextField()
    last_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if hasattr(self.user, 'get_username'):
            return self.user.get_username()
        else:  # Django 1.4
            return self.user.username

    def get_user_data(self):
        return {
            'access_token': self.access_token,
            'access_token_secret': self.access_token_secret,
            'user_id': self.withings_user_id
        }


@python_2_unicode_compatible
class MeasureGroup(models.Model):
    non_ambiguous_device = 0
    ambiguous_device = 1
    manual_entry = 2
    manual_creation_entry = 4
    ATTRIB_TYPES = (
        (non_ambiguous_device, 'Captured by a device, not ambiguous'),
        (ambiguous_device, 'Captured by a device, may belong to other user'),
        (manual_entry, 'Manually entered by user'),
        (manual_creation_entry, 'Manually entered, may not be accurate')
    )
    real = 1
    objective = 2
    CATEGORY_TYPES = (
        (real, 'Real measurements'),
        (objective, 'User objectives')
    )
    # For more information about ATTRIB_TYPES and CATEGORY_TYPES:
    # http://oauth.withings.com/api/doc#api-Measure-get_measure

    user = models.ForeignKey(UserModel)
    grpid = models.IntegerField()
    attrib = models.IntegerField(choices=ATTRIB_TYPES)
    date = models.DateTimeField()
    updatetime = models.DateTimeField()
    category = models.IntegerField(choices=CATEGORY_TYPES)

    class Meta:
        unique_together = ('user', 'grpid',)

    def __str__(self):
        return '%s: %s' % (self.date.date().isoformat(),
                           self.get_category_display())

    @classmethod
    def create_from_measures(cls, user, measures):
        for withings_measure in measures:
            if MeasureGroup.objects.filter(grpid=withings_measure.grpid,
                                           user=user).exists():
                continue
            measure_grp = MeasureGroup.objects.create(
                user=user, grpid=withings_measure.grpid,
                attrib=withings_measure.attrib,
                category=withings_measure.category,
                date=withings_measure.date.datetime,
                updatetime=measures.updatetime.datetime)
            for measure in withings_measure.measures:
                Measure.objects.create(
                    group=measure_grp, value=measure['value'],
                    measure_type=measure['type'], unit=measure['unit'])


@python_2_unicode_compatible
class Measure(models.Model):
    weight = 1
    height = 4
    fat_free_mass = 5
    fat_ratio = 6
    fat_mass_weight = 8
    diastolic_bp = 9
    systolic_bp = 10
    heart_pulse = 11
    sp02 = 54
    MEASURE_TYPES = (
        (weight, 'Weight (kg)'),
        (height, 'Height (meter)'),
        (fat_free_mass, 'Fat Free Mass (kg)'),
        (fat_ratio, 'Fat Ratio (%)'),
        (fat_mass_weight, 'Fat Mass Weight (kg)'),
        (diastolic_bp, 'Diastolic Blood Pressure (mmHg)'),
        (systolic_bp, 'Systolic Blood Pressure (mmHg)'),
        (heart_pulse, 'Heart Pulse (bpm)'),
        (sp02, 'SP02(%)'),
    )

    group = models.ForeignKey(MeasureGroup)
    value = models.IntegerField()
    measure_type = models.IntegerField(choices=MEASURE_TYPES)
    unit = models.IntegerField()

    def get_value(self):
        return float(self.value) * pow(10, self.unit)

    def __str__(self):
        return '%s: %s' % (self.get_measure_type_display(), self.get_value())
