"""Create a DatabaseSource from supplied planemo configuration."""

import contextlib
from typing import Optional

import click

from .interface import DatabaseSource
from .postgres import LocalPostgresDatabaseSource
from .postgres_docker import DockerPostgresDatabaseSource
from .postgres_singularity import SingularityPostgresDatabaseSource


def create_database_source(profile_directory: Optional[str] = None, **kwds) -> DatabaseSource:
    """Return a :class:`planemo.database.interface.DatabaseSource` for configuration."""
    database_type = kwds.get("database_type", "auto")
    if database_type == "auto":
        raise Exception(
            "Managing a database server requires naming one - pass --database_type with "
            "postgres, postgres_docker or postgres_singularity."
        )

    if database_type == "postgres":
        return LocalPostgresDatabaseSource(**kwds)
    elif database_type == "postgres_docker":
        return DockerPostgresDatabaseSource(**kwds)
    elif database_type == "postgres_singularity":
        return SingularityPostgresDatabaseSource(profile_directory=profile_directory, **kwds)
    # TODO
    # from .sqlite import SqliteDatabaseSource
    # elif database_type == "sqlite":
    #     return SqliteDatabaseSource(**kwds)
    else:
        raise Exception("Unknown database type [%s]." % database_type)


def started_database_source(profile_directory: Optional[str] = None, **kwds) -> DatabaseSource:
    """Construct and start a :class:`planemo.database.interface.DatabaseSource`."""
    database_type = kwds.get("database_type", "auto")
    if (
        database_type == "postgres_singularity"
        and profile_directory is None
        and not kwds.get("postgres_storage_location")
    ):
        raise click.UsageError(
            "Database administration with postgres_singularity requires --postgres-storage-location so separate "
            "commands operate on the same PostgreSQL cluster."
        )
    database_source = create_database_source(profile_directory=profile_directory, **kwds)
    database_source.start()
    return database_source


@contextlib.contextmanager
def database_source_context(profile_directory: Optional[str] = None, **kwds):
    """Yield a started database source and stop it when doing so preserves its data."""
    database_source = started_database_source(profile_directory=profile_directory, **kwds)
    try:
        yield database_source
    finally:
        if not database_source.keep_running_after_database_commands:
            database_source.stop()


__all__ = (
    "create_database_source",
    "database_source_context",
    "started_database_source",
)
