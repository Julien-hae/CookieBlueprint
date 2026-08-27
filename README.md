# 🍪 CookieBlueprint

This is a [Copier](https://copier.readthedocs.io/en/stable/) template for Python-based projects. It allows to generate an exemplary setup and project structure including neat stuff like pre-commit-hooks, automated testing, type checking, etc. It is intended to be tailored to project needs.

Unlike a plain Cookiecutter template, a project generated from this template stays linked to it: the answers you gave are recorded in the generated `.copier-answers.yml`, which lets you run `copier update` later on to pull template changes into a project that has already been generated and modified.

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

### Install Copier
If not already installed, get [Copier](https://copier.readthedocs.io/en/stable/) according to <https://copier.readthedocs.io/en/stable/#installation>. As it is a command-line tool, installing it with pipx is recommended:

```shell
pipx install copier
```

### Render Template
Now you can bake your cookies by running Copier. In contrast to Cookiecutter, Copier renders into the destination directory you pass on the command line, so no extra directory is created for you. You will be prompted to provide the required information. Once you rendered the template, follow the setup instructions in the generated `README.md`.

```shell
copier copy git@github.com:Julien-hae/CookieBlueprint.git my-new-project
```

By default Copier renders the newest git tag of the template. To render the current state of `master` instead — for example while working on the template itself — add `--vcs-ref=HEAD`:

```shell
copier copy --vcs-ref=HEAD git@github.com:Julien-hae/CookieBlueprint.git my-new-project
```

## Updating a Generated Project
Because the generated project records which template version it came from, template changes can be pulled in afterwards. Run this from inside the generated project, on a clean working tree:

```shell
copier update
```

Copier re-asks the questions using your previous answers as defaults, computes the diff between the old and the new template version, and applies it on top of your local changes. Hunks that cannot be applied cleanly are written into the affected file as git-style conflict markers (`<<<<<<< before updating` / `>>>>>>> after updating`), and the file is left unmerged in the git index. Resolve those, `git add` them, and review the whole result with `git diff` before committing.

Useful flags:

| Command | Purpose |
|---------|---------|
| `copier update --defaults`      | Reuse all recorded answers without prompting. |
| `copier update --vcs-ref=HEAD`  | Update to the current state of `master` instead of the newest tag. |
| `copier update --conflict=rej`  | Write conflicts to `*.rej` files next to the affected file instead of inline markers. |
| `copier update --pretend`       | Show what would change without touching anything. |

## Adopting the Template in an Existing Project
Projects that were generated with Cookiecutter — or that never used a template at all — have no `.copier-answers.yml` and therefore cannot be updated yet. Run a one-time `copier copy` over them to create it. Do this on a clean working tree so that the result can be reviewed with `git diff`:

```shell
cd my-existing-project
copier copy --overwrite git@github.com:Julien-hae/CookieBlueprint.git .
```

Answer the questions with the values the project already uses, review the diff, revert whatever you do not want, and commit. From then on `copier update` works.

## Releasing a New Template Version
`copier copy` and `copier update` resolve to the newest git tag of this repository, so template changes only reach generated projects once they are tagged. Tags are expected to be [SemVer](https://semver.org/):

```shell
git tag -a v1.0.0 -m "Describe what changed for generated projects"
git push origin v1.0.0
```

## Working on the Template
Execute the following in a terminal:
```shell
# Create venv and install all dependencies
make

# Cleanup venv
make clean
```
Do not forget to activate your virtualenv when done with the makefile

To try out a change without tagging it, render the working copy into a scratch directory:

```shell
copier copy --vcs-ref=HEAD . /tmp/render-check
```

## Contents and Concepts

At first glance one may be overwhelmed by the amount of files and folders present in this directory. This is mainly due to the fact, that each tool uses its own configuration file. The situation has improved with more and more tools adding support for pyproject.toml. The following two tables describe the main structure of this template repository:

| Folder | Purpose |
|--------|-----|
| `.venv` | This is where the Poetry-managed venv lives. |
| `.vscode` | This is where settings for vscode live. Some useful defaults are added in case you use vscode in your project. If not, this can savely be deleted.|
| `template` | The only directory that is rendered into the generated project (`_subdirectory` in `copier.yml`). Everything outside of it belongs to this repository alone. |
| `tests` | Directory containing all tests. This directory will be scanned by the test-infrastructure to find testcases. |

| File                      | Purpose |
|---------------------------|---------|
| `copier.yml`               | The template configuration: the questions asked when rendering, their defaults and validation, and Copier's own settings. |
| `.gitattributes`           | Attributes for git are defined in this file, such as automatic line-ending conversion. |
| `.gitignore`               | This file contains a list of path patterns that you want to ignore for git (they will never appear in commits). |
| `.pre-commit-config.yaml`  | This file contains configuration for the pre-commit hook, which is run whenever you `git commit`, you can configure running code quality tools and tests here. |
| `poetry.toml`              | Configuration for Poetry. |
| `pyproject.toml`           | This file contains meta information for your project, as well as a high-level specification of the dependencies of your project, from which Poetry will do its dependency resolution and generate the `poetry.lock`. Also, it contains some customization for code-quality tools. Check [PEP 621](https://peps.python.org/pep-0621/) for details.|
| `README.md`                | This file. Document how to develop and use your application in here. |

### Inside `template/`

Copier only treats files ending in `.jinja` as templates: their content is rendered and the suffix is stripped. Every other file is copied over verbatim, which keeps genuinely static files (`LICENSE`, `.gitignore`, the VS Code settings) free of escaping concerns. Directory and file *names* are always rendered, which is why the package directories are literally called `{{ package_name }}` on disk.

`template/{{ _copier_conf.answers_file }}.jinja` renders to `.copier-answers.yml` in the generated project. It stores the answers plus the template version and is what makes `copier update` possible, so it must stay committed in generated projects.

## Environment Variable

The following environment variables may be used to configure the generated project:

| Environment Variable | Purpose | Default Value | Allowed Values |
|----------------------|-|-|-|
| LOG_LEVEL            | Sets the default log level. | "INFO" | See [Python Standard Library API-Reference](https://docs.python.org/3/library/logging.html#logging-levels) |
