"""Unit tests for ``planemo.galaxy.config``."""

import contextlib
import json
import os
import shutil
import sys

import yaml

from planemo.galaxy.config import (
    _all_tool_paths,
    _shared_galaxy_properties,
    _shed_config_paths,
    embedded_galaxy_config,
    galaxy_config,
    get_refgenie_config,
    installed_galaxy_config,
    local_galaxy_config,
    SERVICE_LOG_TAIL_LINES,
    tail_log_directory,
    write_galaxy_config,
)
from planemo.runnable import (
    for_path,
    for_uri,
    Runnable,
    RunnableType,
)
from .test_utils import (
    create_test_context,
    skip_if_environ,
    TempDirectoryContext,
)


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
def test_defaults():
    """Test by default Galaxy files are stored in temp ``config_directory``."""
    with _test_galaxy_config() as config:
        config_directory = config.config_directory
        _assert_property_is(config, "file_path", os.path.join(config_directory, "files"))
        conn = "sqlite:///%s/galaxy.sqlite?isolation_level=IMMEDIATE" % config_directory
        _assert_property_is(config, "database_connection", conn)


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
def test_database_connection_override_path():
    """Test by default Galaxy files are stored in temp ``config_directory``."""
    conn = "postgresql://username:password@localhost/mydatabase"
    with _test_galaxy_config(database_connection=conn) as config:
        _assert_property_is(config, "database_connection", conn)


@skip_if_environ("PLANEMO_SKIP_GALAXY_TESTS")
def test_override_files_path():
    """Test Galaxy file path overrideable with --file_path."""
    with TempDirectoryContext() as tdc:
        with _test_galaxy_config(file_path=tdc.temp_directory) as config:
            _assert_property_is(config, "file_path", tdc.temp_directory)


def test_refgenie_config_version():
    with TempDirectoryContext() as tdc:
        galaxy_lib_path = os.path.join(tdc.temp_directory, "lib", "galaxy")
        os.makedirs(galaxy_lib_path)
        if os.path.isdir(os.path.join(galaxy_lib_path, "version")):
            version_path = os.path.join(galaxy_lib_path, "version", "__init__.py")
        else:
            version_path = os.path.join(galaxy_lib_path, "version.py")
        with open(version_path, "w") as version_fh:
            version_fh.write('VERSION_MAJOR = "21.05"')
        refgenie_config = get_refgenie_config(galaxy_root=tdc.temp_directory, refgenie_dir="/")
    assert yaml.load(refgenie_config, Loader=yaml.SafeLoader)["config_version"] == 0.3


def test_all_tool_paths_excludes_remote_galaxy_tools():
    local_tool = os.path.join(os.path.dirname(__file__), "data", "tools", "two_tests.xml")
    remote_tool_id = (
        "toolshed.g2.bx.psu.edu/repos/iuc/collection_element_identifiers/collection_element_identifiers/0.0.3"
    )

    tool_paths = _all_tool_paths([for_path(local_tool), for_uri(f"gxid://tools/{remote_tool_id}")])

    assert local_tool in tool_paths
    assert f"gxid://tools/{remote_tool_id}" not in tool_paths


def test_all_tool_paths_excludes_workflows():
    # A workflow's own .ga path must never be handed to Galaxy as a tool - Galaxy
    # would try to XML-parse the JSON workflow and fail. See has_tools below.
    workflow = os.path.join(os.path.dirname(__file__), "data", "wf1.ga")
    runnable = for_path(workflow)

    assert runnable.has_tools is False
    assert workflow not in _all_tool_paths([runnable])


def test_runnable_delegated_properties_are_booleans():
    # has_tools / is_single_artifact must delegate to the RunnableType and return
    # real booleans (previously they returned an always-truthy property object).
    for runnable_type in RunnableType:
        runnable = Runnable("some_path", runnable_type)
        assert isinstance(runnable.has_tools, bool)
        assert isinstance(runnable.is_single_artifact, bool)
        assert runnable.has_tools == runnable_type.has_tools
        assert runnable.is_single_artifact == runnable_type.is_single_artifact

    assert Runnable("t.xml", RunnableType.galaxy_tool).has_tools is True
    assert Runnable("w.ga", RunnableType.galaxy_workflow).has_tools is False
    assert Runnable("d", RunnableType.directory).is_single_artifact is False


