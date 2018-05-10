from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ModelForm, Form
from django.template.defaultfilters import slugify

from .models import Podcast, Listener, PodcastsSettings
from .utils import refresh_feed
import itertools
import os


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


class ListenerSettingsForm(ModelForm):
    subscribed_podcasts = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(),
        label=_('Subscribed Podcasts'),  # Case otherwise not enforced on the model fields verbose_name
        help_text=_('Podcasts checked here will be included in periodic feed refreshes'),
        required=False,  # When all podcasts are deselected, it's technically empty
    )

    class Meta:
        model = Listener
        exclude = [
            'user',
            'interested_podcasts',

            # Exclude all playback settings until feature implemented
            'playback_seek_forward_by',
            'playback_seek_backward_by',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['subscribed_podcasts'].queryset = self.instance.interested_podcasts.order_by('title')
        if self.fields['subscribed_podcasts'].queryset.count() == 0:
            self.fields['subscribed_podcasts'].help_text = _(
                '(Podcasts you add will appear here to refresh them periodically)')


class AdminSettingsForm(ModelForm):
    test = forms.CharField(required=False)
    pub_date = forms.DateField(required=False)

    class Meta:
        model = PodcastsSettings
        exclude = []

    def save(self):
        instance = super().save(commit=False)
        instance.storage_directory = os.path.expanduser(os.path.expandvars(instance.storage_directory))
        # Workaound for default site missing its settings instance
        # PodcastsSettings.objects.get_or_create(site=instance)

        instance.save()
        return instance
