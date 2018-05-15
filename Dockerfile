FROM python:3.6

MAINTAINER Jan Willhaus <mail@janwillhaus.de

ENV DJANGO_CONFIGURATION=Production

COPY . /app
WORKDIR /app

RUN pip install -U pipenv gunicorn
RUN pipenv install --system
RUN python

# TODO Generate Secret_key

EXPOSE 8000

CMD ["/app/start.sh"]
