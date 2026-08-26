"""Unit tests for :mod:`planemo.galaxy.activity`."""

import os
from unittest import mock

import pytest

from planemo.galaxy.activity import (
    _execute,
    PlanemoStagingInterface,
    wait_for_invocation_and_jobs,
)
from planemo.runnable import (
    Runnable,
    RunnableType,
)
from .test_utils import (
    create_test_context,
    PROJECT_TEMPLATES_DIR,
    TEST_DATA_DIR,
)

TOOL_RUNNABLE = Runnable(os.path.join(PROJECT_TEMPLATES_DIR, "demo", "cat.xml"), RunnableType.galaxy_tool)
WORKFLOW_RUNNABLE = Runnable(os.path.join(TEST_DATA_DIR, "wf2.ga"), RunnableType.galaxy_workflow)


class ExecutionHalted(Exception):
    """Raised to stop ``_execute`` once the request of interest was captured."""


def _execute_capturing_request(runnable, **kwds):
    """Run ``_execute`` far enough to capture the request it makes of Galaxy."""
    config = mock.MagicMock()
    config.user_gi.tools._post.side_effect = ExecutionHalted()
    config.user_gi.workflows.invoke_workflow.side_effect = ExecutionHalted()
    with mock.patch("planemo.galaxy.activity.stage_in", return_value=({}, "historyid123")):
        with pytest.raises(ExecutionHalted):
            _execute(create_test_context(), config, runnable, job_path=None, **kwds)
    if runnable.type == RunnableType.galaxy_tool:
        return config.user_gi.tools._post.call_args.args[0]
    else:
        return config.user_gi.workflows.invoke_workflow.call_args.kwargs


@pytest.mark.parametrize("use_cache", [True, False])
def test_execute_tool_forwards_use_cache(use_cache):
    payload = _execute_capturing_request(TOOL_RUNNABLE, use_cache=use_cache)
    assert payload["use_cached_job"] is use_cache


@pytest.mark.parametrize("use_cache", [True, False])
def test_execute_workflow_forwards_use_cache(use_cache):
    invoke_kwds = _execute_capturing_request(WORKFLOW_RUNNABLE, use_cache=use_cache)
    assert invoke_kwds["use_cached_job"] is use_cache


def test_execute_does_not_cache_without_use_cache():
    """Callers other than ``planemo run`` (e.g. ``planemo test``) never set use_cache."""
    assert _execute_capturing_request(TOOL_RUNNABLE)["use_cached_job"] is False
    assert _execute_capturing_request(WORKFLOW_RUNNABLE)["use_cached_job"] is False


def test_execute_forwards_test_timeout_to_workflow_polling():
    config = mock.MagicMock()
    config.user_gi.workflows.invoke_workflow.return_value = {
        "id": "invocationid123",
        "history_id": "historyid123",
        "workflow_id": "workflowid123",
    }
    with (
        mock.patch("planemo.galaxy.activity.time.monotonic", return_value=100),
        mock.patch("planemo.galaxy.activity.stage_in", return_value=({}, "historyid123")),
        mock.patch("planemo.galaxy.activity.invocation_to_run_response", side_effect=ExecutionHalted()) as convert,
        pytest.raises(ExecutionHalted),
    ):
        _execute(create_test_context(), config, WORKFLOW_RUNNABLE, job_path=None, test_timeout=17)

    assert convert.call_args.kwargs["timeout"] == 17
    assert convert.call_args.kwargs["deadline"] == 117


def test_upload_wait_uses_shared_test_deadline():
    staging = PlanemoStagingInterface(
        create_test_context(),
        WORKFLOW_RUNNABLE,
        mock.MagicMock(),
        "26.1",
        simultaneous_uploads=True,
        deadline=119,
    )
    staging._upload_jobs = [{"id": "uploadid123"}]

    with mock.patch("planemo.galaxy.activity._wait_for_job") as wait_for_job:
        staging.wait_for_uploads(check_ok=False)

    wait_for_job.assert_called_once_with(staging._user_gi, "uploadid123", deadline=119)


def test_workflow_wait_uses_test_timeout():
    user_gi = mock.MagicMock()
    user_gi.base_url = "http://127.0.0.1:8080"
    with (
        mock.patch("planemo.galaxy.activity.PollingTrackerImpl") as polling_tracker,
        mock.patch("planemo.galaxy.activity.WorkflowProgressDisplay"),
        mock.patch(
            "planemo.galaxy.activity.polling_wait_for_invocation_and_jobs",
            return_value=("scheduled", "ok", None),
        ),
    ):
        wait_for_invocation_and_jobs(
            create_test_context(),
            "invocationid123",
            "historyid123",
            user_gi,
            polling_backoff=2,
            timeout=23,
        )

    polling_tracker.assert_called_once_with(2, timeout=23, deadline=None)


def test_base_engine_forwards_explicit_test_timeout_to_run():
    from planemo.engine.interface import BaseEngine

    case = mock.MagicMock()
    case.job_path = "job.json"
    engine = mock.MagicMock()
    run_response = object()
    engine._run.return_value = [run_response]

    results = BaseEngine._run_test_cases(engine, [case], test_timeout=29)

    assert results == [run_response]
    engine._run.assert_called_once_with(
        [case.runnable],
        ["job.json"],
        mock.ANY,
        test_timeout=29,
    )
