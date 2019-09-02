import json
import re
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.json import Deserializer
from django.contrib.postgres.fields import JSONField

timedelta_re = re.compile(
    r"^-?P(?P<days>\d+)DT(?P<hours>\d+)H(?P<minutes>\d+)M(?P<seconds>[\d\.]+)S$"
)


def to_numerics(groupdict):
    return {key: float(value) for key, value in groupdict.items()}


def convert_to_timedelta(string):
    td = timedelta(**to_numerics(timedelta_re.match(string).groupdict()))
    if string.startswith("-"):
        td *= -1
    return td


def parse_chapter_list(chlist):

    for entry in chlist:
        if not isinstance(entry, dict):
            continue
        if "starttime" in entry:
            entry["starttime"] = convert_to_timedelta(entry["starttime"])

    return chlist


# class ChaptersJSONField(JSONField):
#     def from_db_value(self, value, expression, connection):
#         if not isinstance(value, list):
#             return value

#         return parse_chapter_list(value)
