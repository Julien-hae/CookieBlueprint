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
