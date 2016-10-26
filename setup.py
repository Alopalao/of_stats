"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
import sys

from subprocess import call
from setuptools import setup, Command

if 'VIRTUAL_ENV' in os.environ and 'TRAVIS' not in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'


class Doctest(Command):
    """Run Sphinx doctest."""

    if sys.argv[-1] == 'test':
        print('Running examples in documentation')
        call('make doctest -C docs/', shell=True)


class Linter(Command):
    """Run several code linters."""

    description = 'Run many code linters. It may take a while'
    user_options = []

    def __init__(self, *args, **kwargs):
        """Define linters and a message about them."""
        super().__init__(*args, **kwargs)
        self.linters = ['pep257', 'pyflakes', 'mccabe', 'isort', 'pep8',
                        'pylint']
        self.extra_msg = 'It may take a while. For a faster version (and ' \
                         'less checks), run "quick_lint".'

    def initialize_options(self):
        """For now, options are ignored."""
        pass

    def finalize_options(self):
        """For now, options are ignored."""
        pass

    def run(self):
        """Run pylama and radon."""
        files = 'tests setup.py pyof'
        print('running pylama with {}. {}'.format(', '.join(self.linters),
                                                  self.extra_msg))
        cmd = 'pylama -l {} {}'.format(','.join(self.linters), files)
        call(cmd, shell=True)
        print('Low grades (<= C) for Cyclomatic Complexity:')
        call('radon cc --min=C ' + files, shell=True)
        print('Low grades (<= C) for Maintainability Index:')
        call('radon mi --min=C ' + files, shell=True)


class FastLinter(Linter):
    """Same as Linter, but without the slow pylint."""

    description = 'Same as "lint", but much faster (no pylama_pylint).'

    def __init__(self, *args, **kwargs):
        """Remove slow linters and redefine the message about the rest."""
        super().__init__(*args, **kwargs)
        self.linters.remove('pylint')
        self.extra_msg = 'This a faster version of "lint", without pylint. ' \
                         'Run the slower "lint" after solving these issues:'


def retrieve_apps(kytos_napps_path):
    """
    Retrieves the list of files within each app directory
    """
    apps = []
    for napp_name in os.listdir("./kytos"):
        app_files = []
        app_path = os.path.join("./kytos", napp_name)
        for file_name in os.listdir(app_path):
            file_path = os.path.join(app_path, file_name)
            if os.path.isfile(file_path):  # Only select files
                app_files.append(file_path)
        apps.append((os.path.join(kytos_napps_path, napp_name), app_files))
    return apps


setup(name='kyco-core-napps',
      version='1.1.0a5.dev1',
      description='Core Napps developed by Kytos Team',
      url='http://github.com/kytos/kyco-core-napps',
      author='Kytos Team',
      author_email='of-ng-dev@ncc.unesp.br',
      license='MIT',
      install_requires=['python-openflow >= 1.1.0a2.post2'],
      data_files=retrieve_apps(os.path.join(BASE_ENV,
                                            'var/lib/kytos/napps/kytos/')),
      cmdclass={
          'lint': Linter,
          'quick_lint': FastLinter
      },
      zip_safe=False)
