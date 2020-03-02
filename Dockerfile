FROM python:3.7-slim-buster

ARG requirements=requirements.txt

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install --no-install-recommends -yq \
      gcc \
      libc-dev \
      libpq-dev \
      make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -r $requirements
