FROM python:3.6
MAINTAINER Jan Willhaus <mail@janwillhaus.de

COPY . /app
WORKDIR /app

RUN pip install -U pipenv gunicorn honcho
RUN pipenv install --system

RUN python manage.py migrate

# ENV DJANGO_ALLOWED_HOSTS=
# ENV DATABASE_URL=
# TODO Generate Secret_key

EXPOSE 8273

CMD huncho start
