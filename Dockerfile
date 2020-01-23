FROM python:3-slim

COPY ./test /app
COPY . /astroapi
WORKDIR /app

# Python setup
RUN pip install -e /astroapi

# Flask
ENV FLASK_APP=boilerplate.py
ENV FLASK_ENV=development