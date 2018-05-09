from django.db.transaction import atomic
from django.shortcuts import render, redirect, reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.http import (
    Http404, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse,
)



from .forms import NewFromURLForm
from .models import Podcast, Episode, EpisodePlaybackState, Listener
from .utils import refresh_feed, chunks

import json
import urllib


@require_POST
def podcasts_refresh_feed(request, slug=None):
    podcast = get_object_or_404(Podcast, slug=slug)
    response_data = {}
    response_data['info'] = podcast.update()

    return JsonResponse(response_data)


# @require_POST
# def api_move_or_resize_by_code(request):
#     response_data = {}
#     user = request.user
#     id = request.POST.get('id')
#     existed = bool(request.POST.get('existed') == 'true')
#     delta = datetime.timedelta(minutes=int(request.POST.get('delta')))
#     resize = bool(request.POST.get('resize', False))
#     event_id = request.POST.get('event_id')

#     response_data = _api_move_or_resize_by_code(
#         user,
#         id,
#         existed,
#         delta,
#         resize,
#         event_id)

#     return JsonResponse(response_data)


@atomic
@require_POST
def episodes_mark_played(request, id):
    object = get_object_or_404(Episode, id=id)
    listener, created = Listener.objects.get_or_create(user=request.user)
    if created:
        listener.save()
    state = EpisodePlaybackState(episode=object, listener=listener)
    state.completed = True
    state.save()

    next = request.GET.get('next', reverse('podcasts:podcasts-details', kwargs={'slug': object.podcast.slug}))
    return redirect(next)
