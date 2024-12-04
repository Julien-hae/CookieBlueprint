# Esta Python Cookiecutter Template

This is a cookiecutter template for Python-based projects. It allows to generate an exemplary setup and project structure including neat stuff like pre-commit-hooks, automated testing, type checking, CI/CD using Tekton, etc. It is intended to be tailored to project needs.

## Usage

### Install Python

If not already installed, install Python. The recommended way is to use [pyenv](https://github.com/pyenv/pyenv), which allows multiple parallel Python installations which can be automatically selected per project you're working on.

```shell
# Install Python if necessary
pyenv install 3.11
pyenv shell 3.11
```

> **_Note_**: If you start from scratch with Python development you might find <https://confluence.sbb.ch/display/EAPKB/Automated+WSL+and+Docker+Setup> useful.

### Install Cookiecutter
If not already installed get [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/index.html) according to <https://cookiecutter.readthedocs.io/en/stable/installation.html>.

### Order a Bitbucket Repository
Order a Bitbucket repository from the CLEW Portal <https://self.sbb-cloud.net/tools/bitbucket/repository> and clone it.

### (Optional) Order a Docker Repository
If you want to package your code in a Docker container order a "Docker" repository on Artifactory from the CLEW Portal: <https://self.sbb-cloud.net/tools/artifactory>.

### (Optional) Order a PyPI Repository
If you want to share your code as Python library order a "Python" repository on Artifactory from the CLEW Portal: <https://self.sbb-cloud.net/tools/artifactory>.

### Render Template
Now you can go to the freshly cloned repository and bake your cookies by running Cookiecutter. You will be prompted to provide the required information. Once you rendered the template, follow the setup instructions in the rendered template.

```shell
# Note: the name of your Docker and PyPi repository should be docker-repo.docker and pypi-repo.pypi respectively.
cookiecutter ssh://git@codessh.sbb.ch:7999/kd_esta_blueprints/esta-python-cookiecutter.git
```

## Developer's Guide

- Development of esta-python happens in this repository following a standard lean gitflow.
- Release: a release is a merge on master. This will trigger the corresponding Tekton-Pipeline which pushes a rendered version of the template to <https://code.sbb.ch/projects/KD_ESTA_BLUEPRINTS/repos/esta-python/browse>

### Setup
- Install Python (see instructions above).
- Install Poetry according to <https://python-poetry.org/docs/#installation>.
- Setup your environment:

```shell
# Create venv and install all dependencies
make

# Cleanup venv
make clean

# Render template into current HEAD of esta-python
# Helpful when you want to see the diff to esta-python.
make render-in-esta-python

# Cleanup
make remove-rendered-template
```
