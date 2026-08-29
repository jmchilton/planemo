"""Lifecycle support for running wheel-installed Galaxy inside Planemo."""

import contextlib
import copy
import logging
import os
import socket
import threading
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Optional,
)

import click

from planemo.config import OptionSource
from planemo.galaxy.config import embedded_galaxy_config
from planemo.galaxy.ephemeris_sleep import sleep
from planemo.io import live_runtime_resources

INSTALL_MESSAGE = (
    "No compatible Galaxy release is available yet; install Galaxy packages built from "
    "galaxyproject/galaxy#23360 while developing this engine."
)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
WORKER_QUEUES = ("galaxy.internal", "galaxy.external")
CELERY_WORKER_SHUTDOWN_TIMEOUT = 10
UVICORN_SHUTDOWN_TIMEOUT = 10
UVICORN_FORCE_EXIT_JOIN_TIMEOUT = 1
FORK_POOL_JOIN_TIMEOUT = 5
CLEANUP_DIAGNOSTIC_TIMEOUT = 30
CLEANUP_DIAGNOSTIC_THREAD_JOIN_TIMEOUT = 1


@dataclass(frozen=True)
class _RuntimeDependencies:
    build_galaxy_web_app: Any
    galaxy_app_module: Any
    celery_app: Any
    celery_worker_state: Any
    start_worker: Any
    worker_controller: Any
    uvicorn_config: Any
    uvicorn_server: Any


@dataclass
class _UvicornRuntime:
    server: Any
    thread: threading.Thread
    errors: list[BaseException]


@dataclass
class _CeleryWorkerRuntime:
    context: Any
    worker_state: Any = None
    controller: Any = None
    entered: bool = False


class _ContextVerboseHandler(logging.Handler):
    """Send records through Planemo's Rich-aware verbose output path."""

    def __init__(self, ctx):
        super().__init__()
        self._ctx = ctx

    def emit(self, record):
        try:
            self._ctx.vlog(self.format(record))
        except Exception:
            self.handleError(record)


class _ContextWarningHandler(logging.Handler):
    """Keep warnings visible while routine embedded logs stay in the file."""

    def __init__(self, ctx):
        super().__init__(level=logging.WARNING)
        self._ctx = ctx

    def emit(self, record):
        try:
            concise_record = copy.copy(record)
            concise_record.exc_info = None
            concise_record.exc_text = None
            concise_record.stack_info = None
            self._ctx.log(self.format(concise_record))
        except Exception:
            self.handleError(record)


def _load_runtime_dependencies() -> _RuntimeDependencies:
    """Import the optional runtime only after embedded mode is selected."""
    try:
        from celery.contrib.testing.worker import (
            start_worker,
            TestWorkController,
        )
        from celery.worker import state as celery_worker_state
        from galaxy import app as galaxy_app_module
        from galaxy.celery import celery_app
        from galaxy.webapps.galaxy.fast_factory import build_galaxy_web_app
        from uvicorn import Config as UvicornConfig
        from uvicorn import Server as UvicornServer
    except ImportError as exc:
        raise click.ClickException(
            f"The embedded_galaxy engine requires Galaxy's application packages. {INSTALL_MESSAGE}"
        ) from exc

    return _RuntimeDependencies(
        build_galaxy_web_app=build_galaxy_web_app,
        galaxy_app_module=galaxy_app_module,
        celery_app=celery_app,
        celery_worker_state=celery_worker_state,
        start_worker=start_worker,
        worker_controller=TestWorkController,
        uvicorn_config=UvicornConfig,
        uvicorn_server=UvicornServer,
    )


def _option_source(ctx, name) -> Optional[OptionSource]:
    return ctx.get_option_source(name, None)


def _option_was_selected(ctx, kwds, name, neutral_value) -> bool:
    value = kwds.get(name, neutral_value)
    source = _option_source(ctx, name)
    if source is not None:
        return source != OptionSource.default and value != neutral_value
    return value != neutral_value


def validate_embedded_options(ctx, kwds):
    """Reject process and checkout options that have no embedded meaning."""
    if kwds.get("daemon"):
        raise click.UsageError("--engine embedded_galaxy only supports foreground operation; --daemon is unavailable.")

    host = kwds.get("host", "127.0.0.1")
    if host not in LOOPBACK_HOSTS:
        raise click.UsageError("--engine embedded_galaxy only binds to loopback; use --host 127.0.0.1.")

    checkout_options = {
        "galaxy_root": None,
        "cwl_galaxy_root": None,
        "galaxy_python_version": None,
        "install_galaxy": False,
        "skip_venv": False,
        "no_cache_galaxy": False,
        "galaxy_branch": "master",
        "galaxy_source": "https://github.com/galaxyproject/galaxy",
    }
    selected = [
        f"--{name}"
        for name, neutral_value in checkout_options.items()
        if _option_was_selected(ctx, kwds, name, neutral_value)
    ]
    if selected:
        options = ", ".join(selected)
        raise click.UsageError(
            f"--engine embedded_galaxy uses the installed Galaxy package; unsupported option(s): {options}."
        )


