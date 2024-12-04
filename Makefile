PYTHON_VERSION := 3.11
GIT_BRANCH = $(shell git branch --show-current)

all: setup

clean:
	rm -rf .venv

setup: check
	pyenv install ${PYTHON_VERSION} --skip-existing \
	&& pyenv local ${PYTHON_VERSION} \
	&& poetry env use ${PYTHON_VERSION} \
	&& poetry install \
	&& poetry run pre-commit install

check: pyenv-exists poetry-exists

pyenv-exists: ; @which pyenv > /dev/null

poetry-exists: ; @which poetry > /dev/null

render-in-esta-python:
	git clone ssh://git@codessh.sbb.ch:7999/kd_esta_blueprints/esta-python.git /tmp/esta-python
	(cd /tmp/esta-python && git branch ${GIT_BRANCH})
	(cd /tmp/esta-python && git checkout ${GIT_BRANCH})
	cookiecutter --overwrite-if-exists --no-input --output-dir /tmp . pypi_repository="esta.pypi" docker_repository="esta.docker" bitbucket_organization=KD_ESTA_BLUEPRINTS author_email="your-first-name.your-last-name@sbb.ch"
	(cd /tmp/esta-python && git add -A)

remove-rendered-template:
	rm -rf /tmp/esta-python
