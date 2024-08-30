from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="metamorphism",
    version="0.1.0",
    description="Implements metamorphic classes for Python",
    packages=find_packages(where="."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joshurtree/metamorphism",
    author="Josh Andrews",
    author_email="joshurtree@gmail.com",
    license="Apache",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    extra_requrie={
        "dev": ["twine>=5.1.1"]
    },
    python_requires=">=3.7"
)