def _bind_socket(host, port) -> socket.socket:
    bind_host = "127.0.0.1" if host == "localhost" else host
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((bind_host, int(port or 0)))
    except BaseException:
        sock.close()
        raise
    return sock


@contextlib.contextmanager
def _patched_environment(values: Dict[str, str]):
    missing = object()
    previous = {key: os.environ.get(key, missing) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is missing:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


@contextlib.contextmanager
def _embedded_logging(ctx, log_file):
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    verbose_handler = _ContextVerboseHandler(ctx) if ctx.verbose else None
    warning_handler = None if ctx.verbose else _ContextWarningHandler(ctx)
    if verbose_handler:
        verbose_handler.setFormatter(formatter)
    if warning_handler:
        warning_handler.setFormatter(formatter)

    logger_names = ("galaxy", "celery", "uvicorn")
    root_loggers = [logging.getLogger(name) for name in logger_names]
    family_loggers = list(root_loggers)
    for candidate in logging.Logger.manager.loggerDict.values():
        if not isinstance(candidate, logging.Logger):
            continue
        if any(candidate.name.startswith(f"{name}.") for name in logger_names):
            family_loggers.append(candidate)
    family_loggers = list(dict.fromkeys(family_loggers))
    galaxy_app_logger = logging.getLogger("galaxy.app")
    app_guard_handler = logging.NullHandler()
    previous_levels = {logger: logger.level for logger in family_loggers}
    previous_propagation = {logger: logger.propagate for logger in family_loggers}
    previous_handlers = {logger: list(logger.handlers) for logger in family_loggers}
    try:
        # UniverseApplication calls basicConfig() when its own logger has no
        # direct handler. A no-op direct handler prevents it from replacing
        # Planemo's root logging configuration; records still propagate to the
        # file and optional verbose handlers on the ``galaxy`` parent.
        for logger in family_loggers:
            for handler in previous_handlers[logger]:
                logger.removeHandler(handler)
            if logger in root_loggers:
                logger.setLevel(logging.DEBUG if ctx.verbose else logging.INFO)
                logger.propagate = False
            else:
                logger.setLevel(logging.NOTSET)
                logger.propagate = True
        galaxy_app_logger.addHandler(app_guard_handler)
        for logger in root_loggers:
            logger.addHandler(file_handler)
            if verbose_handler:
                logger.addHandler(verbose_handler)
            if warning_handler:
                logger.addHandler(warning_handler)
        yield
    finally:
        galaxy_app_logger.removeHandler(app_guard_handler)
        for logger in root_loggers:
            if file_handler in logger.handlers:
                logger.removeHandler(file_handler)
            if verbose_handler and verbose_handler in logger.handlers:
                logger.removeHandler(verbose_handler)
            if warning_handler and warning_handler in logger.handlers:
                logger.removeHandler(warning_handler)
        for logger in family_loggers:
            logger.setLevel(previous_levels[logger])
            logger.propagate = previous_propagation[logger]
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
            for handler in previous_handlers[logger]:
                logger.addHandler(handler)
        file_handler.close()


def _start_uvicorn(dependencies, asgi_app, sock) -> _UvicornRuntime:
    host, port = sock.getsockname()[:2]
    uvicorn_config = dependencies.uvicorn_config(
        asgi_app,
        host=host,
        port=port,
        access_log=False,
        log_config=None,
        timeout_graceful_shutdown=UVICORN_SHUTDOWN_TIMEOUT,
    )
    server = dependencies.uvicorn_server(uvicorn_config)
    errors: list[BaseException] = []

    def run_server():
        try:
            server.run(sockets=[sock])
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=run_server, name="planemo-embedded-uvicorn", daemon=True)
    thread.start()
    return _UvicornRuntime(server=server, thread=thread, errors=errors)


def _stop_uvicorn(ctx, runtime: _UvicornRuntime):
    runtime.server.should_exit = True
    try:
        runtime.thread.join(timeout=UVICORN_SHUTDOWN_TIMEOUT)
    except KeyboardInterrupt:
        runtime.server.force_exit = True
        runtime.thread.join(timeout=UVICORN_FORCE_EXIT_JOIN_TIMEOUT)
    if runtime.thread.is_alive():
        ctx.vlog(f"Embedded Galaxy's uvicorn thread did not exit within " f"{UVICORN_SHUTDOWN_TIMEOUT:g} seconds.")


