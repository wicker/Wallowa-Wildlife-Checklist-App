import io

from setuptools import find_packages, setup

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='wallowawildlife',
    version='1.0.0',
    url='https://github.com/wicker/Wallowa-Wildlife-Checklist-App',
    license='GPLv3.0',
    maintainer='Jenner Hanni',
    maintainer_email='jenner@wickerbox.net',
    description='Allows users to log in and maintain wildlife checklists.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
