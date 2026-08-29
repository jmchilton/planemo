"""Unit tests for the embedded Galaxy lifecycle."""

import contextlib
import logging
import os
import sys
import threading
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

import click
import pytest

from planemo.config import OptionSource
from planemo.galaxy import embedded


class _Context:
    verbose = False

    def __init__(self, option_sources=None):
        self.messages = []
        self.option_sources = option_sources or {}

    def get_option_source(self, name, default=None):
        return self.option_sources.get(name, default)

    def vlog(self, message, *args, **kwds):
        self.messages.append(message)

    def log(self, message, *args):
        self.messages.append(message)


class _WorkerContext:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        self.events.append("worker enter")

    def __exit__(self, exc_type, exc, traceback):
        self.events.append("worker exit")


class _ForkPool:
    def __init__(self, events):
        self.events = events

    def stop(self):
        self.events.append("pool stop")

    def join(self, timeout):
        self.events.append(("pool join", timeout))


def _lifecycle_fakes(tmp_path, events, *, is_job_handler=True):
    app = SimpleNamespace(
        is_job_handler=is_job_handler,
        application_stack=SimpleNamespace(name="Webless"),
    )
    app.shutdown = lambda: events.append("app shutdown")
    app_module = SimpleNamespace(app=None)
    celery_app = SimpleNamespace(fork_pool=_ForkPool(events))

    def build_galaxy_web_app(properties, global_conf, register_shutdown_at_exit):
        events.append(
            (
                "build",
                properties,
                global_conf,
                register_shutdown_at_exit,
                os.environ.get("GALAXY_CONFIG_FILE"),
            )
        )
        app_module.app = app
        return SimpleNamespace(galaxy_app=app, asgi_app=object())

    def start_worker(celery_application, **kwds):
        events.append(("worker config", celery_application, kwds))
        return _WorkerContext(events)

    dependencies = embedded._RuntimeDependencies(
        build_galaxy_web_app=build_galaxy_web_app,
        galaxy_app_module=app_module,
        celery_app=celery_app,
        start_worker=start_worker,
        worker_controller=None,
        uvicorn_config=None,
        uvicorn_server=None,
    )
    config_file = tmp_path / "galaxy.yml"
    config_file.write_text("galaxy: {}")
    log_file = tmp_path / "embedded.log"
    config = SimpleNamespace(
        env={"GALAXY_CONFIG_FILE": str(config_file)},
        galaxy_config_file=str(config_file),
        galaxy_properties={"server_name": "main"},
        galaxy_url="http://localhost:12345",
        log_file=str(log_file),
        log_contents="",
    )
    config.install_workflows = lambda: events.append("install workflows")

    @contextlib.contextmanager
    def config_context(ctx, runnables, **kwds):
        events.append(("config enter", kwds["port"], kwds["host"]))
        try:
            yield config
        finally:
            events.append("config exit")

    uvicorn_runtime = SimpleNamespace(errors=[])
    return dependencies, config_context, uvicorn_runtime, app_module, config_file


def test_embedded_lifecycle_orders_startup_and_cleanup(tmp_path):
    events = []
    dependencies, config_context, uvicorn_runtime, app_module, config_file = _lifecycle_fakes(tmp_path, events)
    ctx = _Context({"port": OptionSource.default})
    old_config_file = os.environ.get("GALAXY_CONFIG_FILE")

    def start_uvicorn(deps, asgi_app, sock):
        events.append("uvicorn start")
        return uvicorn_runtime

    def wait_until_ready(url, verbose, timeout):
        events.append(("ready", url, verbose, timeout, os.environ.get("GALAXY_CONFIG_FILE")))
        return True

    with (
        patch.object(embedded, "embedded_galaxy_config", config_context),
        patch.object(embedded, "_load_runtime_dependencies", return_value=dependencies),
        patch.object(embedded, "_start_uvicorn", side_effect=start_uvicorn),
        patch.object(embedded, "_stop_uvicorn", side_effect=lambda ctx, runtime: events.append("uvicorn stop")),
        patch.object(embedded, "sleep", side_effect=wait_until_ready),
    ):
        with embedded.serve_embedded(ctx, [], galaxy_startup_timeout=17, port=9090, host="localhost"):
            events.append("body")

    event_names = [event if isinstance(event, str) else event[0] for event in events]
    assert event_names == [
        "config enter",
        "build",
        "worker config",
        "worker enter",
        "uvicorn start",
        "ready",
        "install workflows",
        "body",
        "uvicorn stop",
        "worker exit",
        "pool stop",
        "pool join",
        "app shutdown",
        "config exit",
    ]
    assert events[0][1] != 9090
    assert events[0][2] == "127.0.0.1"
    build_event = events[1]
    assert build_event[1] == {"server_name": "main"}
    assert build_event[2] == {"__file__": str(config_file)}
    assert build_event[3] is False
    assert build_event[4] == str(config_file)
    worker_kwds = events[2][2]
    assert worker_kwds == {
        "pool": "solo",
        "concurrency": 1,
        "queues": ("galaxy.internal", "galaxy.external"),
        "perform_ping_check": False,
        "shutdown_timeout": 10,
    }
    assert app_module.app is None
    assert os.environ.get("GALAXY_CONFIG_FILE") == old_config_file


