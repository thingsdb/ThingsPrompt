"""
Upload to PyPI

python3 setup.py sdist
twine upload --repository pypitest dist/thingsprompt-X.X.X.tar.gz
twine upload --repository pypi dist/thingsprompt-X.X.X.tar.gz
"""
from setuptools import setup, find_packages

try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except IOError:
    long_description = ''

setup(
    name='thingsprompt',
    version='0.1.19',  # Update version in thingsprompt as well
    description='ThingsDB Prompt',
    url='https://github.com/thingsdb/ThingsPrompt',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jeroen van der Heijden',
    author_email='jeroen@transceptor.technology',
    scripts=['bin/thingsprompt'],
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends ',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'setproctitle',
        'python-thingsdb',
        'prompt-toolkit'
    ],
    keywords='database connector orm',
)
