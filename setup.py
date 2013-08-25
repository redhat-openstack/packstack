import os
from setuptools import setup, find_packages

from packstack import version


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="packstack",
    version=version.version_string(),
    author="Derek Higgins",
    author_email="derekh@redhat.com",
    description=("A utility to install openstack"),
    license="ASL 2.0",
    keywords="openstack",
    url="https://github.com/fedora-openstack/packstack",
    packages=find_packages('.'),
    include_package_data=True,
    long_description=read('README'),
    zip_safe=False,
    install_requires=['netaddr'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    scripts=["bin/packstack"]
)
