"""Unit tests for ``planemo workflow_test_on_invocation``."""

import contextlib
from types import SimpleNamespace
from unittest.mock import (
    MagicMock,
    patch,
)

from planemo.commands.cmd_workflow_test_on_invocation import cli
from .test_utils import create_test_context


def test_workflow_test_on_invocation_forwards_test_timeout():
    assert "test_timeout" in {parameter.name for parameter in cli.params}

    ctx = create_test_context()
    ctx.exit = MagicMock()
    user_gi = MagicMock()
    invocation = {"workflow_id": "workflowid123"}
    user_gi.invocations.show_invocation.return_value = invocation
    config = SimpleNamespace(user_gi=user_gi)
    engine = MagicMock()
    engine.ensure_runnables_served.return_value = contextlib.nullcontext(config)
    test_case = MagicMock()
    test_case.structured_test_data.return_value = {
        "id": "workflow-0",
        "has_data": True,
        "data": {"status": "success"},
    }

    with (
        patch(
            "planemo.commands.cmd_workflow_test_on_invocation.engine_context",
            return_value=contextlib.nullcontext(engine),
        ),
        patch(
            "planemo.commands.cmd_workflow_test_on_invocation.for_runnable_identifier",
            return_value=object(),
        ),
        patch(
            "planemo.commands.cmd_workflow_test_on_invocation.definition_to_test_case",
            return_value=[test_case],
        ),
        patch(
            "planemo.commands.cmd_workflow_test_on_invocation.invocation_to_run_response",
            return_value=object(),
        ) as invocation_to_run_response,
        patch(
            "planemo.commands.cmd_workflow_test_on_invocation.handle_reports_and_summary",
            return_value=0,
        ),
    ):
        cli.callback.__wrapped__(
            ctx,
            "workflow-tests.yml",
            "invocationid123",
            1,
            test_timeout=31,
        )

    assert invocation_to_run_response.call_args.kwargs["timeout"] == 31