def _start_celery_worker(dependencies) -> _CeleryWorkerRuntime:
    """Start Celery while retaining a controller for partial-entry cleanup."""
    runtime = _CeleryWorkerRuntime(context=None, worker_state=dependencies.celery_worker_state)
    worker_kwds = {
        "pool": "solo",
        "concurrency": 1,
        "queues": WORKER_QUEUES,
        "perform_ping_check": False,
        "shutdown_timeout": CELERY_WORKER_SHUTDOWN_TIMEOUT,
    }
    if dependencies.worker_controller is not None:
        controller_class = dependencies.worker_controller

        class PlanemoWorkerController(controller_class):
            def __init__(self, *args, **kwds):
                super().__init__(*args, **kwds)
                runtime.controller = self

        worker_kwds["WorkController"] = PlanemoWorkerController

    runtime.context = dependencies.start_worker(dependencies.celery_app, **worker_kwds)
    try:
        runtime.context.__enter__()
        runtime.entered = True
    except BaseException:
        with contextlib.suppress(Exception):
            _terminate_celery_worker(runtime)
        raise
    return runtime


def _terminate_celery_worker(runtime: _CeleryWorkerRuntime):
    try:
        if runtime.controller is not None:
            runtime.controller.terminate()
    finally:
        # celery.contrib.testing.worker leaves this process-global flag set to
        # integer 0 when its shutdown join times out. Celery treats 0 as a
        # termination request by identity, poisoning the next in-process worker.
        if runtime.worker_state is not None:
            runtime.worker_state.should_terminate = None


def _stop_celery_worker(runtime: _CeleryWorkerRuntime):
    if runtime.entered:
        try:
            runtime.context.__exit__(None, None, None)
        except BaseException:
            with contextlib.suppress(Exception):
                _terminate_celery_worker(runtime)
            raise
        finally:
            runtime.entered = False
    elif runtime.controller is not None:
        _terminate_celery_worker(runtime)


def _stop_fork_pool(celery_app):
    fork_pool = getattr(celery_app, "fork_pool", None)
    if fork_pool is not None:
        fork_pool.stop()


def _join_fork_pool(celery_app):
    fork_pool = getattr(celery_app, "fork_pool", None)
    if fork_pool is not None:
        # Pebble currently ignores this timeout for a stopped ProcessPool and
        # performs unbounded internal joins. Keep passing the requested budget
        # in case that behavior is fixed, but rely on the slow-cleanup
        # diagnostic rather than claiming a hard bound here.
        fork_pool.join(timeout=FORK_POOL_JOIN_TIMEOUT)


def _cleanup(ctx, description, operation):
    try:
        operation()
    except KeyboardInterrupt:
        ctx.vlog(f"Interrupted while {description}; continuing embedded Galaxy cleanup.")
    except Exception as exc:
        ctx.vlog(f"Failed while {description}.", exception=exc)


def _enter_cleanup_context(cleanup_stack, ctx, description, manager):
    value = manager.__enter__()
    cleanup_stack.callback(_cleanup, ctx, description, lambda: manager.__exit__(None, None, None))
    return value


def _report_slow_cleanup(ctx, timeout):
    current_thread = threading.current_thread()
    thread_names, process_names = live_runtime_resources(exclude_threads=(current_thread,))
    active_threads = ", ".join(thread_names) or "none"
    active_processes = ", ".join(process_names) or "none"
    ctx.log(
        f"Embedded Galaxy cleanup exceeded {timeout:g} seconds. "
        f"Active threads: {active_threads}. Active child processes: {active_processes}."
    )


@contextlib.contextmanager
def _cleanup_diagnostic_budget(ctx, timeout=CLEANUP_DIAGNOSTIC_TIMEOUT):
    """Report live runtime resources if cooperative cleanup exceeds its budget."""
    timer = None
    timer_started = False
    try:
        timer = threading.Timer(timeout, _report_slow_cleanup, args=(ctx, timeout))
        timer.name = "planemo-embedded-cleanup-diagnostics"
        timer.daemon = True
        timer.start()
        timer_started = True
    except Exception as exc:
        with contextlib.suppress(Exception):
            ctx.vlog("Failed to start embedded Galaxy cleanup diagnostics; continuing cleanup.", exception=exc)
    try:
        yield
    finally:
        if timer_started:
            timer.cancel()
            with contextlib.suppress(KeyboardInterrupt):
                timer.join(timeout=CLEANUP_DIAGNOSTIC_THREAD_JOIN_TIMEOUT)


