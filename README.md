# PyAzBlob
Python tool to upload files into Azure Storage Blob Service from local file system.

## Disclaimer
[AzCopy](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10) is the official tool from Microsoft that, among many other things, implements bulk upload of files from local file system to Azure Storage Blob Service. PyAzBlob is a simple console application created in a few hours, mostly for fun and to practice with [Microsoft Azure Storage SDK for Python](https://github.com/Azure/azure-storage-python). However, it does implement a couple of features that I find useful for my personal use, that are not available in AzCopy.

```
  _____                     ____  _       _
 |  __ \         /\        |  _ \| |     | |
 | |__) |   _   /  \    ___| |_) | | ___ | |__
 |  ___/ | | | / /\ \  |_  /  _ <| |/ _ \| '_ \
 | |   | |_| |/ ____ \  / /| |_) | | (_) | |_) |
 |_|    \__, /_/    \_\/___|____/|_|\___/|_.__/
         __/ |
        |___/
```

## Features
* user friendly console application with integrated help
* recursive upload of files, keeping the same folder structure of local file system
* definition of ignored files by Unix-style glob patterns, in `.pyazblobignore` file (read from command CWD)
* supports definition of Azure Storage keys inside environmental variables or in .ini file
* supports specifying mime types by file extension in `settings.json` file (read from command CWD)

## Requirements
* Python >= 3.7

## How to use
Install:

```
pip install pyazblob
```

Verify that the CLI was installed:

```
pyazblob --help
```

### 2. Configure the Azure Storage

The CLI works by storage account name and key. These parameters can be either configured as environmental variables (recommended) or passed as input parameters.

**Recommendations**: if you are creating an Azure Storage for backups, use _Standard_ performance and [_LRS_ (Locally Redundant Storage)](https://docs.microsoft.com/en-us/azure/storage/storage-redundancy#locally-redundant-storage). Make sure to use *Private* containers if you want your data to be kept private.

#### 2.1 Useful links
* [Create a Storage Account](https://docs.microsoft.com/en-us/azure/storage/storage-create-storage-account)
* [Blob Storage Account pricing](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/)

Storage account name and settings can be found in the Azure Portal under `Settings > Access keys`.

![Azure Storage Settings](https://gist.githubusercontent.com/RobertoPrevato/9ff1fc2fe8acf15bbbe6094a836697f8/raw/0558d5bbf903e1991f69befb39e9e078f446c50e/azure-storage.jpg)

### 3. Run the console application

Example: upload all files from `/home/username/Pictures/` recursively, recreating the folder structure:

```bash
pyazblob -p /home/username/Pictures/ -r
```

Upload all files from `C:\Users\username\Documents\` recursively, keeping folder structure starting from `\Documents\`:
```bash
python pyazblob.py -p C:\Users\username\Documents\ -c C:\Users\username\
```

## Configuration options
* define ignored file paths (Unix-style globs) using `.pyazblobignore` file
* define Azure Storage name and key either by CLI option, or using the following environmental variables (for the key is is recommended to use the environmental variable):

| Name                | Scope          |
|---------------------|----------------|
| PYAZ_ACCOUNT_NAME   | account name   |
| PYAZ_ACCOUNT_KEY    | account key    |
