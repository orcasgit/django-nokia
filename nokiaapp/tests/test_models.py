import arrow

from django.db import IntegrityError
from nokia import NokiaCredentials, NokiaMeasures
from nokiaapp.models import NokiaUser, Measure, MeasureGroup

from .base import NokiaTestBase


class TestNokiaModels(NokiaTestBase):
    def test_nokia_user(self):
        """
        NokiaUser was already created in base, now test the
        properties
        """
        self.assertEqual(self.nokia_user.user, self.user)
        self.assertEqual(self.nokia_user.__str__(), self.username)
        self.assertEqual(self.nokia_user.last_update, None)
        data = self.nokia_user.get_user_data()
        self.assertEqual(type(data), dict)
        self.assertEqual(data['access_token'], self.nokia_user.access_token)
        self.assertEqual(data['access_token_secret'],
                         self.nokia_user.access_token_secret)
        self.assertEqual(data['user_id'], self.nokia_user.nokia_user_id)

    def test_measure_group(self):
        """ Create a MeasureGroup model, check attributes and methods """
        measures = NokiaMeasures({
            "updatetime": 1249409679,
            "measuregrps": [{
                 "grpid": 2909,
                 "attrib": 0,
                 "date": 1222930968,
                 "category": 1,
                 "measures": []
            }]
        })
        self.assertEqual(len(measures), 1)
        measure = measures[0]
        measure_grp = MeasureGroup.objects.create(
            user=self.user, grpid=measure.grpid, attrib=measure.attrib,
            date=measure.date.datetime, category=measure.category,
            updatetime=measures.updatetime.datetime)
        self.assertEqual(measure_grp.__str__(),
                         '2008-10-02: Real measurements')
        self.assertEqual(measure_grp.grpid, 2909)
        self.assertEqual(measure_grp.attrib, 0)
        self.assertEqual(arrow.get(measure_grp.date).timestamp, 1222930968)
        self.assertEqual(arrow.get(measure_grp.updatetime).timestamp,
                         1249409679)
        self.assertEqual(measure_grp.category, 1)
        self.assertEqual(measure_grp.get_attrib_display(),
                         'Captured by a device, not ambiguous')
        self.assertEqual(measure_grp.non_ambiguous_device, measure_grp.attrib)
        self.assertEqual(measure_grp.get_category_display(),
                         'Real measurements')
        self.assertEqual(measure_grp.real, measure_grp.category)

        # Test the create_from_measures function
        MeasureGroup.objects.all().delete()
        measures = self.get_measures
        self.assertEqual(MeasureGroup.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)
        MeasureGroup.create_from_measures(self.user, measures)
        self.assertEqual(MeasureGroup.objects.count(), 3)
        self.assertEqual(Measure.objects.count(), 5)
        self.assertEqual(
            MeasureGroup.objects.get(grpid=2908).measures.count(), 1)
        self.assertEqual(
            MeasureGroup.objects.get(grpid=2909).measures.count(), 1)
        self.assertEqual(
            MeasureGroup.objects.get(grpid=2910).measures.count(), 3)
        # create_from_measures should silently ignore duplicates
        try:
            MeasureGroup.create_from_measures(self.user, measures)
            self.assertEqual(MeasureGroup.objects.count(), 3)
            self.assertEqual(Measure.objects.count(), 5)
        except IntegrityError:
            assert False, 'Not ignoring duplicates'
        # Can't create MeasureGroup with the same user and grpid
        self.assertRaises(IntegrityError, MeasureGroup.objects.create,
            user=self.user, grpid=2908, attrib=1, category=2,
            date=measures[0].date.datetime,
            updatetime=measures.updatetime.datetime)

    def test_measure(self):
        """ Create a Measure model, check attributes and methods """
        nokia_measures = NokiaMeasures({
            "updatetime": 1249409679,
            "measuregrps": [{
                 "grpid": 2909,
                 "attrib": 0,
                 "date": 1222930968,
                 "category": 1,
                 "measures": []
            }]
        })
        nokia_measure = nokia_measures[0]
        measure_grp = MeasureGroup.objects.create(
            user=self.user, grpid=nokia_measure.grpid,
            attrib=nokia_measure.attrib, category=nokia_measure.category,
            date=nokia_measure.date.datetime,
            updatetime=nokia_measures.updatetime.datetime)
        measure = Measure.objects.create(
            group=measure_grp, value=79300, measure_type=1, unit=-3)
        self.assertEqual(measure.__str__(), 'Weight (kg): 79.3')
        self.assertEqual(measure.value, 79300)
        self.assertEqual(measure.measure_type, 1)
        self.assertEqual(measure.unit, -3)
        self.assertEqual(measure.get_value(), 79.3)
        self.assertEqual(measure.get_measure_type_display(), 'Weight (kg)')
        self.assertEqual(measure.weight, 1)
