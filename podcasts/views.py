from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Max, Case, When
from django.views.generic.list import ListView

from podcasts.conf import * # noqa
from podcasts.forms import NewFromURLForm, ListenerSettingsForm, AdminSettingsForm, SiteSettingsForm
from podcasts.models.podcast import Podcast
from podcasts.utils import refresh_feed, chunks, handle_uploaded_file, parse_opml_file

import json
import urllib


# Create your views here.
def index(request):
    # return render(request, 'index.html')
    return redirect('podcasts:podcasts-list')


class PodcastsList(ListView):
    model = Podcast
    paginate_by = PODCASTS_PER_PAGE
    template_name = 'podcasts-list.html'

    def get_queryset(self, **kwargs):
        user_ordering = self.request.user.listener.sort_order_podcasts
        queryset = (
            Podcast.objects
            .prefetch_related('subscribers', 'subscribers')
            .prefetch_related('followers', 'followers')
            .annotate(num_episodes=Count('episodes'))
            .annotate(downloaded_episodes=Count(Case(
                When(episodes__downloaded__isnull=False, then=1))))
            .annotate(last_episode_date=Max('episodes__published'))
            .filter(followers=self.request.user.listener)
            .order_by(user_ordering)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def podcasts_new(request):
    if request.method == 'POST':
        form = NewFromURLForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            if form.cleaned_data['feed_url']:
                podcast, created = Podcast.objects.get_or_create_from_feed_url(
                    form.cleaned_data['feed_url'],
                )
                podcast.add_subscriber(request.user.listener)
                podcast.add_follower(request.user.listener)

            if 'opml_file' in request.FILES:
                tempfile = handle_uploaded_file(request.FILES['opml_file'])
                feeds = parse_opml_file(tempfile)

                for feed in feeds:
                    podcast, created = Podcast.objects.get_or_create_from_feed_url(feed)
                    if podcast is not None:
                        podcast.add_subscriber(request.user.listener)
                        podcast.add_follower(request.user.listener)

            if form.cleaned_data['feed_url'] and not form.cleaned_data['opml_file']:
                return redirect('podcasts:podcasts-details', slug=podcast.slug)
            else:
                return redirect('podcasts:podcasts-list')

    else:
        form = NewFromURLForm()

    context = {
        'form': form,
    }
    return render(request, 'podcasts-new.html', context)


def podcasts_details(request, slug):
    podcast = get_object_or_404((
        Podcast.objects
        .prefetch_related('episodes', 'episodes')
        .prefetch_related('subscribers', 'subscribers'))
        .annotate(num_episodes=Count('episodes'))
        .annotate(downloaded_episodes=Count(Case(
            When(episodes__downloaded__isnull=False, then=1))))
        .annotate(last_episode_date=Max('episodes__published')),
        slug=slug)

    user_ordering = request.user.listener.sort_order_episodes

    user_is_subscriber = podcast.subscribers.filter(user=request.user).exists()
    episodes = podcast.episodes.order_by(user_ordering)[:10]

    context = {
        'user_is_subscriber': user_is_subscriber,
        'podcast': podcast,
        'episodes': episodes,
    }
    return render(request, 'podcasts-details.html', context)


def podcasts_discover(request):
    url = 'https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/25/explicit.json'
    file, header = urllib.request.urlretrieve(url)

    if header['Status'] == '200 OK':
        with open(file) as fp:
            content = json.load(fp)
        feeds = list(chunks(content['feed']['results'], 3))

        context = {
            'content': content,
            'feeds': feeds
        }
        # print(urllib.request.urlretrieve(url)[0])
    else:
        context = {}
    return render(request, 'podcasts-discover.html', context)


def podcasts_refresh_feed(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    podcast.update(update_all=True)
    next = request.GET.get('next', '/')
    return redirect(next)


def settings(request):
    current_site_settings = get_current_site(request)
    current_podcasts_settings = current_site_settings.podcastssettings
    if request.method == 'POST':
        listener_form = ListenerSettingsForm(
            request.POST,
            request.FILES,
            instance=request.user.listener,
            prefix='listener')
        app_admin_form = AdminSettingsForm(
            request.POST,
            request.FILES,
            instance=current_podcasts_settings,
            prefix='app')
        site_admin_form = SiteSettingsForm(
            request.POST,
            request.FILES,
            instance=current_site_settings,
            prefix='site')

        if listener_form.is_valid() and (not request.user.is_superuser or (app_admin_form.is_valid() and site_admin_form.is_valid())):
            listener_form.save()
            app_admin_form.save()
            site_admin_form.save()

            next = request.GET.get('next', '/')
            return redirect(next)
    else:
        listener_form = ListenerSettingsForm(
            instance=request.user.listener,
            prefix='listener')
        app_admin_form = AdminSettingsForm(
            instance=current_podcasts_settings,
            prefix='app')
        site_admin_form = SiteSettingsForm(
            instance=current_site_settings,
            prefix='site')

    return render(request, 'podcasts-settings.html', {'listener_form': listener_form,
                                                      'app_admin_form': app_admin_form,
                                                      'site_admin_form': site_admin_form})
