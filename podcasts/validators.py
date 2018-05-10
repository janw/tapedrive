from django import forms
from django.utils.translation import gettext as _

from .utils import (AVAILABLE_PODCAST_SEGMENTS,
                    AVAILABLE_EPISODE_SEGMENTS,
                    UNIFYING_EPISODE_SEGMENTS)

import os
import re


RE_MATCH_POSSIBLE_EXTENSION = re.compile(r'.*(\.[0-9a-zA-Z]{1,4})$')
RE_MATCH_EPISODE_SEGMENT = re.compile(r'\{episode\_\w+\}')


def validate_path(path):
    path = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isdir(path):
        raise forms.ValidationError(_('Path %(path)s does not exist'),
                                    params={'path': path})
    if not os.access(path, os.W_OK):
        raise forms.ValidationError(_('Path %(path)s is not writable'),
                                    params={'path': path})


def validate_naming_scheme(scheme):
    if '\\' in scheme:
        raise forms.ValidationError(_('<p>Backslashes are not allowed in the scheme. Use slashes for directory separators even on Windows'),
                                    params={'scheme': scheme})
    if scheme.startswith('/'):
        raise forms.ValidationError(_('Scheme must not begin with \'/\', must be relative'),
                                    params={'scheme': scheme})
    if scheme.endswith('/'):
        raise forms.ValidationError(_('Scheme must not end with  \'/\', must end in basename of episode file'),
                                    params={'scheme': scheme})

    match = RE_MATCH_POSSIBLE_EXTENSION.fullmatch(scheme)
    if match:
        raise forms.ValidationError(_('Ending %(possible_extension)s is too similar to a file extension'),
                                    params={'scheme': scheme, 'possible_extension': match.group(1)})
    episode_segments = RE_MATCH_EPISODE_SEGMENT.findall(scheme)
    if len(episode_segments) == 0:
        raise forms.ValidationError(_('Scheme must contain at least one episode segment'),
                                    params={'scheme': scheme})
