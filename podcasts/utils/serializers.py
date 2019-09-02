import datetime

from django.core.serializers.json import DjangoJSONEncoder


class PodcastsJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.timedelta):
            return round(o.total_seconds() * 1000)
        else:
            return super().default(o)
