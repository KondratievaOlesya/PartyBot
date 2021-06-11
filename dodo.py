#!/usr/bin/env python3
"""
Dafault: create wheel
"""
import glob
from doit.tools import create_folder

DOIT_CONFIG = {'default_tasks': ['all']}


def task_gitclean():
    """Clean all generated files not tracked by GIT."""
    return {
        'actions': ['git clean -xdf'],
    }


def task_html():
    """Make HTML documentation."""
    return {
        'actions': ['sphinx-autobuild doc doc/_build/html'],
    }


def task_html_translated():
    """Make HTML documentation."""
    return {
        'actions': ['sphinx-autobuild doc doc/_build/html'],
    }


def task_test():
    """Preform tests."""
    yield {'actions': ['coverage run -m unittest -v tests/test_bot.py'], 'name': "run_bot"}
    yield {'actions': ['coverage report > test_bot'], 'verbosity': 2, 'name': "report_bot"}
    yield {'actions': ['coverage run -m unittest -v tests/test_kudago.py'], 'name': "run_kudago"}
    yield {'actions': ['coverage report > test_kudago'], 'verbosity': 2, 'name': "report_kudago"}
    yield {'actions': ['coverage run -m unittest -v tests/test_tools.py'], 'name': "run_tools"}
    yield {'actions': ['coverage report > test_tools'], 'verbosity': 2, 'name': "report_tools"}


def task_sdist():
    """Create source distribution."""
    return {
        'actions': ['python -m build -s'],
        'task_dep': ['gitclean'],
    }


def task_wheel():
    return {
        'actions': ['python -m build'],
    }


def task_app():
    """Run application."""
    return {
        'actions': ['python -m partybot']
    }


def task_style():
    """Check style against pylint."""
    return {
        'actions': ['pylint partybot']
    }


def task_check():
    """Perform all checks."""
    return {
        'actions': None,
        'task_dep': ['style', 'test']
    }


def task_all():
    """Perform all build task."""
    return {
        'actions': None,
        'task_dep': ['check', 'wheel']
    }