def _assert_property_is(config, prop, value):
    env_var = "GALAXY_CONFIG_OVERRIDE_%s" % prop.upper()
    assert config.env[env_var] == value


def test_gxits_enabled_by_default():
    """Test that Galaxy Interactive Tools are enabled by default in galaxy.yml."""
    with _test_write_galaxy_config() as (config_data, properties, env):
        gravity = config_data["gravity"]
        gx_it_proxy = gravity["gx_it_proxy"]
        assert gx_it_proxy["enable"] is True
        assert "port" in gx_it_proxy
        assert isinstance(gx_it_proxy["port"], int)
        assert "sessions" in gx_it_proxy
        assert gx_it_proxy["sessions"].endswith("interactivetools_map.sqlite")


def test_gxits_sets_galaxy_properties():
    """Test that enabling GxITs sets the required Galaxy properties."""
    with _test_write_galaxy_config() as (config_data, properties, env):
        assert properties["interactivetools_enable"] is True
        assert properties["interactivetools_upstream_proxy"] is False
        assert "galaxy_infrastructure_url" in properties
        assert "interactivetools_proxy_host" in properties
        assert "interactivetools_map" in properties
        assert properties["interactivetools_map"].endswith("interactivetools_map.sqlite")
        # The proxy host should include the gx_it_proxy port
        gx_it_port = config_data["gravity"]["gx_it_proxy"]["port"]
        assert properties["interactivetools_proxy_host"] == f"localhost:{gx_it_port}"
        # sessions and interactivetools_map should point to the same file
        assert config_data["gravity"]["gx_it_proxy"]["sessions"] == properties["interactivetools_map"]


def test_gxits_disabled_with_flag():
    """Test that --disable_gxits flag properly disables interactive tools."""
    with _test_write_galaxy_config(disable_gxits=True) as (config_data, properties, env):
        gravity = config_data["gravity"]
        gx_it_proxy = gravity["gx_it_proxy"]
        assert gx_it_proxy["enable"] is False
        assert "port" not in gx_it_proxy
        # Galaxy properties for interactive tools should not be set
        assert "interactivetools_enable" not in properties
        assert "interactivetools_upstream_proxy" not in properties
        assert "interactivetools_proxy_host" not in properties
        assert "interactivetools_map" not in properties


def test_gxits_infrastructure_url_uses_host_and_port():
    """Test that the galaxy_infrastructure_url uses the configured host and port."""
    with _test_write_galaxy_config(host="0.0.0.0", port=9999) as (config_data, properties, env):
        assert properties["galaxy_infrastructure_url"] == "http://0.0.0.0:9999"
        assert properties["interactivetools_proxy_host"].startswith("0.0.0.0:")


def test_gxits_infrastructure_url_remaps_127_0_0_1_to_localhost():
    """Test that 127.0.0.1 is remapped to localhost for infrastructure URLs."""
    with _test_write_galaxy_config(host="127.0.0.1", port=9090) as (config_data, properties, env):
        assert properties["galaxy_infrastructure_url"] == "http://localhost:9090"
        assert properties["interactivetools_proxy_host"].startswith("localhost:")


def test_tool_evaluation_strategy_remote_sets_metadata_strategy():
    """Test that --tool_evaluation_strategy remote also sets metadata_strategy to extended."""
    with TempDirectoryContext() as tdc:
        props = _shared_galaxy_properties(tdc.temp_directory, {"tool_evaluation_strategy": "remote"}, for_tests=False)
    assert props["tool_evaluation_strategy"] == "remote"
    assert props["metadata_strategy"] == "extended"


def test_tool_evaluation_strategy_default_not_set():
    """Test that tool_evaluation_strategy is not set when not specified."""
    with TempDirectoryContext() as tdc:
        props = _shared_galaxy_properties(tdc.temp_directory, {}, for_tests=False)
    assert "tool_evaluation_strategy" not in props


