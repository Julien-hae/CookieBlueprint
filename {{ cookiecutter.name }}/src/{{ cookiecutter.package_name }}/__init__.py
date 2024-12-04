"""{{ cookiecutter.name }} main package.

Add your package documentation here.
"""

from {{ cookiecutter.package_name }}.common import logging_configuration

logging_configuration.configure_logger()
