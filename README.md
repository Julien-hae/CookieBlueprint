# Python Cookiecutter Template

This is a cookiecutter template for Python-based projects. It allows to generate an exemplary setup and project structure including neat stuff like pre-commit-hooks, automated testing, type checking, etc. It is intended to be tailored to project needs.

## Setup
### Install WSL
If not already installed, install [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
Once thise is done make sure you run the following command

```shell
 # Update the package index and install the build-essential packace (C/C++ compiler, Make, Librariey like libc6-dev, etc):
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
### Install Python
If not already installed, install Python. The recommended way is to use [pyenv](https://github.com/pyenv/pyenv), which allows multiple parallel Python installations which can be automatically selected per project you're working on.

```shell
# Install Python if necessary
pyenv install 3.11
pyenv shell 3.11
```
### Install Poetry
If not already installed, get Poetry using pipx according to <https://python-poetry.org/docs/#installation>. If your are new to Poetry, you may find <https://python-poetry.org/docs/basic-usage/> interesting.
### Install Cookiecutter
If not already installed get [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/index.html) according to <https://cookiecutter.readthedocs.io/en/stable/installation.html>.

### Render Template
Now you can go to the freshly cloned repository and bake your cookies by running Cookiecutter. You will be prompted to provide the required information. Once you rendered the template, follow the setup instructions in the rendered template.

```shell
cookiecutter git@github.com:Julien-hae/CookieBlueprint.git
```

### Create Environment
Execute the following in a terminal:
```shell
# Create venv and install all dependencies
make

# Cleanup venv
make clean

# Cleanup
make remove-rendered-template
```
Do not forget to activate your virtualenv when done with the makefile
## Usage

## Contents and Concepts

At first glance one may be overwhelmed by the amount of files and folders present in this directory. This is mainly due to the fact, that each tool uses its own configuration file. The situation has improved with more and more tools adding support for pyproject.toml. The following two tables describe the main structure of the project:

| Folder | Purpose |
|--------|-----|
| `.venv` | This is where the Poetry-managed venv lives. |
| `.vscode` | This is where settings for vscode live. Some useful defaults are added in case you use vscode in your project. If not, this can savely be deleted.|
| `src` | Main directory for the python code. Most of the times this will contain one subfolder with the main module of the project.
| `tests` | Directory containing all tests. This directory will be scanned by the test-infrastructure to find testcases. |

| File                      | Purpose |
|---------------------------|---------|
| `.gitattributes`           | Attributes for git are defined in this file, such as automatic line-ending conversion. |
| `.gitignore`               | This file contains a list of path patterns that you want to ignore for git (they will never appear in commits). |
| `.pre-commit-config.yaml`  | This file contains configuration for the pre-commit hook, which is run whenever you `git commit`, you can configure running code quality tools and tests here. |
| `poetry.toml`              | Configuration for Poetry. |
| `pyproject.toml`           | This file contains meta information for your project, as well as a high-level specification of the dependencies of your project, from which Poetry will do its dependency resolution and generate the `poetry.lock`. Also, it contains some customization for code-quality tools. Check [PEP 621](https://peps.python.org/pep-0621/) for details.|
| `README.md`                | This file. Document how to develop and use your application in here. |

| Environment Variable | Purpose | Default Value | Allowed Values |
|----------------------|-|-|-|
| LOG_LEVEL            | Sets the default log level. | "INFO" | See [Python Standard Library API-Reference](https://docs.python.org/3/library/logging.html#logging-levels) |