def test_embedded_galaxy_config_is_checkout_independent(tmp_path):
    config_directory = tmp_path / "config"
    config_directory.mkdir()
    test_data = tmp_path / "test-data"
    test_data.mkdir()
    tool_path = os.path.join(os.path.dirname(__file__), "data", "tools", "two_tests.xml")
    dependency_dir = tmp_path / "custom-dependencies"
    ctx = create_test_context()

    with embedded_galaxy_config(
        ctx,
        [for_path(tool_path)],
        config_directory=str(config_directory),
        test_data=str(test_data),
        tool_dependency_dir=str(dependency_dir),
        host="127.0.0.1",
    ) as config:
        with open(config.galaxy_config_file) as config_fh:
            config_data = yaml.safe_load(config_fh)
        file_properties = config_data["galaxy"]
        properties = config.galaxy_properties

        assert "gravity" not in config_data
        assert properties["auto_configure_logging"] is False
        assert properties["configure_logging"] is False
        assert "configure_logging" not in file_properties
        assert properties["enable_celery_tasks"] is True
        assert properties["interactivetools_enable"] is False
        assert properties["monitor_thread_join_timeout"] == 5
        assert "use_display_applications" not in properties
        assert properties["watch_tools"] is False
        assert properties["tool_data_table_config_path"].endswith("empty_tool_data_table_conf.xml")
        assert properties["amqp_internal_connection"] == (f"sqlalchemy+sqlite:///{config_directory / 'control.sqlite'}")
        assert properties["celery_conf"] == {
            "broker_url": "memory://",
            "result_backend": "rpc://localhost",
            "worker_hijack_root_logger": False,
        }
        assert properties["bootstrap_admin_api_key"] == config.master_api_key
        assert "master_api_key" not in properties
        assert all(value is not None for value in properties.values())
        assert properties["tool_dependency_dir"] == str(dependency_dir)
        assert dependency_dir.is_dir()
        assert "tour_config_dir" not in properties
        assert config.galaxy_url.startswith("http://127.0.0.1:")
        assert config.env["GALAXY_CONFIG_FILE"] == config.galaxy_config_file
        assert "GALAXY_DEVELOPMENT_ENVIRONMENT" not in config.env

        with open(properties["job_config_file"]) as job_config_fh:
            job_config = yaml.safe_load(job_config_fh)
        assert "handling" not in job_config


def test_installed_galaxy_config_uses_gravity_and_cross_process_celery(tmp_path):
    config_directory = tmp_path / "config"
    config_directory.mkdir()

    with installed_galaxy_config(
        create_test_context(),
        [],
        config_directory=str(config_directory),
        host="127.0.0.1",
        port=8765,
    ) as config:
        with open(config.galaxy_config_file) as config_fh:
            config_data = yaml.safe_load(config_fh)

        properties = config_data["galaxy"]
        gravity = config_data["gravity"]
        assert properties["bootstrap_admin_api_key"] == config.master_api_key
        assert "master_api_key" not in properties
        assert properties["data_dir"] == str(config_directory / "data")
        assert properties["amqp_internal_connection"] == (
            f"sqlalchemy+sqlite:///{config_directory / 'celery_broker.sqlite'}"
        )
        assert properties["enable_celery_tasks"] is True
        assert properties["interactivetools_enable"] is False
        assert properties["watch_tools"] is False
        assert properties["celery_conf"] == {
            "result_backend": f"db+sqlite:///{config_directory / 'celery_results.sqlite'}",
            "worker_hijack_root_logger": False,
        }
        assert gravity["process_manager"] == "multiprocessing"
        assert gravity["service_command_style"] == "direct"
        assert gravity["virtualenv"] == sys.prefix
        assert gravity["gunicorn"] == {
            "bind": "127.0.0.1:8765",
            "preload": False,
            "workers": 1,
        }
        assert gravity["celery"] == {
            "enable": True,
            "enable_beat": False,
            "concurrency": 1,
            "pool": "solo",
            "queues": "galaxy.internal,galaxy.external",
        }
        assert gravity["gx_it_proxy"] == {"enable": False}
        assert "galaxy_root" not in gravity
        assert config.env == {
            "GALAXY_CONFIG_FILE": str(config_directory / "galaxy.yml"),
            "GRAVITY_STATE_DIR": str(config_directory / "gravity"),
        }
        assert config.galaxy_root is None
        assert config.galaxy_url == "http://127.0.0.1:8765"


def test_installed_galaxy_startup_uses_gravity_from_planemo_environment(tmp_path, monkeypatch):
    config_directory = tmp_path / "config"
    config_directory.mkdir()
    bin_directory = tmp_path / "bin"
    bin_directory.mkdir()
    python = bin_directory / "python"
    galaxy = bin_directory / "galaxy"
    python.touch()
    galaxy.touch()
    monkeypatch.setattr("planemo.galaxy.config.sys.executable", str(python))

    with installed_galaxy_config(
        create_test_context(),
        [],
        config_directory=str(config_directory),
        port=8765,
    ) as config:
        command = config.startup_command(create_test_context())

    assert command == (
        f"{galaxy} --config-file {config_directory / 'galaxy.yml'} " f"--state-dir {config_directory / 'gravity'}"
    )