def _validate_application(dependencies, galaxy_app):
    if not galaxy_app.is_job_handler:
        raise RuntimeError("Embedded Galaxy was not configured as a job handler.")
    if getattr(galaxy_app.application_stack, "name", None) == "Gunicorn":
        raise RuntimeError("Embedded Galaxy cannot use the Gunicorn application stack.")
    if dependencies.galaxy_app_module.app is not galaxy_app:
        raise RuntimeError("Galaxy did not register the embedded application as its process-global app.")


@contextlib.contextmanager
def serve_embedded(ctx, runnables=None, **kwds):
    """Construct, serve, and completely tear down one embedded Galaxy app."""
    if runnables is None:
        runnables = []
    validate_embedded_options(ctx, kwds)

    host = kwds.get("host", "127.0.0.1")
    port = kwds.get("port")
    if _option_source(ctx, "port") == OptionSource.default:
        port = 0
    sock = _bind_socket(host, port)
    bound_host, bound_port = sock.getsockname()[:2]
    kwds["host"] = bound_host
    kwds["port"] = bound_port
    cleanup_stack = contextlib.ExitStack()
    cleanup_stack.callback(_cleanup, ctx, "closing the embedded Galaxy socket", sock.close)
    dependencies = None
    web_app = None
    worker_runtime = None
    uvicorn_runtime = None
    previous_global_app = None
    try:
        config = _enter_cleanup_context(
            cleanup_stack,
            ctx,
            "cleaning up the embedded Galaxy configuration",
            embedded_galaxy_config(ctx, runnables, **kwds),
        )
        _enter_cleanup_context(
            cleanup_stack,
            ctx,
            "restoring the embedded Galaxy environment",
            _patched_environment(config.env),
        )
        _enter_cleanup_context(
            cleanup_stack,
            ctx,
            "restoring embedded Galaxy logging",
            _embedded_logging(ctx, config.log_file),
        )
        dependencies = _load_runtime_dependencies()
        previous_global_app = dependencies.galaxy_app_module.app
        try:
            web_app = dependencies.build_galaxy_web_app(
                config.galaxy_properties,
                global_conf={"__file__": config.galaxy_config_file},
                register_shutdown_at_exit=False,
            )
        except BaseException:
            if dependencies.galaxy_app_module.app is not previous_global_app:
                dependencies.galaxy_app_module.app = previous_global_app
            raise
        galaxy_app = web_app.galaxy_app
        _validate_application(dependencies, galaxy_app)

        worker_runtime = _start_celery_worker(dependencies)

        uvicorn_runtime = _start_uvicorn(dependencies, web_app.asgi_app, sock)
        if not sleep(
            config.galaxy_url,
            verbose=ctx.verbose,
            timeout=kwds.get("galaxy_startup_timeout", 900),
        ):
            if uvicorn_runtime.errors:
                raise RuntimeError(
                    "Embedded Galaxy's uvicorn server failed during startup."
                ) from uvicorn_runtime.errors[0]
            raise RuntimeError(
                f"Attempted to serve embedded Galaxy at {config.galaxy_url}, but it failed to start."
                f"\nGalaxy log contents:\n{config.log_contents}"
            )
        config.install_workflows()
        yield config
    finally:
        with _cleanup_diagnostic_budget(ctx):
            if uvicorn_runtime is not None:
                _cleanup(ctx, "stopping uvicorn", lambda: _stop_uvicorn(ctx, uvicorn_runtime))
            if worker_runtime is not None:
                _cleanup(ctx, "stopping the Celery worker", lambda: _stop_celery_worker(worker_runtime))
            if dependencies is not None:
                _cleanup(
                    ctx,
                    "stopping Celery's fork pool",
                    lambda: _stop_fork_pool(dependencies.celery_app),
                )
                _cleanup(
                    ctx,
                    "joining Celery's fork pool",
                    lambda: _join_fork_pool(dependencies.celery_app),
                )
            if web_app is not None:
                galaxy_app = web_app.galaxy_app
                # Galaxy registers model-engine disposal as part of application
                # shutdown; do not dispose it twice here.
                _cleanup(ctx, "shutting down Galaxy", galaxy_app.shutdown)
                if dependencies.galaxy_app_module.app is galaxy_app:
                    dependencies.galaxy_app_module.app = previous_global_app
            cleanup_stack.close()


__all__ = (
    "serve_embedded",
    "validate_embedded_options",
)
