FROM python:3.6-alpine
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de"

ENV PIP_NO_CACHE_DIR off
ENV PYTHONUNBUFFERED 1
ENV TAPEDRIVE_VERSION 0.2a

COPY Pipfile* /

RUN apk --no-cache add mariadb-client-libs libstdc++ jpeg-dev bash gettext \
  && apk --no-cache add --virtual build-dependencies postgresql-dev mysql-dev \
  zlib-dev build-base \
  && pip install --upgrade pip pipenv gunicorn honcho \
  && pipenv install --system \
  && apk del build-dependencies

# Arbitrary database_url to allow manage.py commands at build time

# User-accessible environment
ENV ENVIRONMENT=PRODUCTION
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1

COPY . /app
WORKDIR /app

ARG DATABASE_URL="sqlite:////tmp.db"
RUN python manage.py compilemessages \
  && python manage.py compress --force \
  && python manage.py collectstatic --no-input -v0

EXPOSE 8273
VOLUME /app /data

CMD ["./start.sh"]
