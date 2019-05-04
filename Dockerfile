FROM python:3.6-alpine
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de"

ENV PIP_NO_CACHE_DIR off
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml poetry.lock ./

RUN apk --no-cache add mariadb-client-libs libstdc++ jpeg-dev bash gettext \
  && apk --no-cache add --virtual build-dependencies postgresql-dev mysql-dev \
  zlib-dev build-base \
  && pip install --upgrade pip poetry gunicorn honcho \
  && poetry config settings.virtualenvs.create false \
  && poetry --no-interaction install --no-dev \
  && apk del build-dependencies


# User-accessible environment
ENV ENVIRONMENT=PRODUCTION

# Arbitrary database_url to allow manage.py commands at build time
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1

COPY . /app
WORKDIR /app

ARG DATABASE_URL="sqlite:////tmp.db"
RUN ["./prepare.sh"]

EXPOSE 8273
VOLUME /app /data

CMD ["./start.sh"]
