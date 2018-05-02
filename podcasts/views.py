from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .models import Podcast


# Create your views here.
def index(request):
    return render(request, 'index.html')


def podcasts_list(request):
    queryset = Podcast.objects.all()

    paginator = Paginator(queryset, 2)

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
