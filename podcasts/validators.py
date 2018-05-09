from django import forms
from django.utils.translation import gettext as _

import os


def validate_path(path):
    path = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isdir(path):
        raise forms.ValidationError(_('Path %(path)s does not exist'),
                                    params={'path': path})
    if not os.access(path, os.W_OK):
        raise forms.ValidationError(_('Path %(path)s is not writable'),
                                    params={'path': path})
