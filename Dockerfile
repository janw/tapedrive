FROM node:8 as compile
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de"

RUN npm install -g yarn
WORKDIR /app
COPY yarn.lock package.json ./
RUN yarn install

COPY gulpfile.js ./
COPY assets ./assets
RUN node `yarn bin`/gulp build \
  && ls -l /app/assets/dist

FROM python:3.7-alpine

ENV PIP_NO_CACHE_DIR off
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml poetry.lock ./

RUN apk --no-cache add --virtual build-dependencies postgresql-dev \
  mysql-dev libstdc++ jpeg-dev bash gettext zlib-dev build-base \
  && pip install --upgrade pip poetry gunicorn honcho \
  && poetry config settings.virtualenvs.create false \
  && poetry --no-interaction install --no-dev

# User-accessible environment
ENV ENVIRONMENT=PRODUCTION
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1

WORKDIR /app
COPY --from=compile /app/assets/dist ./assets/dist
COPY . /app

# Arbitrary database_url to allow manage.py commands at build time
ARG DATABASE_URL="sqlite:////tmp.db"
RUN python manage.py compilemessages \
  && python manage.py collectstatic --no-input -v0 --ignore "src"


EXPOSE 8273
VOLUME /app /data

CMD ["./bin/start.sh"]
