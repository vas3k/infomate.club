# Set the default goal if no targets were specified on the command line
.DEFAULT_GOAL = run
# Makes shell non-interactive and exit on any error
.SHELLFLAGS = -ec

PROJECT_NAME=infomate

run:  ## Run dev server
	python3 manage.py migrate
	python3 manage.py runserver 0.0.0.0:8000

dev-requirements:  ## Install dev requirements
	pip3 install -r requirements.txt

docker-run-app:  ## Run production setup in docker
	python3 manage.py migrate
	gunicorn infomate.asgi:application -w 3 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8816 --capture-output --log-level debug --access-logfile - --error-logfile -

docker-run-cron:  ## Run production cron container
	env >> /etc/environment
	cron -f -l 2

feed_cleanup:  ## Cleanup RSS feeds
	python3 ./scripts/cleanup.py

feed_init:  ## Initialize feeds from boards.yml
	python3 ./scripts/initialize.py --config boards.yml --no-upload-favicons -y

feed_refresh:  ## Refresh RSS feeds
	python3 ./scripts/update.py

help:  ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | sort \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[0;32m%-30s\033[0m %s\n", $$1, $$2}'

lint:  ## Lint code with flake8
	flake8 $(PROJECT_NAME)

migrate:  ## Migrate database to the latest version
	python3 manage.py migrate

mypy:  ## Check types with mypy
	mypy $(PROJECT_NAME)

telegram:
	python3 setup_telegram.py

test-ci: test-requirements lint mypy  ## Run tests (intended for CI usage)

test-requirements:  ## Install requirements to run tests
	@pip3 install -r ./requirements-test.txt

.PHONY: \
  run \
  dev-requirements \
  docker-run-app \
  docker-run-cron \
  feed_cleanup \
  feed_init \
  feed_refresh \
  help \
  lint \
  migrate \
  mypy \
  test-ci \
  test-requirements
