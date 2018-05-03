from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.template.defaultfilters import slugify

from .models import Podcast
from .utils import refresh_feed
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
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.save()
        return instance

    def clean(self):
        super().clean()

        self.cleaned_data['info'] = refresh_feed(self.cleaned_data['feed_url'])

        if self.cleaned_data['info'] is None:
            raise forms.ValidationError(_('The URL did not return a valid podcast feed'))

        return self.cleaned_data
