# PyAzBlob
Python tool to upload files into Azure Storage Blob Service. Comfortably transfers files from local file system into Azure Storage, by account name and key.

```
  _____                     ____  _       _                
 |  __ \         /\        |  _ \| |     | |               
 | |__) |   _   /  \    ___| |_) | | ___ | |__             
 |  ___/ | | | / /\ \  |_  /  _ <| |/ _ \| '_ \            
 | |   | |_| |/ ____ \  / /| |_) | | (_) | |_) |           
 |_|    \__, /_/    \_\/___|____/|_|\___/|_.__/            
         __/ |                                             
        |___/                                              
                                                           
  PyAzBlob | Azure Blob Service Bulk Uploader.             
  Written by Roberto Prevato <roberto.prevato@gmail.com>   
```

## Features
* user friendly console application with integrated help
* recursive upload of files, keeping the same folder structure of local file system
* supports any kind of file type that can be uploaded to Azure Storage
* definition of ignored files by Unix-style glob patterns
* stores uploaded files, to skip re-uploading same files to same Azure Storage container
* supports definition of Azure Storage keys inside environmental variables or in .ini file
* uses official [Microsoft Azure Storage SDK for Python](https://github.com/Azure/azure-storage-python), which automatically handles chunked upload of files greater than 64MB

## Note about lack of parallelism
This console application is **intentionally** made to upload files one by one, synchronously. This decision is not due to lack of technical knowledge, but consciuosly taken to limit number of web requests to Azure Storage service and the consumption of upload bandwidth. Most private users don't have great upload speed from their IP, anyway.

## Use cases
* save space in other locations, transferring files to Azure Cloud 
* creation of backups in Azure Cloud

## Requirements
* Python 3.4 =>
* Azure Storage

## How to use
1. Download or clone this repository
```bash
# clone repository:
git clone https://github.com/RobertoPrevato/PyAzBlob.git
```

### 2. Create Python virtual environment and restore dependencies

```bash
# Linux:
python3 -m venv env

env/bin/pip install -r requirements.txt
```

```bash
# Windows:
py -3 -m venv env
env\Scripts\pip install -r requirements.txt
```

### 3. Activate Python virtual environment (Optional)

```bash
# Linux:
source env/bin/activate
```

```bash
# Windows:
env\Scripts\activate.bat
```

### 4. Configure the Azure Storage

Configure Azure Storage account name and key in file `settings.ini`, which is read by Python console application when running the script. Key and name are used only by official [Microsoft Azure Storage SDK for Python](https://github.com/Azure/azure-storage-python), as can be verified in source code.

Storage account name and settings can be found in the Azure Portal under `Settings > Access keys`.

![Azure Storage Settings](https://gist.githubusercontent.com/RobertoPrevato/9ff1fc2fe8acf15bbbe6094a836697f8/raw/0558d5bbf903e1991f69befb39e9e078f446c50e/azure-storage.jpg)

### 5. Run the console application

If the environment was activated, use "python"; otherwise: `env\bin\python` in Linux or `env/Scripts/python` in Windows.

```bash
# display the help:
python pyazblob.py -h
```

![Help](https://gist.githubusercontent.com/RobertoPrevato/9ff1fc2fe8acf15bbbe6094a836697f8/raw/884083366a9ec2cab55421d9d9392485e1e9faf2/pyazblob-help.png)

Example: upload all files from `/home/username/Pictures/` recursively, and keeping folder structure starting from `/Pictures/`:

```bash
python pyazblob.py -p /home/username/Pictures/ -c /home/username/ -r
```

Upload all files from `C:\Users\username\Documents\` recursively, keeping folder structure starting from `\Documents\`:
```bash
python pyazblob.py -p C:\Users\username\Documents\ -c C:\Users\username\
```

![Bulk upload](https://gist.githubusercontent.com/RobertoPrevato/9ff1fc2fe8acf15bbbe6094a836697f8/raw/0558d5bbf903e1991f69befb39e9e078f446c50e/pyaz-upload.jpg)

## Configuration options
* define ignored file paths (Unix-style globs) using `.pyazblobignore` file
* define Azure Storage key, name and destination container name using `settings.ini` file, or following environmental variables

| Name                | Scope          |
|---------------------|----------------|
| PYAZ_ACCOUNT_NAME   | account name   |
| PYAZ_ACCOUNT_KEY    | account key    |
| PYAZ_CONTAINER_NAME | container name |
