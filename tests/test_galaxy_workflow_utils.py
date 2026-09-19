"""Test utilities for dealing with Galaxy workflows."""

import os

import pytest
from ephemeris import shed_tools

from planemo.galaxy.workflows import (
    _install_shed_repos_from_tools_info,
    describe_outputs,
    FAILED_REPOSITORIES_MESSAGE,
    InstalledShedRepos,
    output_stubs_for_workflow,
    required_input_labels,
)
from planemo.runnable import for_path
from .test_utils import TEST_DATA_DIR


def test_describe_outputs():
    wf_path = os.path.join(TEST_DATA_DIR, "wf1.gxwf.yml")
    runnable = for_path(wf_path)
    outputs = describe_outputs(runnable)
    assert len(outputs) == 1
    output = outputs[0]
    assert output.order_index == 1
    assert output.output_name == "out_file1"
    assert output.label == "wf_output_1"


def test_describe_outputs_dict_tool_state():
    """A .ga with dict (not JSON-string) tool_state must not crash describe_outputs."""
    wf_path = os.path.join(TEST_DATA_DIR, "wf14-unlinted-best-practices-dict-tool-state.ga")
    runnable = for_path(wf_path)
    outputs = describe_outputs(runnable)
    assert len(outputs) == 1
    assert outputs[0].output_name == "outfile"


def test_required_input_steps_excludes_falsy_defaults():
    """Inputs with a default are not required, even when the default is falsy (boolean false, int 0)."""
    wf_path = os.path.join(TEST_DATA_DIR, "wf_required_defaults.gxwf.yml")
    required = set(required_input_labels(wf_path))
    assert "needs_value" in required
    assert "bool_default_false" not in required
    assert "int_default_zero" not in required


def test_output_stubs_skip_anonymous_and_empty_labels():
    """Empty/anonymous output labels are filtered via gxformat2's canonical predicate."""
    wf_path = os.path.join(TEST_DATA_DIR, "wf_empty_output_label.gxwf.yml")
    stubs = output_stubs_for_workflow(wf_path)
    assert stubs == {}


def _install_results(installed=None, errored=None):
    return shed_tools.InstallResults(
        installed_repositories=installed or [],
        skipped_repositories=[],
        errored_repositories=errored or [],
    )


def _patched_manager(monkeypatch, results):
    class FakeManager:
        def __init__(self, admin_gi):
            pass

        def install_repositories(self, tools_info, **kwds):
            return results

    monkeypatch.setattr(shed_tools, "InstallRepositoryManager", FakeManager)


def test_install_shed_repos_without_tools_returns_empty_lists():
    """Nothing to install yields empty lists, not None."""
    repos = _install_shed_repos_from_tools_info([], None, False)
    assert repos == InstalledShedRepos([], [])
    assert repos.installed_repositories == []
    assert repos.updated_repositories == []


def test_install_shed_repos_returns_named_fields(monkeypatch):
    installed = [{"name": "fastqc", "owner": "devteam"}]
    _patched_manager(monkeypatch, _install_results(installed=installed))
    repos = _install_shed_repos_from_tools_info([{"name": "fastqc"}], None, False)
    assert repos.installed_repositories == installed
    assert repos.updated_repositories == []


def test_install_shed_repos_error_names_failed_repositories(monkeypatch):
    """The exception says which repositories failed, not just that some did."""
    errored = [{"name": "broken_tool", "owner": "iuc"}]
    _patched_manager(monkeypatch, _install_results(errored=errored))
    with pytest.raises(Exception) as exc_info:
        _install_shed_repos_from_tools_info([{"name": "broken_tool"}], None, False)
    message = str(exc_info.value)
    assert FAILED_REPOSITORIES_MESSAGE in message
    assert "broken_tool" in message
    assert "iuc" in message


def test_install_shed_repos_warns_when_problems_ignored(monkeypatch, capsys):
    errored = [{"name": "broken_tool", "owner": "iuc"}]
    _patched_manager(monkeypatch, _install_results(installed=[{"name": "ok"}], errored=errored))
    repos = _install_shed_repos_from_tools_info([{"name": "broken_tool"}], None, True)
    assert repos.installed_repositories == [{"name": "ok"}]
    assert "broken_tool" in capsys.readouterr().err  # warn() writes to stderr