def test_embedded_test_configuration_uses_explicit_empty_plugin_directories(tmp_path):
    config_directory = tmp_path / "config"
    config_directory.mkdir()
    ctx = create_test_context()

    with embedded_galaxy_config(
        ctx,
        [],
        for_tests=True,
        config_directory=str(config_directory),
    ) as config:
        properties = config.galaxy_properties

        assert properties["tour_config_dir"] == str(config_directory / "empty")
        assert properties["visualization_plugins_directory"] == str(config_directory / "empty")
        assert properties["interactive_environment_plugins_directory"] == str(config_directory / "empty")


def test_embedded_no_cleanup_preserves_config_and_bounded_log_tail():
    ctx = create_test_context()
    config = None
    config_directory = None
    lines = [f"embedded log line {index}" for index in range(SERVICE_LOG_TAIL_LINES + 5)]

    try:
        with embedded_galaxy_config(ctx, [], no_cleanup=True) as config:
            config_directory = config.config_directory
            with open(config.log_file, "w") as log_fh:
                log_fh.write("\n".join(lines) + "\n")

            service_logs = config.service_log_contents
            assert list(service_logs) == ["embedded.log"]
            assert service_logs["embedded.log"].splitlines() == lines[-SERVICE_LOG_TAIL_LINES:]

        assert os.path.isdir(config_directory)
        assert config.log_contents.splitlines() == lines
    finally:
        if config_directory:
            shutil.rmtree(config_directory, ignore_errors=True)


def test_embedded_config_removes_its_generated_directory():
    ctx = create_test_context()
    config_directory = None

    with embedded_galaxy_config(ctx, []) as config:
        config_directory = config.config_directory
        assert os.path.isdir(config_directory)

    assert config_directory is not None
    assert not os.path.exists(config_directory)


def test_shared_config_refactor_preserves_checkout_runtime(tmp_path):
    galaxy_root = tmp_path / "galaxy"
    galaxy_package = galaxy_root / "lib" / "galaxy"
    galaxy_package.mkdir(parents=True)
    (galaxy_package / "version.py").write_text('VERSION = "25.0.1"')
    config_directory = tmp_path / "config"
    config_directory.mkdir()
    test_data = tmp_path / "test-data"
    test_data.mkdir()
    dependency_dir = tmp_path / "checkout-dependencies"
    ctx = create_test_context()

    with local_galaxy_config(
        ctx,
        [],
        galaxy_root=str(galaxy_root),
        config_directory=str(config_directory),
        test_data=str(test_data),
        tool_dependency_dir=str(dependency_dir),
        disable_gxits=True,
    ) as config:
        with open(config.env["GALAXY_CONFIG_FILE"]) as config_fh:
            config_data = yaml.safe_load(config_fh)

        assert config_data["gravity"]["galaxy_root"] == str(galaxy_root)
        assert config_data["gravity"]["gx_it_proxy"] == {"enable": False}
        assert config.env["GALAXY_DEVELOPMENT_ENVIRONMENT"] == "1"
        assert config.env["GALAXY_CONFIG_OVERRIDE_TOOL_DEPENDENCY_DIR"] == str(dependency_dir)
        assert dependency_dir.is_dir()
        with open(config.env["GALAXY_CONFIG_OVERRIDE_JOB_CONFIG_FILE"]) as job_config_fh:
            assert "handling" not in yaml.safe_load(job_config_fh)


@contextlib.contextmanager
def _test_galaxy_config(tool_paths=[], **kwargs):
    ctx = create_test_context()
    with TempDirectoryContext() as tdc:
        test_data = os.path.join(tdc.temp_directory, "test-data")
        os.makedirs(test_data)
        kwargs["test_data"] = test_data
        with galaxy_config(ctx, tool_paths, **kwargs) as gc:
            yield gc


