from pyazblob import version
from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="pyazblob",
    version=version,
    description=(
        "Python tool to upload files into Azure Storage Blob service "
        "from local file system"
    ),
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/RobertoPrevato/PyAzBlob",
    author="RobertoPrevato",
    author_email="roberto.prevato@gmail.com",
    keywords="azure storage python bulk upload blob service",
    license="MIT",
    packages=["pyazblob", "pyazblob.commands"],
    entry_points={"console_scripts": ["pyazblob=pyazblob.main:main"]},
    install_requires=[
        "click==8.1.3",
        "essentials~=1.1.5",
        "azure-storage-blob==12.13.1",
        "azure-common==1.1.28",
        "azure-core==1.25.0",
    ],
    include_package_data=True,
)
