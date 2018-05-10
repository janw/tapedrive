
<div align="center">
<img src="assets/img/icon@2x.png" alt="Tape Drive Logo" />
<h1>Tape Drive, the selfhosted Podcast Client and Archival server</h1>

[![Build Status](https://travis-ci.org/janwh/selfhosted-podcast-archive.svg?branch=master)](https://travis-ci.org/janwh/selfhosted-podcast-archive)
[![Coverage Status](https://coveralls.io/repos/github/janwh/selfhosted-podcast-archive/badge.svg?branch=master)](https://coveralls.io/github/janwh/selfhosted-podcast-archive?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/540e17f78c60b290b84e/maintainability)](https://codeclimate.com/github/janwh/selfhosted-podcast-archive/maintainability)
[![Development Status](https://img.shields.io/badge/status-alpha-red.svg)](https:///github.com/janwh/selfhosted-podcast-archive/issues)

</div>

Tape Drive is a self-hostable podcast client with built-in archiving features. By default, all subscribed podcasts will be properly organized on disk based on a user-chosen naming scheme, and including the available meta data.

## Current Affairs

Tape Drive is built using [Django](https://djangoproject.com) **and currently in active development on `master` branch**. As soon as the initial feature set has been stabilized, day-to-day development work will move to the `develop` branch, and master will contain stable versions.


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
