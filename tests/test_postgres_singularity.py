"""Unit coverage for the managed PostgreSQL Singularity lifecycle."""

import contextlib
import importlib
import os
import signal
import subprocess
from types import SimpleNamespace
from unittest import mock

import click
import pytest
from click.testing import CliRunner

from planemo import options
from planemo.cli import planemo
from planemo.database.factory import (
    database_source_context,
    started_database_source,
)
from planemo.database.interface import DatabaseConfigurationError
from planemo.database.postgres_singularity import (
    CONTAINER_SOCKET_DIRECTORY,
    DEFAULT_DOCKERIMAGE,
    POSTGRES_SOCKET_NAME,
    SingularityPostgresDatabaseSource,
)
from .test_utils import create_test_context

serve_module = importlib.import_module("planemo.galaxy.serve")


def _source(tmp_path, **kwds):
    source = SingularityPostgresDatabaseSource(
        postgres_storage_location=str(tmp_path / "postgres"),
        **kwds,
    )
    source.startup_timeout = 5
    source.stop_timeout = 2
    return source


@click.command()
@options.profile_database_options()
def _database_options_command(**kwds):
    click.echo(f"{kwds['postgres_storage_location']}|{kwds['singularity_cmd']}")


@pytest.mark.parametrize("storage_option", ("--postgres-storage-location", "--postgres_storage_location"))
def test_profile_database_options_accept_storage_aliases_and_singularity_command(tmp_path, storage_option):
    storage = str(tmp_path / "postgres")
    result = CliRunner().invoke(
        _database_options_command,
        [storage_option, storage, "--singularity_cmd", "apptainer"],
        obj=create_test_context(),
    )
    assert result.exit_code == 0, result.output
    assert result.output.strip() == f"{storage}|apptainer"


def test_database_administration_requires_persistent_storage():
    with mock.patch("planemo.database.postgres_singularity.mkdtemp") as make_temp_directory:
        with pytest.raises(DatabaseConfigurationError, match="--postgres-storage-location"):
            started_database_source(database_type="postgres_singularity", for_database_commands=True)
    make_temp_directory.assert_not_called()


def test_database_command_reports_missing_persistent_storage():
    result = CliRunner().invoke(planemo, ["database_list", "--database_type", "postgres_singularity"])
    assert result.exit_code == 2
    assert "requires --postgres-storage-location" in result.output


def test_profile_options_are_owned_by_the_singularity_backend(tmp_path):
    source = _source(tmp_path, singularity_cmd="apptainer", singularity_sudo=False)

    assert source.profile_options() == {
        "postgres_storage_location": str(tmp_path / "postgres"),
        "singularity_cmd": "apptainer",
        "singularity_sudo": False,
    }


def test_start_waits_for_pg_isready_not_just_initialized_cluster(tmp_path):
    source = _source(tmp_path, singularity_cmd="apptainer")
    pgdata = tmp_path / "postgres" / "pgdata"
    pgdata.mkdir(parents=True)
    (pgdata / "PG_VERSION").write_text("14")
    process = mock.Mock(pid=42)
    process.poll.return_value = None

    with (
        mock.patch("planemo.database.postgres_singularity.shell_process", return_value=process) as shell_process,
        mock.patch.object(source, "_database_is_ready", side_effect=(False, True)) as database_is_ready,
        mock.patch("planemo.database.postgres_singularity.time.sleep") as sleep,
    ):
        source.start()

    assert database_is_ready.call_count == 2
    sleep.assert_called_once_with(1)
    command = shell_process.call_args.args[0]
    assert command[:2] == ["apptainer", "run"]
    assert "POSTGRES_INITDB_ARGS=--encoding=UTF-8" in command
    assert shell_process.call_args.kwargs["start_new_session"] is True
    assert shell_process.call_args.kwargs["stderr"] is subprocess.STDOUT
    assert shell_process.call_args.kwargs["stdout"].name == str(tmp_path / "postgres" / "postgres.log")


def test_readiness_probe_uses_containerized_pg_isready_over_socket(tmp_path):
    source = _source(tmp_path, singularity_cmd="apptainer")
    os.makedirs(source.database_socket_dir)
    open(os.path.join(source.database_socket_dir, POSTGRES_SOCKET_NAME), "w").close()
    completed = subprocess.CompletedProcess([], 0)

    with mock.patch("planemo.database.postgres_singularity.subprocess.run", return_value=completed) as run:
        assert source._database_is_ready()

    command = run.call_args.args[0]
    assert command[:2] == ["apptainer", "exec"]
    assert f"{source.database_socket_dir}:{CONTAINER_SOCKET_DIRECTORY}" in command
    assert f"docker://{DEFAULT_DOCKERIMAGE}" in command
    assert command[-7:] == [
        "pg_isready",
        "--host",
        CONTAINER_SOCKET_DIRECTORY,
        "--username",
        "galaxy",
        "--dbname",
        "postgres",
    ]


