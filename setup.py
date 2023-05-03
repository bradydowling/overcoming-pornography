from setuptools import setup, find_packages

setup(
    name='overcoming-pornography',
    version='0.1.0',
    author='Brady Dowling',
    author_email='bradydowling@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
)