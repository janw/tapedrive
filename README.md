
<div align="center">
<img src="assets/img/icon@2x.png" alt="Tape Drive Logo" />
<h1>Tape Drive, the selfhosted Podcast Client and Archival server</h1>

[![Build Status](https://travis-ci.org/janwh/tapedrive.svg?branch=master)](https://travis-ci.org/janwh/tapedrive?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/janwh/tapedrive/badge.svg?branch=master)](https://coveralls.io/github/janwh/tapedrive?branch=master)
[![Maintainability](https://img.shields.io/codeclimate/maintainability/janwh/tapedrive.svg)](https://codeclimate.com/github/janwh/tapedrive)
[![Development Status](https://img.shields.io/badge/status-alpha-red.svg)](https:///github.com/janwh/tapedrive/issues)
[![Join the chat at https://gitter.im/tapedriveio/Lobby](https://badges.gitter.im/tapedriveio/Lobby.svg)](https://gitter.im/tapedriveio/Lobby)

[![Receiving via Liberapay](https://img.shields.io/liberapay/receives/janw.svg)](https://liberapay.com/janw/)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/janwh)

</div>

Tape Drive is a self-hostable podcast client with built-in archiving features. By default, all subscribed podcasts will be properly organized on disk based on a user-chosen naming scheme, and including the available meta data.

## Current Affairs

Tape Drive is built using [Django](https://djangoproject.com) **and currently in active development on `master` branch**. As soon as the initial feature set has been stabilized, day-to-day development work will move to the `develop` branch, and master will contain stable versions.

## Screenshots

That's how Tape Drive looks like. Not a lot of pages but a few with reasonable information density.

![Tape Drive login screen opening up](assets/img/screenshots/login-animated.gif)

![Tape Drive podcasts list view](assets/img/screenshots/podcasts-list.png)

![Tape Drive podcast detail view](assets/img/screenshots/podcast-detail.png)

## Todos

Currently the main 'todo' is completing the sought out feature set around archiving. This mostly entails

* Aesthetically pleasing presentation of podcasts, episodes, and their metadata
* Fully responsive web UI with distinctively unexcited behavior (no fancy animations, no overly excessive use of JavaScript etc.)
* Periodic automated feed updates
* Manually launched episode downloads
* Automated downloads of newly published episodes, including a Subscribed/Unsubscribed paradim to include/exclude feeds from the automated downloads
* Elaborate User-selectable directory/file naming scheme based on Python's `str.format()` syntax (with segment drag'n'drop support later on)
* Ability to efficiently fetch multi-page feeds
* Smart handling of duplicate downloads if applicable (hashing, filename comparison, etc.)
* Proper unittests


## Authors and License

* **Jan Willhaus** - *Initial work*
* Cassette Icon by [Just UI](https://www.behance.net/Just_UI) via [IconFinder](https://www.iconfinder.com/icons/669942/audio_cassette_multimedia_music_icon)

The project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
