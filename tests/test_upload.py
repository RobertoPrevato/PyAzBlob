import os

from pyazblob.commands.upload import get_env_variable_or_throw


def test_get_env_variable_or_throw():
    os.environ["X_Example"] = "Example"

    assert get_env_variable_or_throw("X_Example", "--foo") == "Example"
