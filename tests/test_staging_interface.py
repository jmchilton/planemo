"""Tests for upload behavior of :class:`PlanemoStagingInterface`.

These cover the part of staging that used to be decided by whether stdout
happened to be a terminal: whether ``--no_simultaneous_uploads`` is honored
and whether uploads are waited on through the progress display.
"""

import sys
from io import StringIO
from typing import (
    Any,
    Dict,
    List,
)

from rich.console import Console

from planemo.galaxy import activity
from planemo.galaxy.activity import PlanemoStagingInterface
from planemo.galaxy.upload_progress import UploadProgressDisplay
from planemo.runnable import RunnableType


def _console() -> Console:
    """A console that is never a terminal, so no live rendering happens."""
    return Console(file=StringIO(), force_terminal=False)


class FakeJobsClient:
    """Bioblend-ish jobs client returning a scripted sequence of states."""

    def __init__(self, states: Dict[str, List[str]]):
        self._states = {job_id: list(job_states) for job_id, job_states in states.items()}
        self.calls: List[Any] = []

    def show_job(self, job_id: str, full_details: bool = False) -> Dict[str, Any]:
        self.calls.append((job_id, full_details))
        states = self._states[job_id]
        # hold on the final state once the script is exhausted
        state = states.pop(0) if len(states) > 1 else states[0]
        return {
            "id": job_id,
            "state": state,
            "history_id": "hist123",
            "outputs": {},
            "output_collections": {},
            "stderr": "",
            "stdout": "",
            "tool_id": "upload1",
            "exit_code": 0,
        }


class FakeGalaxyInstance:
    def __init__(self, states: Dict[str, List[str]]):
        self.jobs = FakeJobsClient(states)
        self.base_url = "http://localhost:8080"


def _staging_interface(gi, simultaneous_uploads: bool, display: UploadProgressDisplay) -> PlanemoStagingInterface:
    return PlanemoStagingInterface(
        ctx=None,
        runnable=None,
        user_gi=gi,
        version_major="24.1",
        simultaneous_uploads=simultaneous_uploads,
        upload_progress_display=display,
    )


def test_sequential_uploads_wait_even_with_a_progress_display():
    """``--no_simultaneous_uploads`` is the documented default and must be honored.

    Before, the per-upload wait was skipped whenever a progress display existed,
    which meant it was skipped in exactly the interactive case.
    """
    gi = FakeGalaxyInstance({"job1": ["running", "ok"]})
    display = UploadProgressDisplay("hist123", console=_console())

    psi = _staging_interface(gi, simultaneous_uploads=False, display=display)
    psi._handle_job({"id": "job1"})

    assert display.upload_progress.terminal, "sequential upload returned before its job was terminal"


def test_simultaneous_uploads_do_not_wait():
    gi = FakeGalaxyInstance({"job1": ["running", "ok"]})
    display = UploadProgressDisplay("hist123", console=_console())

    psi = _staging_interface(gi, simultaneous_uploads=True, display=display)
    psi._handle_job({"id": "job1"})

    assert not display.upload_progress.terminal, "simultaneous upload waited on its job"


def test_wait_for_uploads_reports_errors_through_the_display():
    gi = FakeGalaxyInstance({"job1": ["error"]})
    display = UploadProgressDisplay("hist123", console=_console())

    psi = _staging_interface(gi, simultaneous_uploads=True, display=display)
    psi._upload_jobs.append({"id": "job1"})

    try:
        psi.wait_for_uploads(check_ok=True)
    except Exception:
        pass

    assert "job1" in display.upload_progress.printed_job_errors


class FakeRunnable:
    type = RunnableType.galaxy_tool


class FakeConfig:
    version_major = "24.1"
    use_path_paste = False

    def __init__(self, gi):
        self.user_gi = gi


def test_stage_in_builds_a_progress_display_without_a_tty(monkeypatch):
    """The display is no longer gated on ``sys.stdout.isatty()``."""
    captured: Dict[str, Any] = {}

    def fake_stage(self, tool_or_workflow, **kwds):
        captured["display"] = self._upload_progress_display
        return {}, []

    monkeypatch.setattr(sys, "stdout", StringIO())
    monkeypatch.setattr(activity, "_history_id", lambda gi, **kwds: "hist123")
    monkeypatch.setattr(PlanemoStagingInterface, "stage", fake_stage)
    monkeypatch.setattr(PlanemoStagingInterface, "wait_for_uploads", lambda self, check_ok=True: None)

    gi = FakeGalaxyInstance({})
    job_dict, history_id = activity.stage_in(None, FakeRunnable(), FakeConfig(gi), "job.json")

    assert history_id == "hist123"
    assert isinstance(captured["display"], UploadProgressDisplay)
