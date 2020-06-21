import mimetypes
import os
import re
from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import click
from azure.common import AzureHttpError
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContainerClient, ContentSettings
from essentials.diagnostics import StopWatch
from essentials.exceptions import InvalidArgument
from essentials.folders import get_file_extension

from pyazblob.logs import get_app_logger

from ..errors import ConfigurationError, UploadFailure
from ..settings import Settings

logger = get_app_logger()


def get_env_variable_or_throw(name: str, alternative_parameter: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigurationError(
            f'Missing parameter "{alternative_parameter}", '
            f'and environmental variable "{name}". Provide one of them, '
            "to resolve this error."
        )
    return value


class AccountSettings:
    _key: str
    _name: str

    def __init__(self, account_name: Optional[str], account_key: Optional[str]):
        self._name = account_name or get_env_variable_or_throw(
            "PYAZ_ACCOUNT_NAME", "--account-name"
        )
        self._key = account_key or get_env_variable_or_throw(
            "PYAZ_ACCOUNT_KEY", "--account-key"
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def key(self) -> str:
        return self._key


def validate_root_path(root_path: Path) -> None:
    if not root_path:
        raise InvalidArgument("Missing root path")

    if not root_path.exists():
        raise InvalidArgument(
            f"Error: Invalid value for '--path': \"{root_path}\" does not exist"
        )

    if not root_path.is_dir():
        raise InvalidArgument(
            f"Error: Invalid value for '--path': \"{root_path}\" is not a folder"
        )


def remove_empty_folders(blob_name: str) -> str:
    # avoid "<no-name>"" folders:
    while "//" in blob_name:
        blob_name = blob_name.replace("//", "/")

    while "\\\\" in blob_name:
        blob_name = blob_name.replace("\\\\", "\\")

    while blob_name.startswith("\\") or blob_name.startswith("/"):
        blob_name = blob_name[1:]

    return blob_name


def upload_file(
    file_path: Path,
    container_name: str,
    blob_name: str,
    service: ContainerClient,
    settings: Settings,
    force: bool,
) -> None:
    file_extension = get_file_extension(file_path)

    if file_extension in settings.mimes:
        file_mime = settings.mimes.get(file_extension)
    else:
        file_mime = mimetypes.guess_type(file_path)[0]

    blob_name = remove_empty_folders(blob_name)
    logger.debug("Using mime `%s` for blob `%s`", file_mime, blob_name)
    logger.debug("File `%s` mapped to blob `%s`", file_path, blob_name)
    logger.info(f"Uploading `{blob_name}` ({file_mime})")

    with open(file_path, mode="rb") as file:
        service.upload_blob(
            name=blob_name,
            data=file,
            content_settings=ContentSettings(content_type=file_mime),
            overwrite=force,
        )


class UploadedFile:
    def __init__(self, file_path: Path, blob_name: str, success: bool):
        self.blob_name = blob_name
        self.success = success
        self.file_path = file_path

    @property
    def failed(self) -> bool:
        return not self.success


def read_lines_strip_comments(file_path: Path):
    with open(str(file_path), mode="rt", encoding="utf8") as file:
        lines = file.readlines()
    lines = [re.sub("#.+$", "", x).strip() for x in lines]
    return [line for line in lines if line]


def load_ignored() -> List[str]:
    ignore_file = Path(Path.cwd() / ".pyazblobignore")

    if not ignore_file.is_file():
        # no ignore file specified
        return []

    return read_lines_strip_comments(ignore_file)


def get_paths(
    root_path: Path, recurse: bool, ignored_paths: List[str],
) -> Iterable[Path]:
    validate_root_path(root_path)

    child: Path

    for child in root_path.iterdir():
        if child.is_symlink():
            continue

        if child.is_dir():
            if not recurse:
                continue
            else:
                # upload children files
                yield from get_paths(
                    child, recurse, ignored_paths,
                )
                continue

        if any(
            fnmatch(str(child), ignored_pattern) for ignored_pattern in ignored_paths
        ):
            logger.info("Ignoring... " + str(child))
            continue

        yield child


def get_all(
    root_path: Path,
    paths_prefix: str,
    cut_path: str,
    recurse: bool,
    ignored_paths: List[str],
) -> Iterable[Tuple[Path, str]]:
    for file_path in get_paths(root_path, recurse, ignored_paths):
        blob_name = paths_prefix + str(file_path)[len(cut_path) :]
        yield file_path, blob_name


def upload_from_path(
    file_path: Path,
    container_name: str,
    blob_name: str,
    service: ContainerClient,
    settings: Settings,
    force: bool,
) -> UploadedFile:
    try:
        upload_file(file_path, container_name, blob_name, service, settings, force)

        return UploadedFile(file_path, blob_name, True)
    except Exception as error:
        logger.error(
            "Error while uploading file: " + str(file_path) + " - " + str(error),
        )
        return UploadedFile(file_path, blob_name, False)


def upload_parallel(
    root_path: Path,
    container_name: str,
    paths_prefix: str,
    cut_path: str,
    recurse: bool,
    force: bool,
    service: ContainerClient,
    ignored_paths: List[str],
    settings: Settings,
    concurrency: int,
):
    args_generator = (
        (file_path, container_name, blob_name, service, settings, force)
        for file_path, blob_name in get_all(
            root_path, paths_prefix, cut_path, recurse, ignored_paths
        )
    )

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        for result in executor.map(lambda m: upload_from_path(*m), args_generator):
            yield result


def first_leaf(a):
    return a[: a.index("/")] if "/" in a else a


def get_blob_client(account_settings: AccountSettings) -> BlobServiceClient:
    connection_string = (
        "DefaultEndpointsProtocol=https;"
        f"AccountName={account_settings.name};"
        f"AccountKey={account_settings.key};"
        "EndpointSuffix=core.windows.net"
    )
    return BlobServiceClient.from_connection_string(conn_str=connection_string)


@click.command(name="upload")
@click.option(
    "-p",
    "--path",
    help="root path from which bulk upload should start.",
    required=True,
)
@click.option(
    "-cn",
    "--container-name",
    help="name of the container where files should be uploaded.",
    required=True,
)
@click.option(
    "-c",
    "--cut-path",
    help="portion of root path to cut from uploaded blobs.",
    required=False,
)
@click.option(
    "-r",
    "--recurse",
    help="recursively upload files in subfolders",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
)
@click.option(
    "-f",
    "--force",
    help="whether to overwrite existing files with the same path",
    is_flag=True,
    required=False,
    default=False,
    show_default=True,
)
@click.option(
    "-a",
    "--account-name",
    help="storage account name; if not provided, the "
    + "env variable `STORAGE_ACCOUNT_NAME` is read.",
    required=False,
)
@click.option(
    "-k",
    "--account-key",
    help="storage account key; if not provided, the "
    + "env variable `STORAGE_ACCOUNT_KEY` is read.",
    required=False,
)
@click.option(
    "--continue-on-failure",
    help="continues on failure",
    is_flag=True,
    required=False,
    default=True,
    show_default=True,
)
@click.option(
    "--concurrency",
    help="concurrency",
    required=False,
    default=10,
    show_default=True,
    type=int,
)
def upload_command(
    path: str,
    container_name: str,
    cut_path: str,
    recurse: bool,
    force: bool,
    account_name: str,
    account_key: str,
    continue_on_failure: bool,
    concurrency: int,
):
    """
    Bulk uploads files found under the given directory, to an
    Azure Storage Blob Service with the given name.
    """

    if cut_path:
        if not path.startswith(cut_path):
            raise InvalidArgument("The root path must start with given --cut-path")
    else:
        cut_path = path

    if "/" in container_name:
        paths_prefix = container_name[container_name.index("/") + 1 :]
        container_name = first_leaf(container_name)
    else:
        paths_prefix = ""

    # read ignored files
    ignored_paths = load_ignored()

    settings = Settings.from_settings_file()
    exit_code = 0

    account_settings = AccountSettings(account_name, account_key)

    logger.info(
        f"Uploading files to account `{account_settings.name}`, "
        f"container: `{container_name}`, with concurrency {concurrency}"
    )

    try:
        service = get_blob_client(account_settings)
        try:
            logger.debug("Creating the container if it doesn't exist...")

            service.create_container(container_name)
        except ResourceExistsError:
            pass

        logger.debug("Getting container service...")

        container_service = service.get_container_client(container_name)

        logger.debug("Starting job...")

        with StopWatch() as sw:
            for item in upload_parallel(
                Path(path),
                container_name,
                paths_prefix,
                cut_path,
                recurse,
                force,
                container_service,
                ignored_paths,
                settings,
                concurrency,
            ):
                if item.failed:
                    if continue_on_failure:
                        exit_code = 2
                    else:
                        raise UploadFailure()

        logger.info(f"Elapsed: {sw.elapsed_s:.2f}s")
    except (
        AzureHttpError,
        InvalidArgument,
        ConfigurationError,
        UploadFailure,
    ) as error:
        logger.error(str(error))
        exit(1)
    except KeyboardInterrupt:
        logger.info("User interrupted")
        exit(1)

    exit(exit_code)
