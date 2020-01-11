# Set the default goal if no targets were specified on the command line
.DEFAULT_GOAL = run
# Makes shell non-interactive and exit on any error
.SHELLFLAGS = -ec

PROJECT_NAME=infomate

dev-requirements:  ## Install dev requirements
	@pip3 install -r requirements.txt

docker_run:  ## Run dev server in docker
	@python3 ./utils/wait_for_postgres.py
	@python3 manage.py migrate
	@python3 manage.py runserver

feed_cleanup:  ## Cleanup RSS feeds
	@python3 ./scripts/cleanup.py

feed_init:  ## Initialize feeds from boards.yml
	@python3 ./scripts/initialize.py

feed_refresh:  ## Refresh RSS feeds
	@python3 ./scripts/update.py

help:  ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | sort \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[0;32m%-30s\033[0m %s\n", $$1, $$2}'

lint:  ## Lint code with flake8
	flake8 $(PROJECT_NAME)

migrate:  ## Migrate database to the latest version
	@python3 manage.py migrate

mypy:  ## Check types with mypy
	mypy $(PROJECT_NAME)

run:  ## Runs dev server
	@python3 manage.py runserver

.PHONY: \
  dev-requirements \
  docker_run \
  feed_cleanup \
  feed_init \
  feed_refresh \
  help \
  lint \
  migrate \
  mypy \
  run