def test_start_reports_container_exit(tmp_path):
    source = _source(tmp_path)
    process = mock.Mock(pid=42)
    process.poll.return_value = 17

    with mock.patch("planemo.database.postgres_singularity.shell_process", return_value=process):
        with pytest.raises(RuntimeError, match="code 17"):
            source.start()

    assert source.running_process is None


def test_startup_timeout_stops_the_container(tmp_path):
    source = _source(tmp_path)
    process = mock.Mock(pid=42)
    process.poll.return_value = None

    with (
        mock.patch("planemo.database.postgres_singularity.shell_process", return_value=process),
        mock.patch.object(source, "_database_is_ready", return_value=False),
        mock.patch.object(source, "stop") as stop,
        mock.patch("planemo.database.postgres_singularity.time.monotonic", side_effect=(0, 6)),
    ):
        with pytest.raises(RuntimeError, match="did not become ready"):
            source.start()

    stop.assert_called_once_with()


def test_stop_waits_then_escalates_the_owned_process_group(tmp_path):
    source = _source(tmp_path)
    process = mock.Mock(pid=42)
    process.poll.return_value = None
    process.wait.side_effect = (subprocess.TimeoutExpired("singularity", 2), 0)
    source.running_process = process

    with mock.patch("planemo.database.postgres_singularity.os.killpg") as killpg:
        source.stop()

    assert killpg.call_args_list == [mock.call(42, signal.SIGTERM), mock.call(42, signal.SIGKILL)]
    assert process.wait.call_args_list == [mock.call(timeout=2), mock.call(timeout=2)]
    assert source.running_process is None


def test_create_list_and_delete_target_named_databases(tmp_path):
    source = _source(tmp_path)
    storage = tmp_path / "postgres"
    storage.mkdir()
    marker = storage / "must-not-be-deleted"
    marker.write_text("persistent cluster")
    commands = []

    def communicate(command_builder):
        commands.append(command_builder.command)
        if "--list" in command_builder.command:
            return b"postgres | galaxy\ntest1234 | galaxy\n"
        return b""

    source._communicate = communicate

    source.create_database("test1234")
    assert source.list_databases() == ["postgres", "test1234"]
    source.delete_database("test1234")

    assert commands[0][-2:] == ["--command", "create database test1234;"]
    assert commands[1][-1] == "--list"
    assert commands[2][-2:] == ["--command", "drop database test1234;"]
    assert marker.read_text() == "persistent cluster"
    for command in commands:
        assert command[:2] == ["singularity", "exec"]
        assert ["--dbname", "postgres"] == command[command.index("--dbname") : command.index("--dbname") + 2]


def test_database_source_context_stops_singularity_source(tmp_path):
    source = mock.Mock()
    source.keep_running_after_database_commands = False
    with mock.patch("planemo.database.factory.started_database_source", return_value=source):
        with database_source_context(
            database_type="postgres_singularity",
            postgres_storage_location=str(tmp_path / "postgres"),
        ) as yielded:
            assert yielded is source
            source.stop.assert_not_called()
    source.stop.assert_called_once_with()


def test_managed_galaxy_stops_before_its_database_context_exits(monkeypatch):
    events = []
    config = SimpleNamespace(
        kill=lambda: events.append("galaxy stopped"),
        cleanup=lambda: events.append("configuration cleaned"),
    )

    @contextlib.contextmanager
    def configured_serve(*args, **kwds):
        events.append("database started")
        try:
            yield config
        finally:
            if kwds.get("stop_daemon_after_serve"):
                config.kill()
            events.append("database stopped")

    monkeypatch.setattr(serve_module, "serve", configured_serve)

    with serve_module.serve_daemon(SimpleNamespace(verbose=False)):
        events.append("caller finished")

    assert events == [
        "database started",
        "caller finished",
        "galaxy stopped",
        "database stopped",
        "configuration cleaned",
    ]


def test_managed_galaxy_exception_has_single_shutdown_owner(monkeypatch):
    config = SimpleNamespace(kill=mock.Mock(), cleanup=mock.Mock())

    @contextlib.contextmanager
    def configured_serve(*args, **kwds):
        try:
            yield config
        finally:
            if kwds.get("stop_daemon_after_serve"):
                config.kill()

    monkeypatch.setattr(serve_module, "serve", configured_serve)

    with pytest.raises(RuntimeError, match="caller failed"):
        with serve_module.serve_daemon(SimpleNamespace(verbose=False)):
            raise RuntimeError("caller failed")

    config.kill.assert_called_once_with()
    config.cleanup.assert_called_once_with()
