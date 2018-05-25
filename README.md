
<div align="center">
<img src="assets/img/icon@2x.png" alt="Tape Drive Logo" />
<h1>Tape Drive, the selfhosted Podcast Client and Archival server</h1>

[![Build Status](https://travis-ci.org/janwh/tapedrive.svg?branch=master)](https://travis-ci.org/janwh/tapedrive?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/janwh/tapedrive/badge.svg?branch=master)](https://coveralls.io/github/janwh/tapedrive?branch=master)
[![Maintainability](https://img.shields.io/codeclimate/maintainability/janwh/tapedrive.svg)](https://codeclimate.com/github/janwh/tapedrive)
[![Updates](https://pyup.io/repos/github/janwh/tapedrive/shield.svg)](https://pyup.io/repos/github/janwh/tapedrive/)
[![Development Status](https://img.shields.io/badge/status-alpha-red.svg)](https:///github.com/janwh/tapedrive/issues)
[![Join the chat at https://gitter.im/tapedriveio/Lobby](https://badges.gitter.im/tapedriveio/Lobby.svg)](https://gitter.im/tapedriveio/Lobby)

[![Receiving via Liberapay](https://img.shields.io/liberapay/receives/janw.svg)](https://liberapay.com/janw/)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/janwh)

</div>

Tape Drive is a self-hostable podcast client with built-in archiving features. By default, all subscribed podcasts will be properly organized on disk based on a user-chosen naming scheme, and including the available meta data.

## Current Affairs

Tape Drive is built using [Django](https://djangoproject.com) **and currently in active development on `master` branch**. As soon as the initial feature set has been stabilized, day-to-day development work will move to the `develop` branch, and master will contain stable versions.


## Features

* Aesthetically pleasing presentation of podcasts, episodes, and their metadata
* Fully responsive web UI with distinctively unexcited behavior (no fancy animations, no overly excessive use of JavaScript etc.)
* Manually initiated episode downloads possible
* Elaborate User-selectable directory/file naming scheme based on Python's `str.format()` syntax (with segment drag'n'drop support later on)
* Ability to efficiently fetch multi-page feeds


![Tape Drive welcoming you](assets/img/screenshots/welcome.png)

![Tape Drive podcast list view](assets/img/screenshots/podcasts-list.png)

## Prerequisites and Setup

The easiest way to deploy Tape Drive on your server is to install it via Docker. The service is [available on Docker Hub](https://hub.docker.com/r/janwh/tapedrive/), and the repository contains a [`docker-compose.yml`](docker-compose.yml) file for the real out-of-the-box experience. Alternatively you may run Tape Drive "bare metal" — all you need is Python 3.6.

Please note, that the Docker image and bare metal deployment require you to take care of a database solution. It is technically possible to just use a SQLite database file but as background tasks for feed refreshes and downloads are running concurrently, running into database lockups is to be expected. For real-life / production use, please setup an instance of MySQL/MariaDB or PostgreSQL. In any case you'll have to provide the database connection details to Tape Drive (see below).

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

### Bare-metal setup (also for development)

TBD.


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
