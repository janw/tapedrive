from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language_from_request
from urllib.parse import urlparse
from langcodes import Language

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


@register.simple_tag(takes_context=True)
def add_next_self(context):
    return "?next=%s" % context.request.path


@register.simple_tag(takes_context=False)
def clean_link(link, include_path=True):
    parsed = urlparse(link)
    netloc = parsed.netloc.lstrip('www.')

    if include_path:
        return netloc + parsed.path
    else:
        return netloc


@register.simple_tag(takes_context=True)
def resolve_language(context, language_tag):
    lang = Language.get(language_tag)
    request_language = get_language_from_request(context['request'])
    return lang.language_name(request_language)
