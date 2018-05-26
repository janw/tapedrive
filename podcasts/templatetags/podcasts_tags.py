from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language_from_request
from urllib.parse import urlparse
from langcodes import Language
import os

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
        path = parsed.path.rstrip('/')
        splits = str.split(path, '/')
        if len(splits) > 2:
            path = '/…/' + splits[-1]

        return netloc + path
    else:
        return netloc


@register.simple_tag(takes_context=True)
def resolve_language(context, language_tag):
    lang = Language.get(language_tag)
    request_language = get_language_from_request(context['request'])
    return lang.language_name(request_language)


@register.inclusion_tag('podcasts/_field_help_long.html', takes_context=True)
def field_help_long(context, form, field, html_parent='accordion', show_initially=False):
    context['html_parent'] = html_parent
    context['show_initially'] = show_initially
    context['no_help'] = False

    help_texts = getattr(form.Meta, 'help_texts_long', {})
    if field.name in help_texts:
        context['id'] = field.name
        context['label'] = field.label
        context['help_text'] = help_texts[field.name]
    else:
        context['no_help'] = True

    return context


@register.simple_tag(takes_context=False)
def jsr_var(variable):
    return '{{:%s}}' % variable


@register.simple_tag(takes_context=False)
def jsr_if(condition):
    return mark_safe('{{if %s }}' % condition)


@register.simple_tag(takes_context=False)
def jsr_endif():
    return '{{/if}}'


@register.simple_tag(takes_context=False)
def jsr_for(indexed):
    return mark_safe('{{for %s }}' % indexed)


@register.simple_tag(takes_context=False)
def jsr_endfor():
    return '{{/for}}'


@register.simple_tag(takes_context=False)
def css_spinner(id, hidden=True):
    display = ''
    if hidden is True:
        display = 'display:none;'
    return format_html("""
<div id="{}" class="sk-fading-circle" style="{}">
  <div class="sk-circle1 sk-circle"></div> <div class="sk-circle2 sk-circle"></div>
  <div class="sk-circle3 sk-circle"></div> <div class="sk-circle4 sk-circle"></div>
  <div class="sk-circle5 sk-circle"></div> <div class="sk-circle6 sk-circle"></div>
  <div class="sk-circle7 sk-circle"></div> <div class="sk-circle8 sk-circle"></div>
  <div class="sk-circle9 sk-circle"></div> <div class="sk-circle10 sk-circle"></div>
  <div class="sk-circle11 sk-circle"></div> <div class="sk-circle12 sk-circle"></div>
</div>
    """, id, display)
