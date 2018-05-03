from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File

from .forms import NewFromURLForm
from .models import Podcast
from .utils import refresh_feed

from urllib.parse import urlparse
import urllib
from PIL import Image
from io import BytesIO
import sys


# Create your views here.
def index(request):
    return render(request, 'index.html')


def podcasts_list(request):
    queryset = Podcast.objects.all()

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
        object = Podcast()
        form = NewFromURLForm(request.POST, request.FILES, instance=object)

        if form.is_valid():
            form.instance = podcasts_refresh_new_feed(form.instance)
            form.save()
            return redirect('podcasts:podcasts-details', slug=object.slug)
    else:
        object = Podcast()
        form = NewFromURLForm(instance=object)

    context = {
        'form': form,
    }
    return render(request, 'podcasts-new.html', context)


def podcasts_details(request, slug):
    object = get_object_or_404(Podcast.objects.prefetch_related('episodes'), slug=slug)
    return render(request, 'podcasts-details.html', {'item': object})


def podcasts_refresh_feed(request, slug):
    object = get_object_or_404(Podcast, slug=slug)
    podcasts_refresh_new_feed(object)

    next = request.GET.get('next', '/')
    return redirect(next)


def podcasts_refresh_new_feed(object):
    info = refresh_feed(object.feed_url)

    for key, value in info.items():
        if key == 'image':
            img_url = value
            print(img_url)
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
            object.image.save(name, File(output), save=True)
        elif key == 'episodes':
            pass
        else:
            print(key)
            print(value)
            object.__setattr__(key, value)

    return object

