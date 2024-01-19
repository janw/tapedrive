# Tape Drive, a selfhosted Podcast Client and Archiver

<!-- markdownlint-disable MD033 -->
<div align="center">
<img src="frontend/src/images/icon@2x.png" alt="Tape Drive Logo" />

[![Docker Build](https://github.com/janw/tapedrive/actions/workflows/docker-build.yaml/badge.svg)](https://github.com/janw/tapedrive/actions/workflows/docker-build.yaml)
[![Tests](https://github.com/janw/tapedrive/actions/workflows/tests.yaml/badge.svg)](https://github.com/janw/tapedrive/actions/workflows/tests.yaml)

[![maintainability](https://api.codeclimate.com/v1/badges/e8a6d1046e1aebb4b701/maintainability)](https://codeclimate.com/github/janw/tapedrive/maintainability)
[![coverage](https://api.codeclimate.com/v1/badges/e8a6d1046e1aebb4b701/test_coverage)](https://codeclimate.com/github/janw/tapedrive/test_coverage)
[![pre-commit.ci](https://results.pre-commit.ci/badge/github/janw/tapedrive/main.svg)](https://results.pre-commit.ci/latest/github/janw/tapedrive/main)

[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/docs/)
[![pre-commit](https://img.shields.io/badge/-pre--commit-f8b424?logo=pre-commit&labelColor=grey)](https://github.com/pre-commit/pre-commit)

</div>

Tape Drive is a self-hosted podcast client with an emphasis on long-term storage of episodes. The idea is to organize subscribed podcasts properly on disk following a robust naming scheme, and including the available metadata such as shownotes, episode and season numbering, etc.

In [future versions I plan on extending Tape Drive](#todos-and-planned-features), for example to include a web player for listening to downloaded episodes, hoping to turn it into a simple web-based podcatcher.

Whenever possible Tape Drive takes a privacy-first approach. For example this means removing tracking parameters from download URLs and, as many podcasts are starting to embed tracking pixels and pull images from external domains, Tape Drive will show such embeds only shown after the user explicitly requests it.

## Current state of affairs

Tape Drive is built using [Django] **and I'm working on a first stable release**. Feel free to check it out but there are no guarantees on it working at all at any time right now.

## Features

* Aesthetically pleasing presentation of podcasts, episodes, and their metadata
* Fully responsive web-UI with distinctively unexcited behavior (no fancy animations, clean look, etc.)
* Automatic episode downlodas for subscribed podcasts, including downloading the back catalog
* Storage according to a robust and human-readable naming scheme, including shownotes metadata
* Manually initiated episode downloads possible
* Ability to efficiently fetch multi-page feeds

## Impressions

![Tape Drive login screen](hack/attachments/screenshots/login-animated.gif)

![Tape Drive welcoming you](hack/attachments/screenshots/welcome.png)

![Tape Drive podcast list view](hack/attachments/screenshots/podcasts-list.png)

![Tape Drive podcast detail view](hack/attachments/screenshots/podcast-detail.png)

## Prerequisites and setup

Right now, the only fully supported way of deploying Tape Drive is via Docker container. The image is [available through GitLab Container Registry][gl-containerreg], and in the `hack/docker/` directory you will find an example [`docker-compose.yml`](docker-compose.yml) file for the real out-of-the-box experience. Tape Drive supports PostgreSQL as its database back-end.

Non-dockerized deployment is absolutely possible, as Tape Drive is basically just a Django application.

When applying the initial batch of database migrations (`users.0003_create_initial_superuser` to be precise), an admin account is created with a random password. That password will printed to the console log of the migrations run:

```text
Applying users.0003_create_initial_superuser...Creating initial user: admin // pass: <randompass>
```

You may use those credentials to log in at first, and change the password or create additional users from within Tape Drive.

### Tape Drive in a standalone Docker container

Creating a Docker container from the Tape Drive Docker image is pretty a straight-forward process. As discussed above, Tape Drive expects you to provide a database connection on input, formatted as the well-known [`DATABASE_URL`][dburl] environment variable:

```bash
docker create \
  --name=tapedrive \
  -v <path to data>:/data \
  -e DATABASE_URL="postgres://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE_NAME" \
  -e DJANGO_ALLOWED_HOSTS=127.0.0.1,myfancy.domainname.example \
  -p 8273:8273 \
  ghcr.io/janw/tapedrive
```

Use the `DJANGO_ALLOWED_HOSTS` variable to tell Tape Drive which hostnames to accept connections from (as a comma-separated list). Most likely you want to link the storage path inside the container to a real location on your filesystem. By default, Tape Drive downloads data to `/data`, hence the above `-v` mapping.

### Development setup

 [Poetry]  is used for dependency management of Tape Drive. Just clone the repo and setup the virtualenv:

```bash
git clone https://github.com/janw/tapedrive.git
cd tapedrive
poetry install
```

To further simplify running the dev environment, it is advised to add the necessary flags to Python / the virtualenv via a `.env` file. It will be automatically loaded as part of the Django configuration.. You can use it to provide the default development settings, like a `DATABASE_URL` for your local database instance, or setting `DEBUG` flags for Django. My `.env` contains theses variables:

```bash
ENVIRONMENT=DEVELOPMENT
DJANGO_DEBUG='yes'
DJANGO_TEMPLATE_DEBUG='yes'
DATABASE_URL=postgres://tapedrive:supersecretpassword@localhost/tapedrive
```

Setting `ENVIRONMENT` is not *strictly* necessary, as Tape Drive launches in development implicitly when cloned from the Git repository. By extension of that, the same is true for the `DEBUG` flags that are enabled in the development environment by default as well.

## Todos and Planned Features

Currently the main goal is completing the sought out feature set around archiving. This mostly entails:

* Automated periodic feed updates
* Automated downloads of newly published episodes, including a Subscribed/Unsubscribed paradim to include/exclude feeds from the automated downloads
* Robust storage paradigm of episode files and metadata
* Full test coverage, and replacing actual feed downloads with mocked/vcr'ed fixtures

Furthermore I am considering implementing some of the following features:

* Web player for episode playback, including storing the playback state of episodes
* Smart handling of duplicate downloads if applicable (hashing, filename comparison, etc.)
* Turn the used utilities for handling podcast feeds into an externally usable library

## Authors and License

* **Jan Willhaus** - *Initial work*
* Cassette Icon by [JustUI] via [IconFinder]
* Login backdrop photo "Grado Headphones SR80e" by [Michael Mroczek][mroczek] via [Unsplash]

The project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

[Django]: https://djangoproject.com
[Poetry]: https://poetry.eustace.io/docs/#installation
[dburl]: https://github.com/kennethreitz/dj-database-url#url-schema
[JustUI]: https://www.behance.net/Just_UI
[IconFinder]: https://www.iconfinder.com/icons/669942/audio_cassette_multimedia_music_icon
[mroczek]: https://michaelmroczek.com/?utm_medium=referral&utm_source=unsplash
[Unsplash]: https://unsplash.com/@michaelmroczek?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
[gl-containerreg]: https://gitlab.com/janw/tapedrive/container_registry