def test_readiness_failure_preserves_error_and_completes_cleanup(tmp_path):
    events = []
    dependencies, config_context, uvicorn_runtime, app_module, _ = _lifecycle_fakes(tmp_path, events)

    class FailingForkPool:
        def stop(self):
            events.append("pool stop")
            raise RuntimeError("pool stop failed")

        def join(self, timeout):
            events.append(("pool join", timeout))

    dependencies = replace(dependencies, celery_app=SimpleNamespace(fork_pool=FailingForkPool()))

    with (
        patch.object(embedded, "embedded_galaxy_config", config_context),
        patch.object(embedded, "_load_runtime_dependencies", return_value=dependencies),
        patch.object(embedded, "_start_uvicorn", return_value=uvicorn_runtime),
        patch.object(embedded, "_stop_uvicorn", side_effect=lambda ctx, runtime: events.append("uvicorn stop")),
        patch.object(embedded, "sleep", return_value=False),
        pytest.raises(RuntimeError, match="failed to start") as raised,
    ):
        with embedded.serve_embedded(_Context(), [], galaxy_startup_timeout=0):
            pytest.fail("unreachable")

    assert raised.value.__cause__ is None
    event_names = [event if isinstance(event, str) else event[0] for event in events]
    assert event_names[-6:] == [
        "uvicorn stop",
        "worker exit",
        "pool stop",
        "pool join",
        "app shutdown",
        "config exit",
    ]
    assert app_module.app is None


def test_uvicorn_startup_failure_is_retained_as_cause(tmp_path):
    events = []
    dependencies, config_context, uvicorn_runtime, app_module, _ = _lifecycle_fakes(tmp_path, events)
    server_error = RuntimeError("uvicorn thread crashed")
    uvicorn_runtime.errors.append(server_error)

    with (
        patch.object(embedded, "embedded_galaxy_config", config_context),
        patch.object(embedded, "_load_runtime_dependencies", return_value=dependencies),
        patch.object(embedded, "_start_uvicorn", return_value=uvicorn_runtime),
        patch.object(embedded, "_stop_uvicorn", side_effect=lambda ctx, runtime: events.append("uvicorn stop")),
        patch.object(embedded, "sleep", return_value=False),
        pytest.raises(RuntimeError, match="uvicorn server failed") as raised,
    ):
        with embedded.serve_embedded(_Context(), []):
            pytest.fail("unreachable")

    assert raised.value.__cause__ is server_error
    assert "app shutdown" in events
    assert events[-1] == "config exit"
    assert app_module.app is None


def test_first_interrupt_propagates_after_complete_cleanup(tmp_path):
    events = []
    dependencies, config_context, uvicorn_runtime, app_module, _ = _lifecycle_fakes(tmp_path, events)
    interrupt = KeyboardInterrupt("foreground interrupted")

    with (
        patch.object(embedded, "embedded_galaxy_config", config_context),
        patch.object(embedded, "_load_runtime_dependencies", return_value=dependencies),
        patch.object(embedded, "_start_uvicorn", return_value=uvicorn_runtime),
        patch.object(embedded, "_stop_uvicorn", side_effect=lambda ctx, runtime: events.append("uvicorn stop")),
        patch.object(embedded, "sleep", return_value=True),
        pytest.raises(KeyboardInterrupt) as raised,
    ):
        with embedded.serve_embedded(_Context(), []):
            raise interrupt

    assert raised.value is interrupt
    event_names = [event if isinstance(event, str) else event[0] for event in events]
    assert event_names[-6:] == [
        "uvicorn stop",
        "worker exit",
        "pool stop",
        "pool join",
        "app shutdown",
        "config exit",
    ]
    assert app_module.app is None


