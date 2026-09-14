"""Tests for the base engine's handling of inline test jobs."""

import json
import os
from types import SimpleNamespace

import pytest

from .test_utils import create_test_context


def _inline_test_case(tests_directory, job):
    return SimpleNamespace(
        runnable=object(),
        job_path=None,
        job=job,
        tests_directory=str(tests_directory),
        structured_test_data=lambda _: {},
    )


def _recording_engine(run_callback):
    # Importing the engine at module scope introduces a collection-order
    # dependency through planemo.runnable.
    import planemo.engine.interface as engine_interface

    class RecordingEngine(engine_interface.BaseEngine):
        def _run(self, runnables, job_paths, output_collectors=None, test_timeout=None):
            return run_callback(job_paths)

    return RecordingEngine(create_test_context())


def test_inline_job_uses_temporary_directory_and_preserves_input_paths(tmp_path):
    tests_directory = tmp_path / "workflow-tests"
    tests_directory.mkdir()
    job = {
        "input": {
            "class": "File",
            "path": "data/input.txt",
            "secondaryFiles": [{"class": "File", "location": "data/input.txt.idx"}],
        },
        "directory": {"class": "Directory", "location": "data/directory"},
        "collection": {
            "class": "Collection",
            "elements": [{"class": "File", "path": "data/element.txt"}],
        },
        "composite": {
            "class": "File",
            "composite_data": [{"path": "data/header.txt"}, "data/binary.dat"],
        },
        "remote": {"class": "File", "location": "https://example.org/input.txt"},
        "parameter": {"path": "this-is-not-a-file-input"},
    }
    original_job = json.loads(json.dumps(job))
    observed = {}

    def record_job(job_paths):
        job_path = job_paths[0]
        observed["job_path"] = job_path
        observed["job_directory"] = os.path.dirname(job_path)
        with open(job_path) as f:
            observed["job"] = json.load(f)
        return [object()]

    engine = _recording_engine(record_job)
    engine._run_test_cases([_inline_test_case(tests_directory, job)], test_timeout=None)

    materialized_job = observed["job"]
    assert observed["job_directory"] != str(tests_directory)
    assert not os.path.exists(observed["job_directory"])
    assert materialized_job["input"]["path"] == str(tests_directory / "data/input.txt")
    assert materialized_job["input"]["secondaryFiles"][0]["location"] == str(tests_directory / "data/input.txt.idx")
    assert materialized_job["directory"]["location"] == str(tests_directory / "data/directory")
    assert materialized_job["collection"]["elements"][0]["path"] == str(tests_directory / "data/element.txt")
    assert materialized_job["composite"]["composite_data"] == [
        {"path": str(tests_directory / "data/header.txt")},
        str(tests_directory / "data/binary.dat"),
    ]
    assert materialized_job["remote"]["location"] == "https://example.org/input.txt"
    assert materialized_job["parameter"]["path"] == "this-is-not-a-file-input"
    assert job == original_job


def test_inline_job_temporary_directory_is_cleaned_up_on_engine_failure(tmp_path):
    observed = {}

    def fail(job_paths):
        observed["job_directory"] = os.path.dirname(job_paths[0])
        raise RuntimeError("engine failed")

    engine = _recording_engine(fail)
    test_case = _inline_test_case(tmp_path, {"input": {"class": "File", "path": "input.txt"}})

    with pytest.raises(RuntimeError, match="engine failed"):
        engine._run_test_cases([test_case], test_timeout=None)

    assert not os.path.exists(observed["job_directory"])
