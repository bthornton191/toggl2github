from setuptools import setup

setup(
    name='toggl2github',
    version='0.0.1',
    description='A Python package for syncing Toggl projects with Github projects.',
    author='Ben Thornton',
    author_email='bthorn191@gmail.com',
    url='https://github.com/bthornton191/toggl2github',
    packages=['toggl2github'],
    install_requires=[
        'requests',
        'keyring',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)
