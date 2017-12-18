from setuptools import setup
import sys


requires = [
        'bitarray',
        'lxml',
]
if sys.version_info < (3,0):
    requires.append('future')

setup(
    name='kbinxml',
    version='1.1',
    entry_points = {
        'console_scripts': ['kbinxml=kbinxml:main'],
    },
    packages=['kbinxml'],
    url='https://github.com/mon/kbinxml/',
    author='mon',
    author_email='me@mon.im',
    install_requires=requires
)