def test_second_interrupt_forces_uvicorn_exit():
    class InterruptingJoin:
        def __init__(self):
            self.join_timeouts = []
            self.alive = True

        def join(self, timeout):
            self.join_timeouts.append(timeout)
            if len(self.join_timeouts) == 1:
                raise KeyboardInterrupt()
            self.alive = False

        def is_alive(self):
            return self.alive

    server = SimpleNamespace(should_exit=False, force_exit=False)
    thread = InterruptingJoin()
    runtime = embedded._UvicornRuntime(server=server, thread=thread, errors=[])

    embedded._stop_uvicorn(_Context(), runtime)

    assert server.should_exit is True
    assert server.force_exit is True
    assert thread.join_timeouts == [
        embedded.UVICORN_SHUTDOWN_TIMEOUT,
        embedded.UVICORN_FORCE_EXIT_JOIN_TIMEOUT,
    ]


def test_application_validation_failure_still_shuts_down_app(tmp_path):
    events = []
    dependencies, config_context, _, app_module, _ = _lifecycle_fakes(
        tmp_path,
        events,
        is_job_handler=False,
    )
    ctx = _Context()

    with (
        patch.object(embedded, "embedded_galaxy_config", config_context),
        patch.object(embedded, "_load_runtime_dependencies", return_value=dependencies),
        pytest.raises(RuntimeError, match="not configured as a job handler"),
    ):
        with embedded.serve_embedded(ctx, []):
            pytest.fail("unreachable")

    assert "worker enter" not in events
    assert "app shutdown" in events
    assert app_module.app is None


def test_builder_failure_restores_the_previous_global_app(tmp_path):
    events = []
    dependencies, config_context, _, app_module, _ = _lifecycle_fakes(tmp_path, events)
    leaked_partial_app = object()

    def fail_during_build(*args, **kwds):
        app_module.app = leaked_partial_app
        raise RuntimeError("assembly failed")

    dependencies = embedded._RuntimeDependencies(
        build_galaxy_web_app=fail_during_build,
        galaxy_app_module=dependencies.galaxy_app_module,
        celery_app=dependencies.celery_app,
        start_worker=dependencies.start_worker,
        worker_controller=dependencies.worker_controller,
        uvicorn_config=dependencies.uvicorn_config,
        uvicorn_server=dependencies.uvicorn_server,
    )

    with (
        patch.object(embedded, "embedded_galaxy_config", config_context),
        patch.object(embedded, "_load_runtime_dependencies", return_value=dependencies),
        pytest.raises(RuntimeError, match="assembly failed"),
    ):
        with embedded.serve_embedded(_Context(), []):
            pytest.fail("unreachable")

    assert app_module.app is None


def test_partial_worker_entry_terminates_the_captured_controller():
    events = []

    class CapturableController:
        def __init__(self, *args, **kwds):
            events.append("controller created")

        def terminate(self):
            events.append("controller terminated")

    class FailingWorkerContext:
        def __init__(self, controller_class):
            self.controller_class = controller_class

        def __enter__(self):
            self.controller_class()
            raise RuntimeError("worker startup failed")

    def start_worker(celery_app, **kwds):
        return FailingWorkerContext(kwds["WorkController"])

    dependencies = SimpleNamespace(
        celery_app=object(),
        start_worker=start_worker,
        worker_controller=CapturableController,
    )

    with pytest.raises(RuntimeError, match="worker startup failed"):
        embedded._start_celery_worker(dependencies)

    assert events == ["controller created", "controller terminated"]


def test_worker_exit_failure_terminates_the_captured_controller():
    events = []

    class FailingWorkerContext:
        def __exit__(self, exc_type, exc, traceback):
            events.append("worker exit")
            raise RuntimeError("worker shutdown failed")

    class Controller:
        def terminate(self):
            events.append("controller terminated")

    runtime = embedded._CeleryWorkerRuntime(
        context=FailingWorkerContext(),
        controller=Controller(),
        entered=True,
    )

    with pytest.raises(RuntimeError, match="worker shutdown failed"):
        embedded._stop_celery_worker(runtime)

    assert events == ["worker exit", "controller terminated"]
    assert runtime.entered is False


