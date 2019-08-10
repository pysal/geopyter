# coding: utf-8

from setuptools import setup, find_packages

from distutils.command.build_py import build_py

import os

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get __version__ from geopyter/__init__.py without importing the package
# __version__ has to be defined in the first line
with open('geopyter/__init__.py', 'r') as f:
    exec(f.readline())

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

def _get_requirements_from_files(groups_files):
    groups_reqlist = {}

    for k,v in groups_files.items():
        with open(v, 'r') as f:
            pkg_list = f.read().splitlines()
        groups_reqlist[k] = pkg_list

    return groups_reqlist

def setup_package():
    # get all file endings and copy whole file names without a file suffix
    # assumes nested directories are only down one level
    _groups_files = {
        'base': 'requirements.txt',
        'plus_conda': 'requirements_plus_conda.txt',
        'plus_pip': 'requirements_plus_pip.txt',
        'dev': 'requirements_dev.txt',
        'docs': 'requirements_docs.txt'
    }

    reqs = _get_requirements_from_files(_groups_files)
    install_reqs = reqs.pop('base')
    extras_reqs = reqs

    setup(
        name='geopyter',
        version=__version__,
        description="Geographical Python Teaching Resource",
        long_description=long_description,
        maintainer="PySAL Developers",
        maintainer_email='pysal-dev@googlegroups.com',
        url='http://pysal.org/geopyter',
        download_url='https://pypi.python.org/pypi/geopyter',
        license='BSD',
        py_modules=['geopyter'],
        packages=find_packages(),
        test_suite='nose.collector',
        tests_require=['nose'],
        keywords='spatial statistics',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: GIS',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7'
        ],
        install_requires=install_reqs,
        extras_require=extras_reqs,
        cmdclass={'build_py': build_py},
        python_requires='>3.5'
    )


if __name__ == '__main__':
    setup_package()
