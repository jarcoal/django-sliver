from setuptools import setup, find_packages

setup(
    name="django-sliver",
    version="0.1.0",
    description="Lightweight REST API built on top of Django generic views",
    long_description="Lightweight REST API built on top of Django generic views",
    keywords="django, api, rest",
    author="Jared Morse",
    author_email="jarcoal@gmail.com",
    url="https://github.com/jarcoal/django-sliver",
    license="BSD",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=['django >= 1.11', 'six'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
