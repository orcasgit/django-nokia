import arrow

from django.core.urlresolvers import reverse
from freezegun import freeze_time

from nokia import NokiaMeasures

from nokiaapp.models import NokiaUser, MeasureGroup, Measure

from .base import NokiaTestBase

try:
    from unittest import mock
except ImportError:  # Python 2.x fallback
    import mock


class TestRetrievalTask(NokiaTestBase):
    def setUp(self):
        super(TestRetrievalTask, self).setUp()
        self.startdate = 1222930967
        self.enddate = 1222930969
        self.nokia_measures = {
            "updatetime": 1249409679,
            "measuregrps": [{
                "grpid": 2909,
                "attrib": 0,
                "date": 1222930968,
                "category": 1,
                "measures": [{
                    "value": 79300,
                    "type": 1,
                    "unit": -3
                }]
            }, {
                "grpid": 2910,
                "attrib": 1,
                "date": 1222930968,
                "category": 1,
                "measures": [{
                    "value": 652,
                    "type": 5,
                    "unit": -1
                }, {
                    "value": 178,
                    "type": 6,
                    "unit": -1
                }, {
                    "value": 14125,
                    "type": 8,
                    "unit": -3
                }]
            }, {
                "grpid": 2908,
                "attrib": 0,
                "date": 1222930968,
                "category": 1,
                "measures": [{
                    "value": 173,
                    "type": 4,
                    "unit": -2
                }]
            }]
        }

    def _receive_nokia_notification(self, status_code=204):
        post_params = {
            'userid': self.nokia_user.nokia_user_id,
            'startdate': self.startdate,
            'enddate': self.enddate
        }
        res = self.client.post(
            reverse('nokia-notification', kwargs={'appli': 1}),
            data=post_params)
        self.assertEqual(res.status_code, status_code)

    def test_notification_get(self):
        res = self.client.get(
            reverse('nokia-notification', kwargs={'appli': 1}))

        self.assertEqual(res.status_code, 404)

    def test_notification_head(self):
        res = self.client.head(
            reverse('nokia-notification', kwargs={'appli': 1}))

        self.assertEqual(res.status_code, 200)

    @freeze_time("2012-01-14T12:00:01", tz_offset=-6)
    @mock.patch('nokiaapp.utils.get_nokia_data')
    def test_notification(self, get_nokia_data):
        # Check that data is created when a notification is received from Nokia
        get_nokia_data.return_value = NokiaMeasures(self.nokia_measures)
        self.assertEqual(self.nokia_user.last_update, None)
        self.assertEqual(MeasureGroup.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)
        self._receive_nokia_notification()
        self.assertEqual(get_nokia_data.call_count, 1)
        self.nokia_user = NokiaUser.objects.get(id=self.nokia_user.id)
        self.assertEqual(self.nokia_user.last_update.isoformat(),
                         "2012-01-14T12:00:01+00:00")
        self.assertEqual(MeasureGroup.objects.count(), 3)
        self.assertEqual(Measure.objects.count(), 5)
        startdate = arrow.get(self.startdate).datetime
        enddate = arrow.get(self.enddate).datetime
        measure_grps = MeasureGroup.objects.filter(
            user=self.user, date__gte=startdate, date__lte=enddate)
        self.assertEqual(measure_grps.count(), 3)

    @freeze_time("2012-01-14T12:00:01", tz_offset=-6)
    @mock.patch('nokiaapp.utils.get_nokia_data')
    def test_notification_multi_user_with_error(self, get_nokia_data):
        # Check that the notification handler gracefully handles errors
        get_nokia_data.side_effect = [
            Exception("Error code 283"),
            NokiaMeasures(self.nokia_measures),
        ]
        user2 = self.create_user(username=self.username + '2',
                                 password=self.password)
        nokia_user2 = self.create_nokia_user(user=user2)
        nokia_user2.nokia_user_id = self.nokia_user.nokia_user_id
        nokia_user2.save()

        self.assertEqual(self.nokia_user.last_update, None)
        self.assertEqual(MeasureGroup.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)

        self._receive_nokia_notification()

        self.assertEqual(get_nokia_data.call_count, 2)
        # Only one of the users should have received data
        self.assertEqual(MeasureGroup.objects.count(), 3)
        self.assertEqual(Measure.objects.count(), 5)
        self.assertEqual(MeasureGroup.objects.count(), 3)

    def test_notification_error(self):
        res = self.client.post(
            reverse('nokia-notification', kwargs={'appli': 4}))
        self.assertEqual(res.status_code, 404)
