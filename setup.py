from setuptools import setup, find_packages
import os

version = '0.1'
setup(
    name="kwikstats",
    version=version,
    description="Quick way to view time based statistics",
    keywords='kwikstats',
    author='Deep Compute, LLC',
    author_email="contact@deepcompute.com",
    url="https://github.com/deep-compute/kwikstats",
    download_url="https://github.com/deep-compute/kwikstats/tarball/%s" % version,
    license='MIT License',
    install_requires=[
        'basescript',
        'tornado',
    ],
    package_dir={'kwikstats': 'kwikstats'},
    packages=find_packages('.'),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "kwikstats = kwikstats:main",
        ]
    }

)
