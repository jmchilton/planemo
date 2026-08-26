"""Opt-in integration coverage for package-installed embedded Galaxy.

Run with ``PLANEMO_TEST_EMBEDDED_GALAXY=1`` in an environment containing a
Galaxy build with galaxyproject/galaxy#23360.
"""

import contextlib
import json
import multiprocessing
import os
import shutil
import threading
from dataclasses import replace
from unittest.mock import patch

from .test_utils import (
    CliTestCase,
    PROJECT_TEMPLATES_DIR,
    skip_unless_environ,
    TEST_DATA_DIR,
    TEST_TOOLS_DIR,
)


class EmbeddedGalaxyIntegrationTestCase(CliTestCase):
    @skip_unless_environ("PLANEMO_TEST_EMBEDDED_GALAXY")
    def test_tools_upload_and_workflow_share_one_embedded_application(self):
        xml_tool_path = os.path.join(PROJECT_TEMPLATES_DIR, "demo", "cat.xml")
        yaml_tool_path = os.path.join(TEST_TOOLS_DIR, "embedded_echo.yml")
        workflow_path = os.path.join(TEST_DATA_DIR, "wf2.ga")
        shed_workflow_source = os.path.join(
            TEST_DATA_DIR,
            "wf_repos",
            "basic_wf_iwc_invalid_version",
            "Super-simple-workflow.ga",
        )

        from planemo.galaxy import embedded

        load_runtime_dependencies = embedded._load_runtime_dependencies
        baseline_threads = set(threading.enumerate())
        baseline_child_pids = {process.pid for process in multiprocessing.active_children()}
        construction_count = 0
        celery_state_reads = []
        celery_results = []
        config_directories = []

        def load_counted_runtime_dependencies():
            dependencies = load_runtime_dependencies()
            build_galaxy_web_app = dependencies.build_galaxy_web_app
            start_worker = dependencies.start_worker

            @dependencies.celery_app.task(name="planemo.embedded_result_backend_probe")
            def result_backend_probe():
                return "probe complete"

            def counted_build(*args, **kwds):
                nonlocal construction_count
                construction_count += 1
                config_directories.append(os.path.dirname(kwds["global_conf"]["__file__"]))
                return build_galaxy_web_app(*args, **kwds)

            @contextlib.contextmanager
            def start_worker_with_result_backend_probe(celery_app, **kwds):
                from celery.result import allow_join_result

                with start_worker(celery_app, **kwds) as worker:
                    result = result_backend_probe.delay()
                    celery_state_reads.extend((result.state, result.state))
                    with allow_join_result():
                        celery_results.append(result.get(timeout=30))
                    celery_state_reads.extend((result.state, result.state))
                    yield worker

            return replace(
                dependencies,
                build_galaxy_web_app=counted_build,
                start_worker=start_worker_with_result_backend_probe,
            )

        with self._isolate() as test_directory:
            shed_workflow_path = os.path.join(test_directory, "embedded-shed-workflow.ga")
            shutil.copyfile(shed_workflow_source, shed_workflow_path)
            shed_tests_path = shed_workflow_path.replace(".ga", "-tests.yml")
            with open(shed_tests_path, "w") as shed_tests:
                shed_tests.write("""- doc: Exercise an installed Tool Shed workflow
  job:
    n_rows: 5
  outputs:
    outfile:
      asserts:
        has_n_lines:
          n: 5
""")
            report_path = os.path.join(test_directory, "embedded-report.json")
            with patch.object(embedded, "_load_runtime_dependencies", load_counted_runtime_dependencies):
                result = self._check_exit_code(
                    [
                        "test",
                        "--engine",
                        "embedded_galaxy",
                        "--no_dependency_resolution",
                        "--test_output_json",
                        report_path,
                        xml_tool_path,
                        yaml_tool_path,
                        workflow_path,
                        shed_workflow_path,
                    ]
                )

            with open(report_path) as report_fh:
                report = json.load(report_fh)

        # The Click result is the command's authoritative exit status. Galaxy's
        # raw structured report may leave its optional ``exit_code`` field null;
        # Planemo derives the command result from the report summary.
        assert result.exit_code == 0
        assert report["summary"] == {
            "num_errors": 0,
            "num_failures": 0,
            "num_skips": 0,
            "num_tests": 4,
        }
        assert construction_count == 1
        assert celery_results == ["probe complete"]
        assert len(celery_state_reads) == 4
        assert celery_state_reads[-2:] == ["SUCCESS", "SUCCESS"]
        assert all(test["data"]["status"] == "success" for test in report["tests"])
        tool_jobs = [test["data"]["job"] for test in report["tests"] if test["data"].get("job")]
        assert {job["tool_id"] for job in tool_jobs} == {"cat", "embedded_echo"}
        assert all(job["state"] == "ok" for job in tool_jobs)
        # Pydantic's report model serializes optional fields as null, so select
        # by the authoritative runnable type rather than key presence.
        workflow_results = [test for test in report["tests"] if test["test_type"] == "galaxy_workflow"]
        assert len(workflow_results) == 2
        assert all(result["data"]["invocation_details"] for result in workflow_results)
        assert {result["data"]["invocation_details"]["details"]["invocation_state"] for result in workflow_results} <= {
            "scheduled",
            "completed",
        }

        from galaxy import app as galaxy_app_module

        assert galaxy_app_module.app is None
        remaining_threads = sorted(
            thread.name for thread in threading.enumerate() if thread not in baseline_threads and thread.is_alive()
        )
        remaining_child_processes = sorted(
            f"{process.name} (pid={process.pid})"
            for process in multiprocessing.active_children()
            if process.pid not in baseline_child_pids and process.is_alive()
        )
        assert remaining_threads == []
        assert remaining_child_processes == []
        assert len(config_directories) == 1
        assert not os.path.exists(config_directories[0])
