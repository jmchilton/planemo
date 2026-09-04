"""Unit tests for the Gravity-backed, package-installed Galaxy engine."""

from unittest.mock import patch

import click
import pytest

from planemo.galaxy.config import (
    installed_galaxy_config,
    validate_installed_options,
)
from .test_utils import create_test_context


class _Context:
    verbose = False

    def __init__(self, option_sources=None):
        self.option_sources = option_sources or {}

    def get_option_source(self, name, default=None):
        return self.option_sources.get(name, default)

    def vlog(self, message, *args, **kwds):
        pass


@pytest.mark.parametrize(
    ("kwds", "message"),
    [
        ({"galaxy_root": "/checkout"}, "--galaxy_root"),
        ({"install_galaxy": True}, "--install_galaxy"),
        ({"galaxy_branch": "dev"}, "--galaxy_branch"),
    ],
)
def test_installed_option_validation_rejects_checkout_options(kwds, message):
    with pytest.raises(click.UsageError, match=message):
        validate_installed_options(_Context(), kwds)


def test_installed_engine_factory_registration():
    from planemo.engine.factory import (
        build_engine,
        is_galaxy_engine,
    )
    from planemo.engine.galaxy import (
        InstalledGalaxyEngine,
        InstalledGalaxyEngineWithSingularityDB,
    )

    ctx = _Context()

    assert is_galaxy_engine(engine="installed_galaxy")
    assert isinstance(build_engine(ctx, engine="installed_galaxy"), InstalledGalaxyEngine)
    assert isinstance(
        build_engine(ctx, engine="installed_galaxy", database_type="postgres_singularity"),
        InstalledGalaxyEngineWithSingularityDB,
    )


def test_missing_gravity_executable_has_actionable_error(tmp_path):
    config_directory = tmp_path / "config"
    config_directory.mkdir()

    with installed_galaxy_config(
        create_test_context(),
        [],
        config_directory=str(config_directory),
        port=8765,
    ) as config:
        with (
            patch("planemo.galaxy.config.sys.executable", str(tmp_path / "bin" / "python")),
            pytest.raises(click.ClickException, match="Gravity's 'galaxy' command"),
        ):
            config.startup_command(_Context())
