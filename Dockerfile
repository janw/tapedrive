FROM python:3.6-alpine
MAINTAINER Jan Willhaus <mail@janwillhaus.de

ENV ENVIRONMENT=PRODUCTION
ENV PIP_NO_CACHE_DIR=off

RUN mkdir /app
COPY Pipfile* /app/
WORKDIR /app

RUN apk --no-cache add mariadb-client-libs jpeg-dev
RUN apk --no-cache add --virtual build-dependencies postgresql-dev mysql-dev \
  zlib-dev build-base \
  && pip install --upgrade pip pipenv gunicorn honcho \
  && pipenv install --system \
  && apk del build-dependencies

COPY . /app/

EXPOSE 8273
CMD honcho start
