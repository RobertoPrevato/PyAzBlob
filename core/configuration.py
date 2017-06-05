import os
import configparser

__all__ = ["config"]

config = configparser.ConfigParser()

# Read from settings.ini
config.read("settings.ini")

# Read from environmental variable, if specified (overriding values in settings.ini)
account_name = os.environ.get("PYAZ_ACCOUNT_NAME", None)
account_key = os.environ.get("PYAZ_ACCOUNT_KEY", None)
container_name = os.environ.get("PYAZ_CONTAINER_NAME", None)


if account_name:
    config["StorageAccount"]["name"] = account_name

if account_key:
    config["StorageAccount"]["key"] = account_key

if container_name:
    config["StorageAccount"]["container"] = container_name

