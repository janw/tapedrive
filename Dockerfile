FROM node:16 as frontend
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de"

WORKDIR /frontend
COPY package-lock.json package.json ./
RUN npm install

COPY vite.config.js ./
COPY frontend ./frontend
RUN npm run build

FROM python:3.7 as poetry-export
WORKDIR /src
COPY pyproject.toml poetry.lock ./
RUN \
  pip install --no-cache-dir "poetry>=1.0" && \
  poetry export -f requirements.txt -o requirements.txt

FROM python:3.7-alpine
ENV PIP_NO_CACHE_DIR off
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY --from=poetry-export /src/requirements.txt ./

# hadolint ignore=DL3018
RUN \
  set -ex; \
  apk add --no-cache tini postgresql-libs jpeg-dev && \
  apk add --no-cache --virtual build-dependencies curl postgresql-dev libstdc++ zlib-dev build-base && \
  pip install --no-cache-dir -r requirements.txt && \
  apk del build-dependencies && \
  find /usr/local -depth -type f -a \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' +;


# User-accessible environment
ENV ENVIRONMENT=PRODUCTION
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1

COPY Procfile ./
COPY manage.py ./
COPY bin ./bin
COPY --from=frontend /frontend/frontend/dist ./frontend/dist
COPY tapedrive ./tapedrive
COPY listeners ./listeners
COPY podcasts ./podcasts

RUN python manage.py collectstatic --no-input

EXPOSE 8273
VOLUME /app /data
ENTRYPOINT [ "tini", "--", "./bin/entrypoint.sh" ]
CMD ["honcho", "start"]
