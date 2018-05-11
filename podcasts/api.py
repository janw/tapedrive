from django.db.transaction import atomic
from django.shortcuts import redirect, reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.http import (
    Http404, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse,
    HttpResponseForbidden, HttpResponse
)

from podcasts.models.listener import EpisodePlaybackState, Listener
from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode


class HttpResponseNoContent(HttpResponse):
    status_code = 204


def podcast_refresh_feed(request, slug=None):
    podcast = get_object_or_404(Podcast, slug=slug)
    response_data = {}
    response_data['info'] = podcast.update()

    return JsonResponse(response_data)


def podcast_subscribe(request, slug=None):
    if request.user is None:
        return HttpResponseForbidden
    podcast = get_object_or_404(Podcast, slug=slug)
    podcast.add_subscriber(request.user.listener)
    podcast.save()
    return HttpResponseNoContent()


def podcast_unsubscribe(request, slug=None):
    if request.user is None:
        return HttpResponseForbidden()
    podcast = get_object_or_404(Podcast, slug=slug)
    podcast.remove_subscriber(request.user.listener)
    podcast.save()
    return HttpResponseNoContent()


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
