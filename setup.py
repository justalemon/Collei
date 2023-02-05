from setuptools import setup


def read_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="collei",
    version="0.0.1",
    description="Lemon's set of tools to make development easier",
    long_description=read_description(),
    long_description_content_type="text/markdown",
    author="Lemon",
    author_email="justlemoncl@gmail.com",
    url="https://github.com/LeekByLemon/Collei",
    packages=[
        "collei"
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    install_requires=[
        "Jinja2>=3.1.2,<4.0.0"
    ],
    python_requires=">=3.8",
    package_data={
        "": [
            "**/templates/**/*.*"
        ]
    },
    include_package_data=True
)
