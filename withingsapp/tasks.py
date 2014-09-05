from __future__ import absolute_import

import logging

from celery import shared_task
from django.utils import timezone

from . import utils
from .models import WithingsUser, MeasureGroup


logger = logging.getLogger(__name__)


@shared_task
def update_withings_data_task(user_id):
    logger.debug("WITHINGS DATA TASK")
    try:
        for u in WithingsUser.objects.filter(withings_user_id=user_id):
            kwargs = {'lastupdate': u.last_update} if u.last_update else {}
            measures = utils.get_withings_data(**kwargs)
            MeasureGroup.create_from_measures(u.user, measures)
            u.last_update = timezone.now()
            u.save()
    except:
        logger.exception("Exception creating withings measures")
        raise
    logger.debug("WITHINGS DATA UPDATED")
