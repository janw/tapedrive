import os
import re
from string import Template

from django import forms
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from podcasts.utils.properties import ALL_VALID_SEGMENTS
from podcasts.utils.properties import UNIFYING_EPISODE_SEGMENTS


RE_MATCH_POSSIBLE_EXTENSION = re.compile(r".*(\.[0-9a-zA-Z]{1,4})$")
RE_MATCH_ALL_SEGMENTS = re.compile(r"\$(" + Template.idpattern + ")")


def validate_path(path):
    path = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isdir(path):
        raise forms.ValidationError(
            _("Path %(path)s does not exist"), params={"path": path}
        )
    if not os.access(path, os.W_OK):
        raise forms.ValidationError(
            _("Path %(path)s is not writable"), params={"path": path}
        )


def validate_naming_scheme(scheme):
    if "\\" in scheme:
        raise forms.ValidationError(
            _("<p>Backslashes (\\) are not allowed in scheme."),
            params={"scheme": scheme},
        )
    if scheme.startswith("/") or scheme.endswith("/"):
        raise forms.ValidationError(
            _("Scheme must not begin or end with '/'"), params={"scheme": scheme}
        )

    match = RE_MATCH_POSSIBLE_EXTENSION.fullmatch(scheme)
    if match:
        raise forms.ValidationError(
            _("Ending %(possible_extension)s is too similar to a file extension"),
            params={"scheme": scheme, "possible_extension": match.group(1)},
        )

    potential_segments = RE_MATCH_ALL_SEGMENTS.findall(scheme)
    invalid_segments = [s for s in potential_segments if s not in ALL_VALID_SEGMENTS]
    if len(invalid_segments) > 0:
        raise forms.ValidationError(
            ngettext(
                "Segment '%(segments)s' is not a valid segment",
                "Segments '%(segments)s' are not valid segments",
                len(invalid_segments),
            ),
            params={"segments": "', '".join(invalid_segments)},
        )

    unifying_segments = [
        s for s in potential_segments if s in UNIFYING_EPISODE_SEGMENTS
    ]
    if len(unifying_segments) == 0:
        raise forms.ValidationError(
            _("Scheme must contain at least one unifying episode segment"),
            params={"scheme": scheme},
        )
