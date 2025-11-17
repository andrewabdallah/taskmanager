set dotenv-load
set positional-arguments

CURRENT_DATE  := `date +"%y%m%dT%H%M%S"`
GIT_BRANCH := `git rev-parse --abbrev-ref HEAD`
COMMIT_SHA := `git rev-parse --short HEAD`
DOCKER_COMPOSE := env_var_or_default("DOCKER_COMPOSE", "docker compose")
DOCKER_COMPOSE_EXEC := DOCKER_COMPOSE + " exec"
DOCKER_COMPOSE_EXEC_WEB := DOCKER_COMPOSE_EXEC + " web"
DOCKER_COMPOSE_EXEC_WEB_MANAGE := DOCKER_COMPOSE_EXEC_WEB + " python manage.py"
WEB_TEST_SETTINGS_MODULE := env_var_or_default("WEB_TEST_SETTINGS_MODULE", "core.settings.test")
WEB_TEST_PARAMETERS := "--noinput -v 1 --exclude-tag=kcf"
WEB_TEST_COMMAND := "manage.py test " + WEB_TEST_PARAMETERS + " --settings=" + WEB_TEST_SETTINGS_MODULE
WEB_TEST_MODE := "-e SERVER_MODE=test web"
DJANGO_UV := "uv pip compile --quiet --upgrade --python=3.11"


dependencies_update:
	{{DOCKER_COMPOSE_EXEC_WEB}} {{DJANGO_UV}} pyproject.toml --output-file requirements/base.txt
	{{DOCKER_COMPOSE_EXEC_WEB}} {{DJANGO_UV}} --all-extras pyproject.toml --output-file requirements/.txt

# Init dev environment
init-dev:
	{{DOCKER_COMPOSE}} build --no-cache
	{{DOCKER_COMPOSE}} run --rm web python manage.py migrate

# manage.py commands
manage *command="help":
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} $@

# Make migrations
makemigrations:
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} makemigrations

# Make view migrations
makeviewmigrations:
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} makeviewmigrations

# Migrate
migrate *args='':
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} migrate $@

# Make migrations and migrate
migrations:
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} makemigrations
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} makeviewmigrations
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} migrate

# Build the containers
build *args='':
    {{DOCKER_COMPOSE}} build --build-arg BUILD_DATE={{CURRENT_DATE}} --build-arg GIT_BRANCH={{GIT_BRANCH}} --build-arg COMMIT_SHA={{COMMIT_SHA}} $@

# Launch the containers in the background
up *apps='':
	{{DOCKER_COMPOSE}} up -d $@

# Turn off the containers
down:
	{{DOCKER_COMPOSE}} down --remove-orphans

# Starts the webserver on the django container
run:
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} runserver 0.0.0.0:8080

# Starts the Backend with Granian
granian:
	{{DOCKER_COMPOSE_EXEC_WEB}} granian --interface asginl --host 0.0.0.0 --port 8080 --log-level info --respawn-failed-workers --reload core.asgi:application

# Command to run custom commands such as just action python manage.py createsuperuser
action *action='':
	{{ DOCKER_COMPOSE_EXEC_WEB }} $@

# Open a Django shell => todo
shell:
	{{DOCKER_COMPOSE_EXEC_WEB_MANAGE}} shell_plus

# Open a bash => todo
bash:
	{{DOCKER_COMPOSE_EXEC_WEB}} bash

# Run the test suit as the CI
test *args='':
	{{DOCKER_COMPOSE_EXEC}} {{WEB_TEST_MODE}} python {{WEB_TEST_COMMAND}} --parallel=auto $@

# Run the test suit but keep the database
tesk *args='':
	{{DOCKER_COMPOSE_EXEC}} {{WEB_TEST_MODE}} python {{WEB_TEST_COMMAND}} --parallel=auto --keepdb $@

# Test linting on the current changes compared to local dev branch
lint:
	{{DOCKER_COMPOSE_EXEC_WEB}} ruff check --output-format concise .
	{{DOCKER_COMPOSE_EXEC_WEB}} ruff format --check .

ruff *args='':
	{{DOCKER_COMPOSE_EXEC_WEB}} ruff check . $@

# Fix linting on the current changes compared to local dev branch
lint-fix:
	{{DOCKER_COMPOSE_EXEC_WEB}} ruff check . --fix
	{{DOCKER_COMPOSE_EXEC_WEB}} ruff format .
