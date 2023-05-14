FROM node:16 as frontend
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de"

WORKDIR /frontend
COPY package-lock.json package.json ./
RUN npm install

COPY webpack.config.js ./
COPY frontend ./frontend
RUN npm run build

FROM python:3.7 as poetry-export
WORKDIR /src
COPY pyproject.toml poetry.lock ./
RUN \
  pip install --no-cache-dir poetry && \
  poetry export -f requirements.txt -o requirements.txt

FROM python:3.7-alpine
ENV PIP_NO_CACHE_DIR off
ENV PYTHONUNBUFFERED 1

COPY --from=poetry-export /src/requirements.txt ./
RUN \
  set -ex; \
  apk --update add tini postgresql-libs jpeg-dev && \
  apk add --virtual build-dependencies curl postgresql-dev libstdc++ zlib-dev build-base && \
  pip install -r requirements.txt && \
  pip install gunicorn honcho && \
  apk del build-dependencies && \
  rm -rf /var/cache/apk/* && \
  find /usr/local -depth -type f -a \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' +;


# User-accessible environment
ENV ENVIRONMENT=PRODUCTION
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1

WORKDIR /app
COPY Procfile ./
COPY manage.py ./
COPY bin ./bin
COPY --from=frontend /frontend/frontend/dist ./frontend/dist
COPY tapedrive ./tapedrive
COPY listeners ./listeners
COPY podcasts ./podcasts

EXPOSE 8273
VOLUME /app /data
ENTRYPOINT [ "tini", "--", "./bin/entrypoint.sh" ]
CMD ["honcho", "start"]
