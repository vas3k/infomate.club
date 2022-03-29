FROM ubuntu:20.04
ENV MODE dev
ENV DEBIAN_FRONTEND=noninteractive

ARG requirements=requirements.txt

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
      python3 \
      python3-pip \
      gcc \
      libc-dev \
      libpq-dev \
      make \
      cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app
COPY etc/crontab /etc/crontab
RUN chmod 600 /etc/crontab

ADD . /app

RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -r $requirements

RUN python3 -c "import nltk; nltk.download('punkt')"