def test_fork_pool_join_is_attempted_after_stop_failure():
    events = []

    class FailingForkPool:
        def stop(self):
            events.append("pool stop")
            raise RuntimeError("pool stop failed")

        def join(self, timeout):
            events.append(("pool join", timeout))

    with pytest.raises(RuntimeError, match="pool stop failed"):
        embedded._stop_fork_pool(SimpleNamespace(fork_pool=FailingForkPool()))

    assert events == ["pool stop", ("pool join", embedded.FORK_POOL_JOIN_TIMEOUT)]


def test_slow_cleanup_reports_live_runtime_resources():
    reported = threading.Event()

    class DiagnosticContext(_Context):
        def log(self, message, *args):
            super().log(message, *args)
            reported.set()

    ctx = DiagnosticContext()
    with embedded._cleanup_diagnostic_budget(ctx, timeout=0.01):
        assert reported.wait(timeout=1)

    assert len(ctx.messages) == 1
    message = ctx.messages[0]
    assert "cleanup exceeded 0.01 seconds" in message
    assert "Active threads:" in message
    assert "MainThread" in message
    assert "Active child processes:" in message
    assert not any(
        thread.name == "planemo-embedded-cleanup-diagnostics" and thread.is_alive() for thread in threading.enumerate()
    )


def test_cleanup_continues_if_diagnostic_thread_cannot_start(monkeypatch):
    events = []

    class FailingTimer:
        def __init__(self, *args, **kwds):
            pass

        def start(self):
            raise RuntimeError("thread allocation failed")

    monkeypatch.setattr(threading, "Timer", FailingTimer)
    ctx = _Context()

    with embedded._cleanup_diagnostic_budget(ctx):
        events.append("cleanup ran")

    assert events == ["cleanup ran"]
    assert ctx.messages == ["Failed to start embedded Galaxy cleanup diagnostics; continuing cleanup."]


@pytest.mark.parametrize(
    ("kwds", "message"),
    [
        ({"daemon": True}, "foreground"),
        ({"host": "0.0.0.0"}, "loopback"),
        ({"galaxy_root": "/checkout"}, "--galaxy_root"),
        ({"install_galaxy": True}, "--install_galaxy"),
    ],
)
def test_embedded_option_validation(kwds, message):
    with pytest.raises(click.UsageError, match=message):
        embedded.validate_embedded_options(_Context(), kwds)


def test_embedded_engine_factory_registration():
    from planemo.engine.factory import (
        build_engine,
        is_galaxy_engine,
    )
    from planemo.engine.galaxy import (
        EmbeddedGalaxyEngine,
        EmbeddedGalaxyEngineWithSingularityDB,
    )

    ctx = _Context()

    assert is_galaxy_engine(engine="embedded_galaxy")
    assert isinstance(build_engine(ctx, engine="embedded_galaxy"), EmbeddedGalaxyEngine)
    assert isinstance(
        build_engine(ctx, engine="embedded_galaxy", database_type="postgres_singularity"),
        EmbeddedGalaxyEngineWithSingularityDB,
    )


def test_missing_runtime_explains_the_unreleased_development_prerequisite():
    with (
        patch.dict(sys.modules, {"celery.contrib.testing.worker": None}),
        pytest.raises(click.ClickException, match="galaxyproject/galaxy#23360"),
    ):
        embedded._load_runtime_dependencies()


def test_embedded_test_reuses_one_application_for_inner_test_groups():
    from planemo.engine.galaxy import EmbeddedGalaxyEngine
    from planemo.engine.interface import BaseEngine

    events = []
    config = object()

    @contextlib.contextmanager
    def fake_serve(ctx, runnables, **kwds):
        events.append(("serve enter", runnables))
        try:
            yield config
        finally:
            events.append("serve exit")

    native = SimpleNamespace(uri="native")
    workflow = SimpleNamespace(uri="workflow")

    def fake_base_test(engine, runnables, test_timeout):
        with engine.ensure_runnables_served([native]) as first_config:
            events.append(("native", first_config))
        with engine.ensure_runnables_served([workflow]) as second_config:
            events.append(("workflow", second_config))
        return "results"

    engine = EmbeddedGalaxyEngine(_Context(), engine="embedded_galaxy")
    with (
        patch("planemo.engine.galaxy.serve_embedded", fake_serve),
        patch.object(BaseEngine, "test", fake_base_test),
    ):
        with patch.object(engine, "_check_can_run_all") as check_can_run_all:
            assert engine.test([native, workflow], test_timeout=30) == "results"

    assert events == [
        ("serve enter", [native, workflow]),
        ("native", config),
        ("workflow", config),
        "serve exit",
    ]
    check_can_run_all.assert_called()
    assert engine._active_embedded_config is None
    assert engine._active_embedded_runnable_uris == set()


