from django import template

from withingsapp import utils


register= template.Library()


@register.filter
def is_integrated_with_withings(user):
    """Returns ``True`` if we have Oauth info for the user.

    For example::

        {% if request.user|is_integrated_with_withings %}
            do something
        {% else %}
            do something else
        {% endif %}
    """
    return utils.is_integrated(user)
