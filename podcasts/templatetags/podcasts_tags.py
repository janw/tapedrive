from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
register = template.Library()


@register.simple_tag(takes_context=True)
def add_active(context, name, by_path=False):
    """ Return the string 'active' current request.path is same as name

    Keyword aruguments:
    request  -- Django request object
    name     -- name of the url or the actual path
    by_path  -- True if name contains a url instead of url name
    """
    if by_path:
        path = name
    else:
        path = reverse(name)

    if context.request.path == path:
        return 'active'

    return ''
