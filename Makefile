PROJECT_NAME=infomate

all: run

# Install dev requirements
dev-requirements:
	@pip3 install -r requirements.txt

# Migrate database to the latest version
migrate:
	@python3 manage.py migrate

# Check types with mypy
mypy:
	mypy $(PROJECT_NAME)

# Lint code with flake8
lint:
	flake8 $(PROJECT_NAME)

# Runs dev server
run:
	@python3 manage.py runserver

# Run dev server in docker
docker_run:
	@python3 ./utils/wait_for_postgres.py
	@python3 manage.py migrate
	@python3 manage.py runserver

# Initialize feeds from boards.yml
feed_init:
	@python3 ./scripts/initialize.py

# Refresh RSS feeds
feed_refresh:
	@python3 ./scripts/update.py
