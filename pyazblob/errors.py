class ConfigurationError(Exception):
    pass


class ApplicationError(Exception):
    pass


class UploadFailure(ApplicationError):
    pass
