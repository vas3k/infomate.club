# Infomate.club

[![Build Status](https://travis-ci.org/vas3k/infomate.club.svg?branch=master)](https://travis-ci.org/vas3k/infomate.club) [![GitHub license](https://img.shields.io/github/license/vas3k/infomate.club)](https://github.com/vas3k/infomate.club/blob/master/LICENSE) [![GitHub contributors](https://img.shields.io/github/contributors/vas3k/infomate.club)](https://GitHub.com/vas3k/infomate.club/graphs/contributors/)

Infomate is a small web service that shows multiple RSS sources on one page and performs tricky parsing and summarizing articles using TextRank algorithm. 

It helps to keep track of news from different areas without subscribing to hundreds of media accounts and getting annoying notifications.

Thematic and people-based collections does a really good job for discovery of new sources of information. 
Since we all are biased, such compilations can really help us to get out of information bubbles.

### Live URL: [infomate.club](https://infomate.club)

![](https://i.vas3k.ru/i7m.png)

## This is a pet-project 🐶

Which means you really shouldn't expect much from it. I wrote it over the weekend to solve my own pain.
No state-of-art kubernetes bullshit, no architecture patterns, even no tests at all. 
It's here just to show people what a pet-project might look like.

I wrote this code for fun, not for work. That's usually a huge difference. 


Like between riding a bike on the streets and cycling in the wild for fun :)

## How it works

It's basically a Django web app with a bunch of [scripts](scripts) for RSS parsing. 
It stores the parsed data in a PostgreSQL database.

The web app is only used to show the data (with heavy caching). 
Parsing and feed updates are performed by the three scripts running in cron. Like poor people do.

[Feedparser](https://pythonhosted.org/feedparser/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) are used to find, download and parse RSS. 

Text summarization is done via [newspaper3k](https://newspaper.readthedocs.io/en/latest/) with some additional 
protection against bad types of content like podcasts and too big pages in general, which can eat all your memory. Anything can happen in the RSS world :)

## Running it locally

The easy way. Install [docker](https://docs.docker.com/install/) on your machine. Then:

```
git clone git@github.com:vas3k/infomate.club.git
ls infomate.club
docker-compose up --build
```

After that navigate to [localhost:8000](http://localhost:8000)

To terminate:

```shell script
docker-compose down --remove-orphans
```


## Running for development

Make sure you have python3 and postresql installed locally.

#### Step 1: Install requirements

```
pip3 install -r requirements.txt --user
```

#### Step 2: Create a database structure

```
python3 manage.py migrate
```

#### Step 3: Take a look at [boards.yml](boards.yml)

This is the main source of truth for all RSS streams and collections in the service. 
All updates to the database are made through it. For the first time you can just use the existing one.

#### Step 4: Initialize your feeds

```
python3 scripts/initialize.py --config boards.yml
```

> Every time you make a change to boards.yml, just run this script again. 
> He is smart enough to create the missing ones and remove the old ones.

#### Step 5: Fetch some articles

```
python3 scripts/update.py
```

> Don't run it too often, otherwise sites may ban your IP. 
> There is a hardcoded cooldown interval for each feed, but you can use `--force` flag to ignore it.

#### Step 6: Run dev server

```
python3 manage.py runserver 8000
```

Then go to [localhost:8000](http://localhost:8000) again

## boards.yml format

TBD

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

You can help us with opened issues too. There's always something to work on.

We don't have any strict rules on formatting, just explain your motivation and the changes you've made to the PR description so that others understand what's going on.

## License

[Apache 2.0](LICENSE) © Vasily Zubarev

> TL;DR: you can modify, distribute and use it commercially, 
but you MUST reference the original author or give a link to service