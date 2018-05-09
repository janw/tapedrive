from django.db.transaction import atomic
from django.shortcuts import render, redirect, reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import NewFromURLForm
from .models import Podcast, Episode, EpisodePlaybackState, Listener
from .utils import refresh_feed, chunks

import json
import urllib


# Create your views here.
def index(request):
    # return render(request, 'index.html')
    return redirect('podcasts:podcasts-list')


def podcasts_list(request):
    queryset = Podcast.objects.order_by('title')

    paginator = Paginator(queryset, 5)

    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    return render(request, 'podcasts-list.html', {'items': items})


def podcasts_new(request):
    if request.method == 'POST':
        form = NewFromURLForm(request.POST, request.FILES)
        if form.is_valid():
            podcast = Podcast.objects.create_from_feed_url(
                form.cleaned_data['feed_url'],
                form.cleaned_data['info'])
            return redirect('podcasts:podcasts-details', slug=podcast.slug)
    else:
        form = NewFromURLForm()

    context = {
        'form': form,
    }
    return render(request, 'podcasts-new.html', context)


def podcasts_details(request, slug):
    object = get_object_or_404(Podcast.objects.prefetch_related('episodes', 'episodes'), slug=slug)
    episodes = object.episodes.order_by('-published')[:10]
    return render(request, 'podcasts-details.html', {'podcast': object, 'episodes': episodes})


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
    info = refresh_feed(object.feed_url)
    podcast.create_episodes(info)

    next = request.GET.get('next', '/')
    return redirect(next)


def user_settings(request):
    pass
