# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye
WORKDIR /app
COPY ./balti_zirgai .
COPY ./requirments.txt .
RUN apt update
RUN apt upgrade
RUN apt install -y gettext
RUN pip3 install -r requirments.txt
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
#RUN python manage.py compilemessages
CMD ["gunicorn", "-b", "0.0.0.0:8000", "balti_zirgai.wsgi"]