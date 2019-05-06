# Tape Drive, a selfhosted Podcast Client and Archiver

<!-- markdownlint-disable MD033 -->
<div align="center">
<img src="assets/src/img/icon@2x.png" alt="Tape Drive Logo" />

[![pipeline status](https://gitlab.com/janw/tapedrive/badges/master/pipeline.svg)](https://gitlab.com/janw/tapedrive/commits/master)
[![Coverage Status](https://coveralls.io/repos/github/janw/tapedrive/badge.svg?branch=refresh-project)](https://coveralls.io/github/janw/tapedrive?branch=refresh-project)
[![Maintainability](https://img.shields.io/codeclimate/maintainability/janw/tapedrive.svg)](https://codeclimate.com/github/janw/tapedrive)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Dependency management: poetry](https://img.shields.io/badge/deps-poetry-blueviolet.svg)](https://poetry.eustace.io/docs/)
[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https:///github.com/janw/tapedrive/issues)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/janwh)


</div>

Tape Drive is a selfhosted podcast client with built-in archiving features. By default, all subscribed podcasts will be properly organized on disk based on a user-chosen naming scheme, and including the available metadata.

## Current state of affairs

Tape Drive is built using [Django] **and contains beta releases on `master` branch**. While the initial feature set is being completed and stabilized, day-to-day development might also happen on master, in addition to feature branches and `develop` branch.

## Features

* Aesthetically pleasing presentation of podcasts, episodes, and their metadata
* Fully responsive web UI with distinctively unexcited behavior (no fancy animations, no overly excessive use of JavaScript etc.)
* Manually initiated episode downloads possible
* Elaborate User-selectable directory/file naming scheme based on Python's `str.format()` syntax
* Ability to efficiently fetch multi-page feeds

![Tape Drive welcoming you](.attachments/screenshots/welcome.png)

![Tape Drive podcast list view](.attachments/screenshots/podcasts-list.png)

## Prerequisites and setup

The easiest way to deploy Tape Drive on your server is to install it via Docker. The service is [available through GitLab Container Registry][gl-containerreg], and the repository contains a [`docker-compose.yml`](docker-compose.yml) file for the real out-of-the-box experience.

Please note, that the Docker image and bare metal deployment require you to take care of a database solution. It is technically possible to just use a SQLite database file but as background tasks for feed refreshes and downloads are running concurrently, running into database lockups is to be expected. For real-life / production use, please setup an instance of MySQL/MariaDB or PostgreSQL. In any case you'll have to provide the database connection details to Tape Drive (see below).

When applying the initial batch of database migrations (`users.0003_create_initial_superuser` to be precise), an admin account is created with a random password. That password will printed to the console log of the migrations run:

```text
Applying users.0003_create_initial_superuser...Creating initial user: admin // pass: <randompass>
```

You may use those credentials to log in at first, and change the password or create additional users from within Tape Drive.

### Tape Drive in a standalone Docker container

Creating a Docker container from the Tape Drive Docker image is pretty a straight-forward process. As discussed above, Tape Drive expects you to provide a database connection on input, formatted as the well-known [`DATABASE_URL`][dburl] environment variable. Most testing of Tape Drive is done in MySQL, so I recommend using that:

```bash
docker create \
  --name=tapedrive \
  -v <path to data>:/data \
  -e DATABASE_URL="mysql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE_NAME" \
  -e DJANGO_ALLOWED_HOSTS=127.0.0.1,myfancy.domainname.example \
  -p 8273:8273 \
  janwh/tapedrive
```

Use the `DJANGO_ALLOWED_HOSTS` variable to tell Tape Drive which hostnames to accept connections from (as a comma-separated list). Most likely you want to link the storage path inside the container to a real location on your filesystem. By default, Tape Drive downloads data to `/data`, hence the above `-v` mapping.

### Deploying Tape Drive via Docker-compose

TBD.

### Development setup

For the development/bare-metal setup of Tape Drive I use [Poetry]. Just clone the repo and setup the virtualenv:

```bash
git clone https://github.com/janw/tapedrive.git
cd tapedrive
poetry install
```

Unless deactivated with the `--no-dev` flag, all dependencies (including debug tooling, django-extensions, etc.) will be installed. To further simplify running the dev environment, it is advised to add the necessary flags to Python / the virtualenv via a `.env` file. It will be automatically loaded as part of the Django configuration.. You can use it to provide the default development settings, like a `DATABASE_URL` for your local database instance, or setting `DEBUG` flags for Django. My `.env` contains theses variables:

```bash
ENVIRONMENT=DEVELOPMENT
DJANGO_DEBUG='yes'
DJANGO_TEMPLATE_DEBUG='yes'
DATABASE_URL=mysql://tapedrive:supersecretpassword@localhost/tapedrive
```

Setting `ENVIRONMENT` is not *strictly* necessary, as Tape Drive launches in development implicitly when cloned from the Git repository. By extension of that, the same is true for the `DEBUG` flags that are enabled in the development environment by default as well.

## Todos

Currently the main 'todo' is completing the sought out feature set around archiving. This mostly entails

* Automated periodic feed updates
* Automated downloads of newly published episodes, including a Subscribed/Unsubscribed paradim to include/exclude feeds from the automated downloads
* Smart handling of duplicate downloads if applicable (hashing, filename comparison, etc.)
* A comprehensive utilities library for handling podcast feeds
* Full test coverage, and replacing actual feed downloads with mocked/vcr'ed fixtures

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
