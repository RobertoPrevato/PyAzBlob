"""
 * PyAzBlob 1.0.0 Python Azure Blob Service Bulk Uploader
 * https://github.com/RobertoPrevato/PyAzBlob
 *
 * Copyright 2017, Roberto Prevato
 * https://robertoprevato.github.io
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
"""
import re
import os
import errno
import fnmatch
import mimetypes
import time
from pathlib import Path
from core.diagnostics import StopWatch
from core.configuration import config
from core.literature import Scribe
from core.exceptions import ArgumentNullException, InvalidArgument, MissingDependency, ConfigurationError

__all__ = ["pyazupload", "pyazupload_entry"]

# I am a kind person..
try:
    from azure.storage.blob import BlockBlobService, ContentSettings
except ImportError:
    raise MissingDependency("azure-storage")


# load configuration
storage_config = config["StorageAccount"]

if not storage_config:
    raise ConfigurationError("missing StorageAccount configuration")

account_name = storage_config["name"]
account_key = storage_config["key"]
container_name = storage_config["container"]


if not account_key and not account_name:
    raise ConfigurationError("missing Storage Account configuration")

if not account_name:
    raise ConfigurationError("missing Storage Account name configuration")

if not account_key:
    raise ConfigurationError("missing Storage Account key configuration")

if not container_name:
    raise ConfigurationError("missing Storage Account destination container name configuration")


def first_leaf(a):
    return a[:a.index("/")] if "/" in a else a


# support for subfolders
if "/" in container_name:
    paths_prefix = container_name[container_name.index("/")+1:]
    container_name = first_leaf(container_name)
else:
    paths_prefix = ""


def read_lines_strip_comments(p):
    lines = [re.sub("#.+$", "", x) for x in Scribe.read_lines(p)]
    return [l for l in lines if l]


def load_ignored():
    calling_path = Path.cwd()
    ignore_file = Path(calling_path / ".pyazblobignore")

    if not ignore_file.is_file():
        # no ignore file specified
        return []

    return read_lines_strip_comments(str(ignore_file))


def pyazupload_file(file_path, blob_name, block_blob_service):
    file_mime = mimetypes.guess_type(file_path)[0]

    print("[*] Uploading {} ({})".format(file_path, file_mime))

    # avoid "<no-name>"" folders:
    while "//" in blob_name:
        blob_name = blob_name.replace("//", "/")

    while "\\\\" in blob_name:
        blob_name = blob_name.replace("\\\\", "\\")

    while blob_name.startswith("\\"):
        blob_name = blob_name[1:]

    block_blob_service.create_blob_from_path(
        container_name,
        blob_name,
        file_path,
        content_settings=ContentSettings(content_type=file_mime)
        )


def ensure_folder(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


ensure_folder("logs")


files_log = os.path.join("logs", "-".join([account_name, container_name.replace("\\", "_").replace("/", "_"), "files.log"]))


def pyazupload_entry(root_path,
                     cut_path=None,
                     ignored=None,
                     recurse=False,
                     force=False,
                     sleep=None,
                     block_blob_service=None):

    with StopWatch() as sw:
        pyazupload(root_path,
                   cut_path,
                   ignored,
                   recurse,
                   force,
                   sleep,
                   block_blob_service)

        print("[*] Elapsed: {0:.2f}s".format(sw.elapsed_s))


def pyazupload(root_path,
               cut_path=None,
               ignored=None,
               recurse=False,
               force=False,
               sleep=None,
               block_blob_service=None):
    """
    Bulk uploads files found under the given directory inside a configured Azure Storage Blob Service.
    
    :param root_path: root path from which bulk upload should start.
    :param cut_path: portion of root path to cut from uploaded blobs.
    :param ignored: ignored paths.
    :param recurse: whether to recursively upload files in subfolders.
    :param force: whether to force re-upload of files that were uploaded in a previous run (from files.log).
    :param block_blob_service: block blob service to use when uploading files.
    """
    if not ignored:
        ignored = []
       
    if force:
        files_uploaded_previously = []
        Scribe.write("", files_log)
    else:
        try:
            files_uploaded_previously = Scribe.read_lines(files_log)
        except FileNotFoundError:
            files_uploaded_previously = []

    if not block_blob_service:
        try:
            block_blob_service = BlockBlobService(account_name=account_name,
                                                  account_key=account_key)

            # create container (if it already exists, nothing bad happens)
            block_blob_service.create_container(container_name)
        except Exception as ex:
            raise RuntimeError("Cannot obtain instance of BlockBlobService. Error details: {}".format(ex))

    if not root_path:
        raise ArgumentNullException("root_path")

    p = Path(root_path)

    if not p.exists():
        raise InvalidArgument("given root path does not exist")

    if not p.is_dir():
        raise InvalidArgument("given root path is not a directory")

    # check cut_path
    if cut_path:
        if not root_path.startswith(cut_path):
            raise InvalidArgument("root_path must start with given cut_path")
    else:
        cut_path = root_path
    
    # read ignored files
    ignored_paths = load_ignored() + ignored

    # get files;
    items = (x for x in p.iterdir())
    for item in items:
        item_path = str(item)

        if os.path.islink(item_path):
            continue

        if item_path in files_uploaded_previously:
            print("[*] Skipping... " + item_path)
            continue

        if any(fnmatch.fnmatch(item_path, x) for x in ignored_paths):
            print("[*] Ignoring... " + item_path)
            continue

        # if the item is a folder, and work is recursive; go to its children
        if item.is_dir():
            if not recurse:
                continue
            else:
                # upload children;
                pyazupload(item_path,
                           cut_path,
                           ignored,
                           recurse,
                           force,
                           sleep,
                           block_blob_service)
                continue

        try:
            blob_name = paths_prefix + item_path[len(cut_path):]
          
            pyazupload_file(item_path, blob_name, block_blob_service)
        except Exception as ex:
            print("[*] Error while uploading file: " + item_path + " - " + str(ex))
        else:
            # add line to file containing list of uploaded files
            Scribe.add_lines([item_path], files_log)

            if sleep and sleep > 1:
                # sleep between uploads
                time.sleep(sleep / 1000.0)


