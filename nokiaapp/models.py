import arrow

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from math import pow


UserModel = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class NokiaUser(models.Model):
    """ A user's Nokia credentials, allowing API access """
    user = models.OneToOneField(UserModel, help_text='The user')
    nokia_user_id = models.IntegerField(help_text='The nokia user ID')
    access_token = models.TextField(help_text='OAuth access token')
    access_token_secret = models.TextField(
        help_text='OAuth access token secret')
    last_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The datetime the user's nokia data was last updated")

    def __str__(self):
        if hasattr(self.user, 'get_username'):
            return self.user.get_username()
        else:  # Django 1.4
            return self.user.username

    def get_user_data(self):
        return {
            'access_token': self.access_token,
            'access_token_secret': self.access_token_secret,
            'user_id': self.nokia_user_id
        }


@python_2_unicode_compatible
class MeasureGroup(models.Model):
    """
    A group of measurements, i.e. Diastolic/Systolic blood pressure:
    http://oauth.nokia.com/api/doc#api-Measure-get_measure
    """
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

    user = models.ForeignKey(UserModel, help_text="The group's user")
    grpid = models.IntegerField(help_text='The group ID, assigned by nokia')
    attrib = models.IntegerField(
        choices=ATTRIB_TYPES,
        help_text="The group's attribution, one of: {}".format(
            ', '.join(['{} ({})'.format(ci, cs) for ci, cs in ATTRIB_TYPES])
        ))
    date = models.DateTimeField(help_text='The datetime of the measurement(s)')
    updatetime = models.DateTimeField(
        help_text='The last updated datetime of the measurement(s)')
    category = models.IntegerField(
        choices=CATEGORY_TYPES,
        help_text="The group's category, one of: {}".format(
            ', '.join(['{} ({})'.format(ci, cs) for ci, cs in CATEGORY_TYPES])
        ))

    class Meta:
        unique_together = ('user', 'grpid',)

    def __str__(self):
        return '%s: %s' % (self.date.date().isoformat() if self.date else None,
                           self.get_category_display())

    @classmethod
    def create_from_measures(cls, user, measures):
        for nokia_measure in measures:
            if MeasureGroup.objects.filter(grpid=nokia_measure.grpid,
                                           user=user).exists():
                continue
            measure_grp = MeasureGroup.objects.create(
                user=user, grpid=nokia_measure.grpid,
                attrib=nokia_measure.attrib,
                category=nokia_measure.category,
                date=nokia_measure.date.datetime,
                updatetime=measures.updatetime.datetime)
            for measure in nokia_measure.measures:
                Measure.objects.create(
                    group=measure_grp, value=measure['value'],
                    measure_type=measure['type'], unit=measure['unit'])


@python_2_unicode_compatible
class Measure(models.Model):
    """
    A body measurement:
    http://oauth.nokia.com/api/doc#api-Measure-get_measure
    """
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

    group = models.ForeignKey(
        MeasureGroup,
        related_name='measures',
        help_text="The measurement's group")
    value = models.IntegerField(
        help_text=(
            'Value for the measure in S.I units (kilogram, meters, etc.). '
            'Value should be multiplied by 10 to the power of "unit" to get '
            'the real value.'
        ))
    measure_type = models.IntegerField(
        choices=MEASURE_TYPES,
        help_text="The measurement's type, one of: {}".format(
            ', '.join(['{} ({})'.format(ci, cs) for ci, cs in MEASURE_TYPES])
        ))
    unit = models.IntegerField(
        help_text=(
            'Power of ten the "value" attribute should be multiplied to to '
            'get the real value. Eg : value = 20 and unit=-1 means the value '
            'really is 2.0'
        ))

    def get_value(self):
        return float(self.value) * pow(10, self.unit)

    def __str__(self):
        return '%s: %s' % (self.get_measure_type_display(), self.get_value())
