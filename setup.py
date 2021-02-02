"""Setup script for rhasspy-hermes-app package"""
import os

import setuptools

this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.rst"), "r") as readme_file:
    long_description = readme_file.read()

with open(os.path.join(this_dir, "requirements.txt"), "r") as requirements_file:
    requirements = requirements_file.read().splitlines()

with open(os.path.join(this_dir, "VERSION"), "r") as version_file:
    version = version_file.read().strip()

setuptools.setup(
    name="rhasspy-hermes-app",
    version=version,
    author="Koen Vervloesem",
    author_email="koen@vervloesem.eu",
    url="https://github.com/rhasspy/rhasspy-hermes-app",
    packages=setuptools.find_packages(),
    package_data={"rhasspyhermes_app": ["py.typed"]},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires=">=3.7",
)
