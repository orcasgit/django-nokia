from django import template

from nokiaapp import utils


register= template.Library()


@register.filter
def is_integrated_with_nokia(user):
    """Returns ``True`` if we have Oauth info for the user.

    For example::

        {% if request.user|is_integrated_with_nokia %}
            do something
        {% else %}
            do something else
        {% endif %}
    """
    return utils.is_integrated(user)
