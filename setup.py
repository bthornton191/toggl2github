from setuptools import setup

setup(
    name='toggl2github',
    version='0.0.1',
    description='A Python package for syncing Toggl projects with Github projects.',
    author='Ben Thornton',
    author_email='bthorn191@gmail.com',
    url='https://github.com/bthornton191/toggle2github',
    packages=['toggl', 'githubpy'],
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)