def test_galaxy_test_results_remain_paired_with_mixed_case_types():
    from planemo.engine.galaxy import EmbeddedGalaxyEngine
    from planemo.engine.interface import BaseEngine
    from planemo.runnable import ExternalGalaxyToolTestCase

    config = object()
    native_runnable = SimpleNamespace(uri="native")
    native_case = ExternalGalaxyToolTestCase(native_runnable, "native", "1.0", 0, {})
    expanded_case_one = ExternalGalaxyToolTestCase(native_runnable, "native", "1.0", 0, {})
    expanded_case_two = ExternalGalaxyToolTestCase(native_runnable, "native", "1.0", 1, {})
    workflow_case = SimpleNamespace(runnable=SimpleNamespace(uri="workflow"))
    native_results = {
        expanded_case_one: {"id": "native-0", "status": "success"},
        expanded_case_two: {"id": "native-1", "status": "success"},
    }
    workflow_result = object()
    engine = EmbeddedGalaxyEngine(_Context(), engine="embedded_galaxy")
    engine._active_embedded_config = config
    engine._active_embedded_runnable_uris = {"native"}

    with (
        patch.object(BaseEngine, "_run_test_cases", return_value=[workflow_result]),
        patch(
            "planemo.engine.galaxy.expand_test_cases",
            return_value=[expanded_case_one, expanded_case_two],
        ),
        patch.object(
            engine,
            "_run_galaxy_tool_test_case",
            side_effect=lambda config, case, timeout, register: register(native_results[case]),
        ),
    ):
        results = engine._collect_test_results([native_case, workflow_case], test_timeout=30)

    assert results == [
        (expanded_case_one, native_results[expanded_case_one]),
        (expanded_case_two, native_results[expanded_case_two]),
        (workflow_case, workflow_result),
    ]


def test_embedded_test_rejects_unsupported_runnable_before_startup():
    from planemo.engine.galaxy import EmbeddedGalaxyEngine

    engine = EmbeddedGalaxyEngine(_Context(), engine="embedded_galaxy")
    with (
        patch.object(engine, "_check_can_run_all", side_effect=ValueError("unsupported")),
        patch("planemo.engine.galaxy.serve_embedded") as serve,
        pytest.raises(ValueError, match="unsupported"),
    ):
        engine.test([SimpleNamespace(uri="unsupported")], test_timeout=30)

    serve.assert_not_called()


def test_embedded_logging_is_scoped_and_keeps_details_in_file(tmp_path):
    ctx = _Context()
    galaxy_logger = logging.getLogger("galaxy")
    child_logger = logging.getLogger("galaxy.existing_child")
    child_handler = logging.NullHandler()
    child_logger.addHandler(child_handler)
    child_logger.setLevel(logging.WARNING)
    child_logger.propagate = False
    original_level = galaxy_logger.level
    original_propagate = galaxy_logger.propagate
    original_handlers = list(galaxy_logger.handlers)
    root_handlers = list(logging.getLogger().handlers)
    log_file = tmp_path / "embedded.log"

    with embedded._embedded_logging(ctx, str(log_file)):
        assert galaxy_logger.propagate is False
        assert not any(handler in galaxy_logger.handlers for handler in original_handlers)
        child_logger.info("file detail")
        galaxy_logger.warning("visible warning")
        try:
            raise RuntimeError("logged failure")
        except RuntimeError:
            galaxy_logger.exception("visible failure")

    log_contents = log_file.read_text()
    assert "file detail" in log_contents
    assert "visible warning" in log_contents
    assert "Traceback" in log_contents
    assert len(ctx.messages) == 2
    assert "visible warning" in ctx.messages[0]
    assert "visible failure" in ctx.messages[1]
    assert "Traceback" not in ctx.messages[1]
    assert galaxy_logger.level == original_level
    assert galaxy_logger.propagate is original_propagate
    assert galaxy_logger.handlers == original_handlers
    assert logging.getLogger().handlers == root_handlers
    assert child_logger.level == logging.WARNING
    assert child_logger.propagate is False
    assert child_logger.handlers == [child_handler]
    child_logger.removeHandler(child_handler)
