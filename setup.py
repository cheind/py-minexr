from setuptools import setup
from pathlib import Path

THISDIR = Path(__file__).parent

with open(THISDIR/'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='minexr',
    author='Christoph Heindl',
    description='Minimal, standalone OpenEXR reader for single-part, uncompressed scan line files.',
    url='https://github.com/cheind/py-minexr',
    packages=['minexr'],
    version=open(THISDIR/'minexr'/'__init__.py').readlines()[-1].split()[-1].strip('\''),
    install_requires=['numpy'],
    long_description=long_description,
    long_description_content_type='text/markdown',
)