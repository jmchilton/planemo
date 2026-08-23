"""Unit tests for how a database backend gets picked.

Nothing here probes ``PATH`` - the presence of a ``psql`` client says nothing about
whether a postgres server is reachable, so a backend is only used when it is named.
"""

import os
from unittest import mock

import pytest

from planemo.database import create_database_source
from planemo.galaxy.config import DATABASE_LOCATION_TEMPLATE
from planemo.galaxy.profiles import (
    _create_profile_local,
    _profile_to_database_identifier,
)
from .test_utils import TempDirectoryContext


def test_create_database_source_requires_a_named_backend():
    for kwds in ({}, {"database_type": "auto"}):
        with pytest.raises(Exception) as exc_info:
            create_database_source(**kwds)
        assert "--database_type" in str(exc_info.value), kwds


def test_create_database_source_dispatches_on_the_named_backend():
    source = create_database_source(database_type="postgres")
    assert type(source).__name__ == "LocalPostgresDatabaseSource"


def test_profile_defaults_to_its_own_sqlite_file():
    for kwds in ({}, {"database_type": None}, {"database_type": "auto"}, {"database_type": "sqlite"}):
        with TempDirectoryContext() as temp_directory_context:
            profile_directory = temp_directory_context.temp_directory
            with mock.patch("planemo.galaxy.profiles.started_database_source") as started_database_source:
                options = _create_profile_local(None, profile_directory, "profile1234", dict(kwds))
            started_database_source.assert_not_called()
            assert options["database_type"] == "sqlite", kwds
            database_location = os.path.join(profile_directory, "galaxy.sqlite")
            assert options["database_connection"] == DATABASE_LOCATION_TEMPLATE % database_location, kwds


def test_profile_creates_a_database_for_a_named_backend():
    database_source = mock.Mock()
    database_source.sqlalchemy_url.return_value = "postgresql://galaxy@localhost/plnmoprof_profile1234"
    with TempDirectoryContext() as temp_directory_context:
        with mock.patch("planemo.galaxy.profiles.started_database_source", return_value=database_source):
            options = _create_profile_local(
                None, temp_directory_context.temp_directory, "profile1234", {"database_type": "postgres"}
            )
    identifier = _profile_to_database_identifier("profile1234")
    database_source.create_database.assert_called_once_with(identifier)
    assert options["database_type"] == "postgres"
    assert options["database_connection"] == "postgresql://galaxy@localhost/plnmoprof_profile1234"


def test_profile_creation_failure_is_not_swallowed_into_sqlite():
    database_source = mock.Mock()
    database_source.create_database.side_effect = RuntimeError("role does not exist")
    with TempDirectoryContext() as temp_directory_context:
        with mock.patch("planemo.galaxy.profiles.started_database_source", return_value=database_source):
            with pytest.raises(RuntimeError):
                _create_profile_local(
                    None, temp_directory_context.temp_directory, "profile1234", {"database_type": "postgres"}
                )