@contextlib.contextmanager
def _test_write_galaxy_config(**kwds):
    """Helper to test write_galaxy_config directly with a fake galaxy root."""
    with TempDirectoryContext() as tdc:
        galaxy_root = tdc.temp_directory
        # Create fake galaxy version file (>= 22.01 to use YAML config)
        galaxy_lib_path = os.path.join(galaxy_root, "lib", "galaxy")
        os.makedirs(galaxy_lib_path)
        version_path = os.path.join(galaxy_lib_path, "version.py")
        with open(version_path, "w") as version_fh:
            version_fh.write('VERSION_MAJOR = "24.1"')

        config_dir = os.path.join(galaxy_root, "config")
        os.makedirs(config_dir)

        def config_join(*args):
            return os.path.join(config_dir, *args)

        host = kwds.pop("host", "localhost")
        port = kwds.pop("port", 9090)
        properties = {}
        env = {}
        template_args = {"port": port}
        config_kwds = {"host": host}
        config_kwds.update(kwds)

        write_galaxy_config(
            galaxy_root=galaxy_root,
            properties=properties,
            env=env,
            kwds=config_kwds,
            template_args=template_args,
            config_join=config_join,
        )

        config_file = env["GALAXY_CONFIG_FILE"]
        with open(config_file) as f:
            config_data = json.load(f)

        yield config_data, properties, env


def _config_join(*args):
    return os.path.join("/ephemeral", *args)


def test_shed_config_paths_default_ephemeral():
    """Without --shed_data_dir the paths fall back to the config directory."""
    paths = _shed_config_paths({}, _config_join)
    assert paths["shed_tool_conf"] == "/ephemeral/shed_tools_conf.xml"
    assert paths["shed_tool_path"] == "/ephemeral/shed_tools"
    assert paths["shed_tool_data_table_config"] == "/ephemeral/shed_tool_data_table_conf.xml"
    assert paths["shed_data_manager_config_file"] == "/ephemeral/shed_data_manager_conf.xml"


def test_shed_config_paths_seeded_by_shed_data_dir():
    """--shed_data_dir seeds all four shed-install config paths."""
    paths = _shed_config_paths({"shed_data_dir": "/persist"}, _config_join)
    assert paths["shed_tool_conf"] == "/persist/shed_tools_conf.xml"
    assert paths["shed_tool_path"] == "/persist/shed_tools"
    assert paths["shed_tool_data_table_config"] == "/persist/shed_tool_data_table_conf.xml"
    assert paths["shed_data_manager_config_file"] == "/persist/shed_data_manager_conf.xml"


def test_shed_config_paths_individual_override_wins():
    """An explicit per-file option overrides the --shed_data_dir default."""
    kwds = {
        "shed_data_dir": "/persist",
        "shed_tool_conf": "/custom/conf.xml",
        "shed_data_manager_config": "/custom/dm.xml",
    }
    paths = _shed_config_paths(kwds, _config_join)
    assert paths["shed_tool_conf"] == "/custom/conf.xml"
    assert paths["shed_data_manager_config_file"] == "/custom/dm.xml"
    # untouched ones still derive from --shed_data_dir
    assert paths["shed_tool_path"] == "/persist/shed_tools"
    assert paths["shed_tool_data_table_config"] == "/persist/shed_tool_data_table_conf.xml"


def test_tail_log_directory_missing_directory():
    """A Galaxy that never started leaves no log directory at all."""
    with TempDirectoryContext() as tdc:
        assert tail_log_directory(os.path.join(tdc.temp_directory, "nope")) == {}


def test_tail_log_directory_reads_only_logs():
    with TempDirectoryContext() as tdc:
        log_directory = tdc.temp_directory
        with open(os.path.join(log_directory, "celery.log"), "w") as f:
            f.write("task failed\n")
        with open(os.path.join(log_directory, "celery_broker.sqlite"), "w") as f:
            f.write("not a log\n")
        os.mkdir(os.path.join(log_directory, "subdir.log"))
        assert tail_log_directory(log_directory) == {"celery.log": "task failed"}


def test_tail_log_directory_truncates_to_tail():
    with TempDirectoryContext() as tdc:
        log_directory = tdc.temp_directory
        with open(os.path.join(log_directory, "celery.log"), "w") as f:
            f.writelines(f"line {i}\n" for i in range(10))
        tails = tail_log_directory(log_directory, lines=3)
        assert tails["celery.log"] == "line 7\nline 8\nline 9"


def test_tail_log_directory_skips_empty_logs():
    with TempDirectoryContext() as tdc:
        log_directory = tdc.temp_directory
        open(os.path.join(log_directory, "gunicorn.log"), "w").close()
        assert tail_log_directory(log_directory) == {}
