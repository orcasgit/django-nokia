import arrow
import json

from datetime import datetime
from django.core.urlresolvers import reverse
from freezegun import freeze_time

from withings import WithingsApi, WithingsMeasures

from withingsapp import utils
from withingsapp.models import WithingsUser, MeasureGroup, Measure

from .base import WithingsTestBase

try:
    from unittest import mock
except ImportError:  # Python 2.x fallback
    import mock


class TestRetrievalTask(WithingsTestBase):
    def setUp(self):
        super(TestRetrievalTask, self).setUp()
        self.startdate = 1222930967
        self.enddate = 1222930969

    def _receive_withings_notification(self, status_code=204):
        post_params = {
            'userid': self.withings_user.withings_user_id,
            'startdate': self.startdate,
            'enddate': self.enddate
        }
        res = self.client.post(
            reverse('withings-notification', kwargs={'appli': 1}),
            data=post_params)
        self.assertEqual(res.status_code, status_code)

    @freeze_time("2012-01-14T12:00:01", tz_offset=-6)
    @mock.patch('withingsapp.utils.get_withings_data')
    def test_notification(self, get_withings_data):
        # Check that celery tasks get made when a notification is received
        # from Withings.
        get_withings_data.return_value = WithingsMeasures({
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
            },
            {
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
        })
        self.assertEqual(self.withings_user.last_update, None)
        self.assertEqual(MeasureGroup.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)
        self._receive_withings_notification()
        self.assertEqual(get_withings_data.call_count, 1)
        self.withings_user = WithingsUser.objects.get(id=self.withings_user.id)
        self.assertEqual(self.withings_user.last_update.isoformat(),
                         "2012-01-14T12:00:01+00:00")
        self.assertEqual(MeasureGroup.objects.count(), 3)
        self.assertEqual(Measure.objects.count(), 5)
        startdate = arrow.get(self.startdate).datetime
        enddate = arrow.get(self.enddate).datetime
        measure_grps = MeasureGroup.objects.filter(
            user=self.user, date__gte=startdate, date__lte=enddate)
        self.assertEqual(measure_grps.count(), 3)

    def test_notification_error(self):
        res = self.client.post(
            reverse('withings-notification', kwargs={'appli': 4}))
        self.assertEqual(res.status_code, 404)
