from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.template.defaultfilters import slugify

from .models import Podcast

import itertools


class NewFromURLForm(ModelForm):
    class Meta:
        model = Podcast
        fields = ['feed_url', ]

    def save(self):
        instance = super().save(commit=False)

        max_length = Podcast._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.title)

        for x in itertools.count(1):
            if not Podcast.objects.filter(slug=instance.slug).exists():
                break
            instance.slug = '%s-%d' % (orig, x)
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.save()
