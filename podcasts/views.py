from django.db.transaction import atomic
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File

from .forms import NewFromURLForm
from .models import Podcast, Episode
from .utils import refresh_feed

from urllib.parse import urlparse
import urllib
from PIL import Image
from io import BytesIO


# Create your views here.
def index(request):
    return render(request, 'index.html')


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
            object = create_podcast_from_feed_url(
                form.cleaned_data['feed_url'],
                form.cleaned_data['info'])
            return redirect('podcasts:podcasts-details', slug=object.slug)
    else:
        form = NewFromURLForm()

    context = {
        'form': form,
    }
    return render(request, 'podcasts-new.html', context)


def podcasts_details(request, slug):
    object = get_object_or_404(Podcast.objects.prefetch_related('episodes'), slug=slug)
    return render(request, 'podcasts-details.html', {'item': object})


@atomic
def create_podcast_from_feed_url(feed_url, info=None):
        if info is None:
            info = refresh_feed(feed_url)

        episodes = info.pop('episodes', None)
        image = info.pop('image', None)
        object = Podcast(feed_url=feed_url, **info)

        if image is not None:
            insert_podcast_cover(object, image)

        object.save()

        create_episodes_from_podcast(object, info_or_episodes=episodes)
        return object


@atomic
def podcasts_refresh_feed(request, slug):
    object = get_object_or_404(Podcast, slug=slug)
    info = refresh_feed(object.feed_url)
    create_episodes_from_podcast(object, info)

    next = request.GET.get('next', '/')
    return redirect(next)


def insert_podcast_cover(podcast, info_or_img_url=None):
    if info_or_img_url is None:
        img_url = refresh_feed(podcast.feed_url)['image']
    elif isinstance(info_or_img_url, dict):
        img_url = info_or_img_url['image']
    else:
        img_url = info_or_img_url

    name = urlparse(img_url).path.split('/')[-1]
    content, headers = urllib.request.urlretrieve(img_url)

    img_size = getattr(settings, 'COVER_IMAGE_SIZE', (250, 250))

    im = Image.open(content)
    output = BytesIO()

    # Resize the image (from https://djangosnippets.org/snippets/10597/)
    im.thumbnail(img_size)

    # After modifications, save it to the output
    im.save(output, format='JPEG', quality=95)
    output.seek(0)

    # See also: http://docs.djangoproject.com/en/dev/ref/files/file/
    podcast.image.save(name, File(output), save=True)

    return podcast


def create_episodes_from_podcast(podcast, info_or_episodes=None):
    if info_or_episodes is None:
        episodes = refresh_feed(podcast.feed_url)['episodes']
    elif isinstance(info_or_episodes, dict):
        episodes = info_or_episodes['episodes']
    else:
        episodes = info_or_episodes

    objects = (Episode(podcast=podcast, **ep) for ep in episodes)
    Episode.objects.bulk_create(objects)
