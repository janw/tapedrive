
<div align="center">
<img src="assets/img/icon@2x.png" alt="Tape Drive Logo" />
<h1>Tape Drive, the selfhosted Podcast Client and Archival server</h1>

[![Build Status](https://travis-ci.org/janw/tapedrive.svg?branch=master)](https://travis-ci.org/janw/tapedrive)
[![Maintainability](https://img.shields.io/codeclimate/maintainability/janw/tapedrive.svg)](https://codeclimate.com/github/janw/tapedrive)
[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https:///github.com/janw/tapedrive/issues)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/janwh)

</div>

Tape Drive is a self-hostable podcast client with built-in archiving features. By default, all subscribed podcasts will be properly organized on disk based on a user-chosen naming scheme, and including the available meta data.

## Current state of affairs

Tape Drive is built using [Django](https://djangoproject.com) **and contains beta releases on `master` branch**. While the initial feature set is being completed and stabilized, day-to-day development might also happen on master, in addition to feature branches and `develop` branch.


## Features

* Aesthetically pleasing presentation of podcasts, episodes, and their metadata
* Fully responsive web UI with distinctively unexcited behavior (no fancy animations, no overly excessive use of JavaScript etc.)
* Manually initiated episode downloads possible
* Elaborate User-selectable directory/file naming scheme based on Python's `str.format()` syntax
* Ability to efficiently fetch multi-page feeds

![Tape Drive welcoming you](assets/img/screenshots/welcome.png)

![Tape Drive podcast list view](assets/img/screenshots/podcasts-list.png)

## Prerequisites and setup

The easiest way to deploy Tape Drive on your server is to install it via Docker. The service is [available on Docker Hub](https://hub.docker.com/r/janwh/tapedrive/), and the repository contains a [`docker-compose.yml`](docker-compose.yml) file for the real out-of-the-box experience. Alternatively you may run Tape Drive "bare metal" — all you need is Python 3.6.

Please note, that the Docker image and bare metal deployment require you to take care of a database solution. It is technically possible to just use a SQLite database file but as background tasks for feed refreshes and downloads are running concurrently, running into database lockups is to be expected. For real-life / production use, please setup an instance of MySQL/MariaDB or PostgreSQL. In any case you'll have to provide the database connection details to Tape Drive (see below).

When applying the initial batch of database migrations (`users.0003_create_initial_superuser` to be precise), an admin account is created with a random password. That password will printed to the console log of the migrations run:

```
Applying users.0003_create_initial_superuser...Creating initial user: admin // pass: <randompass>
```

You may use those credentials to log in at first, and change the password or create additional users from within Tape Drive.

### Tape Drive in a standalone Docker container

Creating a Docker container from the Tape Drive Docker image is pretty a straight-forward process. As discussed above, Tape Drive expects you to provide a database connection on input, formatted as the well-known [12factor inspired `DATABASE_URL`](https://github.com/kennethreitz/dj-database-url#url-schema) environment variable. Most testing of Tape Drive is done in MySQL, so I recommend using that:

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

### Deploying Tape Drive via Docker-compose.

TBD.

### Bare-metal setup

For the development of Tape Drive I employ a bare-metal [setup via Pipenv/Pipfile](https://docs.pipenv.org). Pipenv is the up-and-coming alternative to the classic `requirements.txt` shipping with so many Python projects. It "aims to bring the best of all packaging worlds to the Python world" — Python devs should really check it out.

I digress. Setting up the environment becomes fairly simple with Pipenv. After [installing Pipenv](https://docs.pipenv.org/install/#installing-pipenv), just clone the repo and setup the virtualenv:

```bash
git clone https://github.com/janwh/tapedrive.git
cd tapedrive
pipenv install --dev
```

Note the `--dev` flag. It causes all development dependencies (debug tooling, django-extensions, etc.) to be installed as well. To further simplify running the dev environment, it is advised to add the necessary flags to Python / the virtualenv via a `.env` file. It will be automatically loaded with `pipenv shell` ans `pipenv run`, and might contain a custom `DATABASE_URL` to your local database instance, and set `DEBUG` flags for Django. My `.env` contains theses variables:

```bash
ENVIRONMENT=DEVELOPMENT
DJANGO_DEBUG='yes'
DJANGO_TEMPLATE_DEBUG='yes'
DATABASE_URL=mysql://tapedrive:supersecretpassword@localhost/tapedrive
```

Until further notice, setting `ENVIRONMENT` is not *strictly* necessary, as Tape Drive launches in development implicitly when cloned from the Git repository. By extension of that, the same is true for the `DEBUG` flags that are enabled in the development environment by default as well.

## Todos

Currently the main 'todo' is completing the sought out feature set around archiving. This mostly entails

* Periodic automated feed updates
* Automated downloads of newly published episodes, including a Subscribed/Unsubscribed paradim to include/exclude feeds from the automated downloads
* Smart handling of duplicate downloads if applicable (hashing, filename comparison, etc.)
* Proper unittests


## Authors and License

* **Jan Willhaus** - *Initial work*
* Cassette Icon by [Just UI](https://www.behance.net/Just_UI) via [IconFinder](https://www.iconfinder.com/icons/669942/audio_cassette_multimedia_music_icon)
* Login backdrop photo "Grado Headphones SR80e" by [Michael Mroczek](https://michaelmroczek.com/?utm_medium=referral&utm_source=unsplash) via [Unsplash](https://unsplash.com/@michaelmroczek?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)

The project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
