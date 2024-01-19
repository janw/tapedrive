from __future__ import annotations

from django.db import models


class PodcastOrder(models.TextChoices):
    TITLE = "TIT", "Title"
    PUBLISHED_ASC = "PUB", "Last Published"
    NUM_EPISODES = "NUM", "Number of Episodes"

    @classmethod
    def default(cls) -> PodcastOrder:
        return cls.TITLE


class EpisodeOrder(models.TextChoices):
    TITLE = "TIT", "Title"
    DOWNLOADED_ASC = "DOW", "Download Date (Earliest First)"
    DOWNLOADED_DESC = "-DOW", "Download Date (Latest First)"
    PUBLISHED_ASC = "PUB", "Publishing Date (Earliest First)"
    PUBLISHED_DESC = "-PUB", "Publishing Date (Latest First)"
    DURATION_ASC = "DUR", "Duration (Shortest First)"
    DURATION_DESC = "-DUR", "Duration (Longest First)"

    @classmethod
    def default(cls) -> EpisodeOrder:
        return cls.PUBLISHED_DESC


class ImageSecurityPolicy(models.TextChoices):
    ALLOW_ALL = "a", "Allow All"
    ALLOW_FIRST_PARTY = "f", "Allow First-Party"
    ALLOW_NONE = "n", "Allow None"

    @classmethod
    def default(cls) -> ImageSecurityPolicy:
        return cls.ALLOW_FIRST_PARTY
