import re
from setuptools import setup


with open('wumpus/__init__.py') as f:
    contents = f.read()

    try:
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', contents, re.M
        ).group(1)
    except AttributeError:
        raise RuntimeError('Could not identify version') from None

    # look at this boilerplate code
    try:
        author = re.search(
            r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', contents, re.M
        ).group(1)
    except AttributeError:
        author = 'jay3332'

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.readlines()


setup(
    name='wumpus.py',
    author=author,
    url='https://github.com/jay3332/wumpus.py',
    project_urls={
        "Issue tracker": "https://github.com/jay3332/wumpus.py/issues",
        "Discord": "https://discord.gg/FqtZ6akWpd"
    },
    version='0.0.0',  # version  (Reserve 0.1.0 for the finished release)
    packages=[
        'wumpus',
        'wumpus.core',
        'wumpus.models',
        'wumpus.typings'
    ],
    license='MIT',
    description="An asynchronous wrapper around Discord's API.",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'docs': [
            'sphinx>=4.1.1',
            'karma_sphinx_theme>=0.0.8',
        ],
        'performance': [
            'orjson>=1.3.0'
        ]
    },
    python_requires='>=3.8.0',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
