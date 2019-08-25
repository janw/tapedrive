FROM node:lts as frontend
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de"

WORKDIR /frontend
COPY frontend/yarn.lock frontend/package.json ./
RUN yarn install

COPY frontend ./
RUN yarn build

FROM python:3.7-alpine
ENV PIP_NO_CACHE_DIR off
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml poetry.lock ./

RUN \
  apk --update add tini postgresql-libs jpeg-dev && \
  apk add --virtual build-dependencies curl postgresql-dev \
  libstdc++ zlib-dev build-base && \
  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python && \
  source $HOME/.poetry/env && \
  poetry config settings.virtualenvs.create false && \
  poetry --no-interaction install --no-dev && \
  pip install gunicorn honcho && \
  apk del build-dependencies && \
  rm -rf /var/cache/apk/* && \
  rm -rf $HOME/.poetry

# User-accessible environment
ENV ENVIRONMENT=PRODUCTION
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1

WORKDIR /app
COPY Procfile ./
COPY manage.py ./
COPY bin ./bin
COPY --from=frontend /frontend/dist ./frontend/dist
COPY tapedrive ./tapedrive
COPY listeners ./listeners
COPY podcasts ./podcasts

# Collect static files from external apps
RUN python manage.py collectstatic --no-input

EXPOSE 8273
VOLUME /app /data
ENTRYPOINT [ "tini", "--", "./bin/entrypoint.sh" ]
CMD ["honcho", "start"]
