from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site
from django.forms import ModelForm, Form

from podcasts.models import PodcastsSettings
from podcasts.models.listener import Listener
from podcasts.utils import resolve_segments


class NewFromURLForm(Form):
    feed_url = forms.CharField(
        required=False,
        label=_("Feed URL"),
        help_text=_('Named by the format, this is often also called "RSS feed"'),
    )

    opml_file = forms.FileField(
        required=False,
        label=_("OPML File"),
        help_text=_(
            "Many podcast clients allow you to export all you subscriptions at once as an OPML file"
        ),
    )

    class Meta:
        pass

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)


class ListenerSettingsForm(ModelForm):
    subscribed_podcasts = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(),
        label=_(
            "Subscribed Podcasts"
        ),  # Case otherwise not enforced on the model fields verbose_name
        help_text=_(
            "Podcasts checked here will be included in periodic feed refreshes"
        ),
        required=False,  # When all podcasts are deselected, it's technically empty
    )

    class Meta:
        model = Listener
        exclude = [
            "user",
            "interested_podcasts",
            # Exclude all playback settings until feature implemented
            "playback_seek_forward_by",
            "playback_seek_backward_by",
        ]
        help_texts_long = {
            "subscribed_podcasts": _(
                """
                <p>Contains a list of checkboxes for all the podcasts you have
                added to the archive. When a podcast is checked, it is
                'subscribed to' and will therefore be included not only in the
                periodic feed refreshes (i.e. gathering newly published episodes
                ), but also have new episodes downloaded automatically.</p>
                <p>This setting is also available on each podcast's individual
                details page as the <span class="btn btn-outline-secondary
                btn-sm disabled text-dark py-0">Subscribe</span> toggle.</p>
                """
            ),
            "image_security_policy": _(
                """
                <p>More and more podcasts have images in their content / show
                notes section, and not all of them are actual content. In an
                effort to better track listening behavior of users, many
                podcast producers, networks, and feed providers add so-called
                tracking pixels and similiar structures to the show notes.
                Loading those when displaying the notes will reveal personally
                identifying information about you — which we don't like.</p>
                <p>By selecting the 'Allow None' option, all images in show
                notes are replaced with placeholders, that only load images when
                actively clicked on by you. Selecting 'Allow First-Party' will
                enable only the images that come from the podcast's website
                itself, effectively disabling tracking-pixels from the big ad
                networks. If you select 'Allow All' you're becoming fair game —
                all images are loaded, without regard to their source.</p>
                """
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            "subscribed_podcasts"
        ].queryset = self.instance.interested_podcasts.order_by("title")
        if self.fields["subscribed_podcasts"].queryset.count() == 0:
            self.fields["subscribed_podcasts"].help_text = _(
                "(Podcasts you add will appear here to refresh them periodically)"
            )


class AdminSettingsForm(ModelForm):
    naming_scheme = forms.CharField(
        widget=forms.Textarea(attrs={"rows": "4"}),
        help_text="""
            <p class="mb-1">Make the archive structure your own. The following segments are supported:</p>
            <p class="mb-1 naming-scheme-segments"><b>Feed-based segments:</b> {podcast_segments}</p>
            <p class="mb-1 naming-scheme-segments"><b>Episode-based segments:</b> {episode_segments}</p>
            <p>☝️Btw: Click on one of these to add them to the input field above! </p>
            """,
    )

    class Meta:
        model = PodcastsSettings
        exclude = ["site"]
        help_texts_long = {
            "storage_directory": _(
                """
                <p>The Storage Directory is the root of all your downloaded
                podcast episodes. It has to be set once before any episodes are
                downloaded. Changing it later on is not officially supported and
                strongly advised against.</p>
                <p>References to the user's home <code>~</code>, and available
                environment variables like <code>$HOME</code> and
                <code>$USER</code> will be expanded only once before the
                settings are saved.</p>
                """
            ),
            "naming_scheme": _(
                """
                <p>The Episode Naming Scheme is used to create all filenames
                when episodes are downloaded into the archive storage directory.
                The scheme uses <a
                href="https://docs.python.org/3/library/string.html#formatspec">
                Format Specification Mini-Language
                </a> to compile filenames from the available episode and podcast
                properties. The available properties are listed below the field.
                </p>
                <p>Please note that the scheme must contain at least one of
                these segments to ensure a unique name:
                <code>$episode_slug</code>,
                <code>$episode_id</code>,
                <code>$episode_date</code>,
                <code>$episode_number</code>
                </p>
                """
            ),
            "inpath_dateformat": _(
                """
                <p>When using one of the date segments (currently <code>$podcast_updated</code> and <code>$episode_date
                </code>), the format given in the in-path date format will be used to compile the date. The elements in
                the date are also properly localized according to the locale set. The usable format identifiers can be
                found <a href="https://docs.djangoproject.com/en/2.0/ref/templates/builtins/#date" rel="nofollow">here
                in the Django documentation</a>.</p>
                """
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["naming_scheme"].help_text = resolve_segments(
            self.fields["naming_scheme"].help_text
        )
        self.fields["naming_scheme"].label = _("Episode Naming Scheme")


class SiteSettingsForm(ModelForm):
    class Meta:
        model = Site
        exclude = ["name"]
        labels = {"domain": _("Site Domain")}
        help_texts = {
            "domain": _(
                "Will be used to prefix absolute URLs (for example links in emails)"
            )
        }
        help_texts_long = {
            "domain": _(
                """
                <p>The Site Domain is a site-wide setting that affects places
                where an absolute URL of a page is generated. This mostly
                applies to emails sent by the system that contain links to
                pages.</p>
                <p class="mb-0">In case you are running the app in a subfolder
                behind a reverse-proxy, you should include the subfolder in the
                Site Domain to make sure internal (i.e. relative) URLs resolve
                properly:</p>
                <p><code>example.com/fancysubfolder/</code></p>
                """
            )
        }
